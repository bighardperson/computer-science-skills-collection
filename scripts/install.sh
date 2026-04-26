#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-$HOME/.agents/skills}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/skills"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Cannot find skills directory: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET"

echo "Installing skills to: $TARGET"
rsync -a --delete \
  --exclude '.git/' \
  --exclude 'node_modules/' \
  --exclude '__pycache__/' \
  --exclude '.DS_Store' \
  "$SOURCE_DIR/" "$TARGET/"

COUNT="$(find "$TARGET" -iname 'SKILL.md' | wc -l | tr -d ' ')"
echo "Done. Installed skill entry files: $COUNT"

