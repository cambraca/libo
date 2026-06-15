"""
Adapted from aedocw/epub2tts:
https://github.com/aedocw/epub2tts

Downloaded on June 13, 2026, and adapted for this project to support only
Microsoft Edge TTS.
"""

import argparse
import asyncio
import os
import multiprocessing as mp
import re
import random
import subprocess
import sys
import time

import edge_tts
from mutagen import mp4
from nltk.tokenize import sent_tokenize
from pydub import AudioSegment
from pydub.silence import split_on_silence
import nltk

class Text2WaveFile:
    def __init__(self, config = {}):
        self.config = config

    def proccess_text(self, text, wave_file_name):
        raise NotImplementedError

    def proccess_text_retry(self, text, wave_file_name):
        attempts = 8
        last_error = None
        for attempt in range(1, attempts + 1):
            remove_file(wave_file_name)
            try:
                self.proccess_text(text, wave_file_name)
                if is_valid_audio_file(wave_file_name):
                    return
                last_error = RuntimeError("TTS returned an empty or invalid audio file")
            except Exception as exc:
                last_error = exc
            remove_file(wave_file_name)
            if attempt < attempts:
                delay = min(30, 2 ** (attempt - 1)) + random.uniform(0, 1)
                print(
                    f"TTS attempt {attempt}/{attempts} failed for "
                    f"{wave_file_name}: {last_error}. Retrying in {delay:.1f}s"
                )
                time.sleep(delay)
        raise RuntimeError(
            f"Could not create valid audio file {wave_file_name} after "
            f"{attempts} attempts: {last_error}"
        )

class EdgeTTS(Text2WaveFile):
    def __init__(self, config = {}):
        if 'speaker' not in config:
            raise Exception('no speeker configured')
        self.config = config

    def proccess_text(self, text, wave_file_name):
        asyncio.run(self.edgespeak(text, wave_file_name))

    async def edgespeak(self, text, wave_file_name):
        communicate = edge_tts.Communicate(text, self.config['speaker'])
        await communicate.save(wave_file_name)

def remove_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass

def is_valid_audio_file(file_path):
    if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
        return False
    try:
        return len(AudioSegment.from_file(file_path)) > 0
    except Exception:
        return False

def get_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_milliseconds = len(audio)
    return duration_milliseconds

def join_temp_files_to_chapter(tempfiles, outputwav):
    tempwavfiles = [AudioSegment.from_file(f"{f}") for f in tempfiles]
    concatenated = sum(tempwavfiles)
    # remove silence, then export to wav
    #print(f"Replacing silences longer than one second with one second of silence ({outputwav})")
    one_sec_silence = AudioSegment.silent(duration=1000)
    two_sec_silence = AudioSegment.silent(duration=2000)
    # This AudioSegment is dedicated for each file.
    audio_modified = AudioSegment.empty()
    # Split audio into chunks where detected silence is longer than one second
    chunks = split_on_silence(
        concatenated, min_silence_len=1000, silence_thresh=-50
    )
    msec_added = 0
    # Iterate through each chunk
    for chunkindex, chunk in enumerate(chunks):
        audio_modified += chunk
        audio_modified += one_sec_silence
        msec_added += 1000

    # add extra 2sec silence at the end of each part/chapter
    msec_added += 2000
    audio_modified += two_sec_silence
    # Write modified audio to the final audio segment
    audio_modified.export(outputwav, format="wav")
    for f in tempfiles:
        os.remove(f)
    return msec_added

def process_book_chapter(dat):
    print("initiating chapter: ", dat['chapter'])
    tts_engine = dat['config']['engine_cl'](dat['config'])
    for text, file_name in dat['synthesis_jobs']:
        try:
            tts_engine.proccess_text_retry(text, file_name)
        except Exception as exc:
            # Ensure exceptions are safe to pass through multiprocessing.
            msg = f"Chapter '{dat['chapter']}' failed: {exc.__class__.__name__}: {exc}"
            raise RuntimeError(msg) from None

    join_temp_files_to_chapter(dat['tempfiles'], dat['outputwav'])

    print("done chapter: ", dat['chapter'])
    return dat['outputwav']



