#!/usr/bin/env bash
# Build a Computer-ready zip: SKILL.md must sit at the zip root.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/bo2bot-messaging"
OUT="${1:-$ROOT/bo2bot-messaging.zip}"
mkdir -p "$(dirname "$OUT")"

if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "FAIL: $SRC/SKILL.md not found" >&2
  exit 1
fi

rm -f "$OUT"
(
  cd "$SRC"
  zip -r "$OUT" SKILL.md config.json scripts references \
    -x "*.pyc" -x "*__pycache__*" -x "*.DS_Store" -x "*/.*"
)

echo "Wrote $OUT"
echo "Upload it in Computer → Skills → Create skill → Upload a skill"
