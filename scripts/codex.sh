#!/usr/bin/env bash

set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
sandbox_name=codex-libo

cd "$repo_root"

if ! sbx ls -q | grep -Fxq "$sandbox_name"; then
  sbx create --name "$sandbox_name" --kit . codex .
fi

if [[ "${CODEX_AUTO_UPDATE:-1}" != "0" ]]; then
  if ! sbx exec "$sandbox_name" -- codex update; then
    echo "warning: codex update failed; continuing with the installed version" >&2
  fi
fi

exec sbx run --name "$sandbox_name" -- --disable apps "$@"
