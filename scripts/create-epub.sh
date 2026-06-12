#!/usr/bin/env bash

set -euo pipefail

target_dir=${1:-target}
output_file=${2:-book.epub}

if [[ ! -d "$target_dir" ]]; then
  printf 'Error: target directory does not exist: %s\n' "$target_dir" >&2
  exit 1
fi

if [[ ! -f "$target_dir/mimetype" ]]; then
  printf 'Error: required EPUB mimetype file does not exist: %s/mimetype\n' "$target_dir" >&2
  exit 1
fi

target_dir=$(cd "$target_dir" && pwd)

if [[ "$output_file" != /* ]]; then
  output_file="$PWD/$output_file"
fi

rm -f "$output_file"

(
  cd "$target_dir"
  zip -X0 "$output_file" mimetype
  zip -Xr9D "$output_file" . -x mimetype
)

printf 'Created EPUB: %s\n' "$output_file"
