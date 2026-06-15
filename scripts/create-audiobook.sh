#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'Usage: docker compose run --rm epub2tts <book-directory>\n' >&2
  exit 1
fi

book_dir="/books/$1"
text_file="$book_dir/audiobook.txt"
work_dir="$book_dir/.audiobook-work"
voice_output="$work_dir/audiobook-${TTS_SPEAKER}.m4b"
output_file="$book_dir/audiobook.m4b"
cover_file=""

if [[ ! -d "$book_dir" ]]; then
  printf 'Error: book directory does not exist: %s\n' "$book_dir" >&2
  exit 1
fi

if [[ ! -f "$text_file" ]]; then
  printf 'Error: audiobook text does not exist: %s\n' "$text_file" >&2
  printf 'Create it first by running the audiobook prompt.\n' >&2
  exit 1
fi

for candidate in "$book_dir/cover.png" "$book_dir/cover.jpg" "$book_dir/cover.jpeg"; do
  if [[ -f "$candidate" ]]; then
    cover_file="$candidate"
    break
  fi
done

mkdir -p "$work_dir"
cd "$work_dir"

printf 'Generating %s with %s\n' "$output_file" "$TTS_SPEAKER"
rm -f "$output_file"
tts_args=(
  "$text_file"
  --speaker "$TTS_SPEAKER"
  --threads "$TTS_THREADS"
)

if [[ -n "$cover_file" ]]; then
  printf 'Using cover image: %s\n' "$cover_file"
  tts_args+=(--cover "$cover_file")
fi

epub2tts "${tts_args[@]}"

if [[ ! -f "$voice_output" ]]; then
  printf 'Error: expected audiobook output was not created: %s\n' "$voice_output" >&2
  exit 1
fi

mv "$voice_output" "$output_file"
printf 'Created audiobook: %s\n' "$output_file"
