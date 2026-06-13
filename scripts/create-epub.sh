#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  printf 'Usage: %s <book-directory> [target|audiobook]\n' "$0" >&2
  exit 1
fi

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
books_dir="$repo_root/books"
book_dir="$books_dir/$1"
version="${2:-target}"

case "$version" in
  target|audiobook)
    ;;
  *)
    printf 'Error: version must be either "target" or "audiobook": %s\n' "$version" >&2
    exit 1
    ;;
esac

if [[ ! -d "$book_dir" ]]; then
  printf 'Error: book directory does not exist: %s\n' "$book_dir" >&2
  exit 1
fi

book_dir=$(cd "$book_dir" && pwd)

if [[ "$(dirname "$book_dir")" != "$books_dir" ]]; then
  printf 'Error: book name must identify a direct subdirectory of: %s\n' "$books_dir" >&2
  exit 1
fi

input_dir="$book_dir/$version"
output_file="$book_dir/$version.epub"

if [[ ! -d "$input_dir" ]]; then
  printf 'Error: required %s directory does not exist: %s\n' "$version" "$input_dir" >&2
  exit 1
fi

if [[ ! -f "$input_dir/mimetype" ]]; then
  printf 'Error: required EPUB mimetype file does not exist: %s/mimetype\n' "$input_dir" >&2
  exit 1
fi

rm -f "$output_file"

(
  cd "$input_dir"
  zip -X0 "$output_file" mimetype
  zip -Xr9D "$output_file" . -x mimetype
)

printf 'Created EPUB: %s\n' "$output_file"
