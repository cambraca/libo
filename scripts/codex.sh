#!/usr/bin/env bash

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
sandbox_name=codex-libo

cd "$repo_root"

if ! sbx ls -q | grep -Fxq "$sandbox_name"; then
  sbx create --name "$sandbox_name" --kit . codex .
fi

exec sbx run --name "$sandbox_name" -- "$@"
