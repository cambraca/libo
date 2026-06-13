FROM python:3.11-slim

ARG EPUB2TTS_COMMIT=286d12975f43861218a5c3c8737b30430e34718e

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
      beautifulsoup4 \
      ebooklib \
      edge-tts \
      fuzzywuzzy \
      lxml \
      mutagen \
      nltk \
      pillow \
      pydub \
      python-Levenshtein \
    && python -m nltk.downloader -d /usr/local/share/nltk_data punkt punkt_tab

RUN curl -fsSL \
      "https://raw.githubusercontent.com/aedocw/epub2tts/${EPUB2TTS_COMMIT}/epub2tts.py" \
      -o /usr/local/lib/epub2tts.py \
    && sed -i \
      -e '/^import pkg_resources$/d' \
      -e '/^from kokoro import KPipeline$/d' \
      -e '/^import numpy as np$/d' \
      -e '/^from openai import OpenAI$/d' \
      -e '/^from pedalboard/d' \
      -e '/^from TTS/d' \
      -e '/^import noisereduce$/d' \
      -e '/^import torch, gc$/d' \
      -e '/^import torchaudio$/d' \
      -e '/^import whisper$/d' \
      -e '/^import soundfile as sf$/d' \
      -e 's|self.tts_dir = str(get_user_data_dir("tts"))|self.tts_dir = os.path.expanduser("~/.local/share/tts")|' \
      -e '/        if torch.cuda.is_available():/,/            self.device = "cpu"/c\        self.device = "cpu"' \
      /usr/local/lib/epub2tts.py \
    && printf '#!/bin/sh\nexec python /usr/local/lib/epub2tts.py "$@"\n' \
      > /usr/local/bin/epub2tts \
    && chmod +x /usr/local/bin/epub2tts

ENV NLTK_DATA=/usr/local/share/nltk_data

ENTRYPOINT ["epub2tts"]
CMD ["--help"]