class TextToAudiobook:
    def __init__(
        self,
        source,
        start,
        threads,
        end,
        debug,
        sayparts,
        skip_cleanup,
    ):
        self.source = source
        self.bookname = os.path.splitext(os.path.basename(source))[0]
        self.start = start - 1
        self.threads = threads
        self.end = end
        self.sayparts = sayparts
        self.debug = debug
        self.output_filename = self.bookname + ".m4b"
        self.chapters_to_read = []
        self.section_names = []
        self.section_speakers = []
        self.skip_cleanup = skip_cleanup
        self.title = self.bookname
        self.author = "Unknown"
        self.audioformat = ["m4b"]
        if not source.endswith(".txt"):
            print("Can only handle a txt source.")
            sys.exit(1)
        self.ffmetadatafile = "FFMETADATAFILE"
        # Make sure we've got nltk punkt
        self.ensure_punkt()

    def ensure_punkt(self):
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")
        try:
            nltk.data.find("tokenizers/punkt_tab")
        except LookupError:
            nltk.download("punkt_tab")


    def generate_metadata(self, files):
        chap = 1
        start_time = 0
        with open(self.ffmetadatafile, "w", encoding='utf8') as file:
            file.write(";FFMETADATA1\n")
            file.write(f"ARTIST={self.author}\n")
            file.write(f"ALBUM={self.title}\n")
            file.write("DESCRIPTION=Made with https://github.com/aedocw/epub2tts\n")
            for file_name in files:
                duration = get_duration(file_name)
                file.write("[CHAPTER]\n")
                file.write("TIMEBASE=1/1000\n")
                file.write(f"START={start_time}\n")
                file.write(f"END={start_time + duration}\n")
                file.write(f"title={self.section_names[self.start+chap-1]}\n")
                chap += 1
                start_time += duration


    def get_length(self, start, end, chapters_to_read):
        total_chars = 0
        for i in range(start, end):
            total_chars += len(chapters_to_read[i])
        return total_chars

    def prep_text(self, text_in):
        # Replace some chars with comma to improve TTS by introducing a pause
        text = (
            text_in.replace("--", ", ")
            .replace("—", ", ")
            .replace(";", ", ")
            .replace(":", ", ")
            .replace("''", ", ")
            .replace("’", "'")
            .replace('“', '"')
            .replace('”', '"')
            .replace("◇", "")
            .replace(" . . . ", ", ")
            .replace("... ", ", ")
            .replace("«", " ")
            .replace("»", " ")
            .replace("[", "")
            .replace("]", "")
            .replace("&", " and ")
            .replace(" GNU ", " new ")
            .replace("\n", " \n")
            .replace("*", " ")
            .strip()
        )
        return text

    def get_chapters_text(self, speaker):
        with open(self.source, "r") as file:
            text = file.read()
        metadata, text = self.extract_title_author(text)
        if metadata.get("Title") != None:
            self.title = metadata.get("Title")
        if metadata.get("Author") != None:
            self.author = metadata.get("Author")
        if self.skip_cleanup:
            pass
        else:
            text = self.prep_text(text)
        lines_with_hashtag = [line for line in text.splitlines() if line.startswith("# ")]
        if not lines_with_hashtag:
            print("Error: audiobook.txt must contain named '# ' chapter headings.")
            sys.exit(1)
        for line in lines_with_hashtag:
            chapter_name = line.lstrip("# ").strip()
            if not chapter_name:
                print("Error: audiobook.txt contains an empty chapter heading.")
                sys.exit(1)
            self.section_speakers.append(speaker)
            self.section_names.append(chapter_name)
            print(f"Section speakers: {self.section_speakers}") if self.debug else None
            print(f"Section names: {self.section_names}") if self.debug else None
        sections = re.split(r"\n(?=#\s)", text)
        sections = [section.strip() for section in sections if section.strip()]
        for i, section in enumerate(sections):
            lines = section.splitlines()
            section = "\n".join(lines[1:])
            self.chapters_to_read.append(section.strip())
            print(f"Part: {len(self.chapters_to_read)}")
            print(f"{self.section_names[i]}")
            print(f"Speaker: {self.section_speakers[i]}")
            print(str(self.chapters_to_read[-1])[:256])
        if self.end == 999:
            self.end = len(self.chapters_to_read)
        print(f"Section names: {self.section_names}") if self.debug else None


    def combine_sentences(self, sentences, length=1000):
        for sentence in sentences:
            yield sentence

    def check_for_file(self, filename):
        if os.path.isfile(filename):
            print(f"The file '{filename}' already exists.")
            overwrite = input("Do you want to overwrite the file? (y/n): ")
            if overwrite.lower() != 'y':
                print("Exiting without overwriting the file.")
                sys.exit()
            else:
                os.remove(filename)

    def add_cover(self, cover_img):
        if os.path.isfile(cover_img):
            m4b = mp4.MP4(self.output_filename)
            cover_image = open(cover_img, "rb").read()
            m4b["covr"] = [mp4.MP4Cover(cover_image)]
            m4b.save()
        else:
            print(f"Cover image {cover_img} not found")

    def extract_title_author(self, text):
        lines = text.split('\n')
        metadata = {}

        # A copy of the list for iteration
        lines_copy = lines[:]

        for line in lines_copy[:2]:  # We check only the first two lines
            if line.startswith('Title: '):
                metadata['Title'] = line.replace('Title: ', '').strip()
                lines.remove(line)  # Remove line from the original list
            elif line.startswith('Author: '):
                metadata['Author'] = line.replace('Author: ', '').strip()
                lines.remove(line)  # Remove line from the original list

        # Check for the next non-whitespace line
        for line in lines:
            if line.strip():  # Find the first non-empty line
                if not line.startswith('#'):
                    print("Error: The first non-whitespace line must start with '#'")
                    sys.exit(1)  # Exit the script if the condition is not met
                break  # Exit the loop once the condition is met

        text = '\n'.join(lines)   # Join the lines back
        return metadata, text
    def read_book(self, speaker, bitrate):
        voice_name = "-" + speaker
        self.output_filename = re.sub(".m4b", voice_name + ".m4b", self.output_filename)
        print(f"Saving to {self.output_filename}")
        self.check_for_file(self.output_filename)
        total_chars = self.get_length(self.start, self.end, self.chapters_to_read)
        print(f"Total characters: {total_chars}")
        files = []
        position = 0
        start_time = time.time()
        print(f"Reading from {self.start + 1} to {self.end}")
        chapter_job_que = []
        for partnum, i in enumerate(range(self.start, self.end)):
            synthesis_jobs = []
            outputwav = f"{self.bookname}-{i + 1}.wav"
            files.append(outputwav)
            if is_valid_audio_file(outputwav):
                print(f"{outputwav} exists, skipping to next chapter")
            else:
                if os.path.exists(outputwav):
                    print(f"{outputwav} is incomplete or invalid; regenerating chapter")
                    remove_file(outputwav)
                tempfiles = []
                chapter_name = "Part " + str(partnum + 1)
                if len(self.section_names) > 0:
                    chapter_name = self.section_names[i].strip()

                if self.sayparts and len(self.section_names) == 0:
                    chapter = chapter_name + ". " + self.chapters_to_read[i]
                elif self.sayparts and len(self.section_names) > 0:
                    chapter = chapter_name + ".\n" + self.chapters_to_read[i]
                else:
                    chapter = self.chapters_to_read[i]

                if self.section_speakers[i] != None:
                    speaker = self.section_speakers[i]

                config = {
                    'speaker': speaker,
                    'debug': self.debug,
                    'engine_cl': EdgeTTS,
                }


                sentences = sent_tokenize(chapter)
                #Drop any items that do NOT have at least one letter or number
                sentences = [s for s in sentences if any(c.isalnum() for c in s)]
                sentence_groups = list(self.combine_sentences(sentences, 1000))


                #tts_engine = config['engine_cl'](config)

                for x in range(len(sentence_groups)):
                    #skip if item is empty
                    if len(sentence_groups[x]) == 0:
                        continue
                    #skip if item has no characters or numbers
                    if not any(char.isalnum() for char in sentence_groups[x]):
                        continue
                    tempwav = "temp"+ str(partnum)+ "_" + str(x) + ".wav"

                    if is_valid_audio_file(tempwav):
                        print(tempwav + " exists, skipping to next chunk")
                    else:
                        if os.path.exists(tempwav):
                            print(tempwav + " is empty or invalid; regenerating chunk")
                            remove_file(tempwav)
                        synthesis_jobs.append((sentence_groups[x], tempwav))
                    tempfiles.append(tempwav)
                chapter_job_que.append({
                    'config': config,
                    'tempfiles': tempfiles,
                    'synthesis_jobs': synthesis_jobs,
                    'outputwav': outputwav,
                    'chapter': chapter_name,
                })

        print("initiating work:")

        if self.threads <= 1:
            map_result = list(map(process_book_chapter, chapter_job_que))
        else:
            pool = mp.Pool(processes=self.threads)
            pool.map(process_book_chapter, chapter_job_que)
        files2 =[]
        for filename in files:
            if is_valid_audio_file(filename):
                files2.append(filename)
        files = files2
        outputm4a = self.output_filename.replace("m4b", "m4a")
        filelist = "filelist.txt"
        with open(filelist, "w") as f:
            for filename in files:
                filename = filename.replace("'", "'\\''")
                f.write(f"file '{filename}'\n")

        for i in self.audioformat:
            if i == "wav":
                outputm4a = outputm4a.replace(".m4a", "_without_metadata.wav")
                self.output_filename = self.output_filename.replace(".m4b", ".wav")
                ffmpeg_command = [
                    "ffmpeg",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    filelist,
                    outputm4a,
                ]
            elif i == "flac":
                outputm4a = outputm4a.replace(".m4a", "_without_metadata.flac")
                self.output_filename = self.output_filename.replace(".m4b", ".flac")
                ffmpeg_command = [
                    "ffmpeg",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    filelist,
                    outputm4a,
                ]
            elif i == "m4b":
                ffmpeg_command = [
                    "ffmpeg",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    filelist,
                    "-codec:a",
                    "aac",
                    "-b:a",
                    bitrate,
                    "-f",
                    "ipod",
                    outputm4a,
                ]
            subprocess.run(ffmpeg_command)
            self.generate_metadata(files)
            ffmpeg_command = [
                "ffmpeg",
                "-i",
                outputm4a,
                "-i",
                self.ffmetadatafile,
                "-map_metadata",
                "1",
                "-codec",
                "copy",
                self.output_filename,
            ]
            subprocess.run(ffmpeg_command)
            if not self.debug: # Leave the files if debugging
                os.remove(outputm4a)
        if not self.debug: # Leave the files if debugging
            os.remove(filelist)
            os.remove(self.ffmetadatafile)
            for f in files:
                os.remove(f)
        print(self.output_filename + " complete")


