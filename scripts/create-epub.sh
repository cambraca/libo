#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'Usage: %s <book-directory>\n' "$0" >&2
  exit 1
fi

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
books_dir="$repo_root/books"
book_dir="$books_dir/$1"

if [[ ! -d "$book_dir" ]]; then
  printf 'Error: book directory does not exist: %s\n' "$book_dir" >&2
  exit 1
fi

book_dir=$(cd "$book_dir" && pwd)

if [[ "$(dirname "$book_dir")" != "$books_dir" ]]; then
  printf 'Error: book name must identify a direct subdirectory of: %s\n' "$books_dir" >&2
  exit 1
fi

target_dir="$book_dir/target"
output_file="$book_dir/target.epub"

if [[ ! -d "$target_dir" ]]; then
  printf 'Error: required target directory does not exist: %s\n' "$target_dir" >&2
  exit 1
fi

if [[ ! -f "$target_dir/mimetype" ]]; then
  printf 'Error: required EPUB mimetype file does not exist: %s/mimetype\n' "$target_dir" >&2
  exit 1
fi

rm -f "$output_file"

(
  cd "$target_dir"
  zip -X0 "$output_file" mimetype
  zip -Xr9D "$output_file" . -x mimetype
)

printf 'Created EPUB: %s\n' "$output_file"
