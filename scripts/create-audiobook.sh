#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'Usage: docker compose run --rm epub2tts <book-directory>\n' >&2
  exit 1
fi

book_dir="/books/$1"
epub_file="$book_dir/audiobook.epub"
work_dir="$book_dir/.audiobook-work"
text_file="$work_dir/audiobook.txt"
voice_output="$work_dir/audiobook-${TTS_SPEAKER}.m4b"
output_file="$book_dir/audiobook.m4b"

if [[ ! -d "$book_dir" ]]; then
  printf 'Error: book directory does not exist: %s\n' "$book_dir" >&2
  exit 1
fi

if [[ ! -f "$epub_file" ]]; then
  printf 'Error: audiobook EPUB does not exist: %s\n' "$epub_file" >&2
  printf 'Create it first with: ./scripts/create-epub.sh "%s" audiobook\n' "$1" >&2
  exit 1
fi

mkdir -p "$work_dir"
cd "$book_dir"

printf 'Scanning %s\n' "$epub_file"
epub2tts "$epub_file" --engine edge --speaker "$TTS_SPEAKER" --scan

printf 'Exporting %s\n' "$text_file"
rm -f "$text_file"
cd "$work_dir"
epub2tts "$epub_file" --engine edge --speaker "$TTS_SPEAKER" --export txt

printf 'Generating %s with %s\n' "$output_file" "$TTS_SPEAKER"
rm -f "$output_file"
epub2tts "$text_file" \
  --engine edge \
  --speaker "$TTS_SPEAKER" \
  --threads "$TTS_THREADS" \
  --minratio 0

if [[ ! -f "$voice_output" ]]; then
  printf 'Error: expected audiobook output was not created: %s\n' "$voice_output" >&2
  exit 1
fi

mv "$voice_output" "$output_file"
printf 'Created audiobook: %s\n' "$output_file"