def main():
    parser = argparse.ArgumentParser(
        prog="TextToAudiobook",
        description="Convert an audiobook text file to an Edge TTS M4B",
    )
    parser.add_argument("sourcefile", type=str, help="The audiobook.txt file to process")
    parser.add_argument(
        "--speaker",
        type=str,
        default="en-US-AndrewNeural",
        help="Microsoft Edge TTS voice",
    )
    parser.add_argument(
        "--start",
        type=int,
        nargs="?",
        const=1,
        default=1,
        help="Chapter/part to start from",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of chapters to synthesize concurrently",
    )
    parser.add_argument(
        "--end",
        type=int,
        nargs="?",
        const=999,
        default=999,
        help="Chapter/part to end with",
    )
    parser.add_argument(
        "--sayparts",
        action="store_true",
        help="Say each part number at start of section"
    )
    parser.add_argument(
        "--bitrate",
        type=str,
        nargs="?",
        const="69k",
        default="69k",
        help="Specify bitrate for output file",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
    )
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Skip text cleanup",
    )
    parser.add_argument(
        "--cover",
        type=str,
        help="jpg image to use for cover",
    )

    args = parser.parse_args()
    print(args)

    mybook = TextToAudiobook(
        source=args.sourcefile,
        start=args.start,
        threads=args.threads,
        end=args.end,
        debug=args.debug,
        sayparts=args.sayparts,
        skip_cleanup=args.skip_cleanup,
    )

    speaker = args.speaker
    print(f"Speaker: {speaker}")

    mybook.get_chapters_text(speaker=speaker)

    mybook.read_book(
        speaker=speaker,
        bitrate=args.bitrate,
    )
    if args.cover is not None:
        mybook.add_cover(args.cover)


if __name__ == "__main__":
    main()
