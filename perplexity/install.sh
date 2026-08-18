#!/usr/bin/env bash
# One-command Mac (and Linux) installer for the Perplexity Bo2bot skill.
#
#   bash perplexity/install.sh
#   bash perplexity/install.sh /path/to/bo2bot.env
#   bash perplexity/install.sh --no-open
#
# Places credentials, copies the skill to ~/.perplexity/skills/, builds the
# Computer-ready zip, copies the kickoff to the clipboard, reveals the zip
# in Finder, and launches Perplexity. Then paste into Computer (Cmd+V).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/bo2bot-messaging"
KICKOFF="$ROOT/kickoff.txt"
SECRETS_DIR="${HOME}/.perplexity/secrets"
SKILLS_DIR="${HOME}/.perplexity/skills"
CREDS_DST="${SECRETS_DIR}/bo2bot.env"
SKILL_DST="${SKILLS_DIR}/bo2bot-messaging"
ZIP_DST="${SKILLS_DIR}/bo2bot-messaging.zip"
REQUIRED=(BO2BOT_HANDLE BO2BOT_PUBLIC_ADDRESS BO2BOT_ACCOUNT_ID BO2BOT_AUTH_KEY)

NO_OPEN=0
ENV_SRC=""

usage() {
  cat <<EOF
Usage: bash perplexity/install.sh [bo2bot.env] [--no-open]

Finds bo2bot.env automatically (existing install, Downloads, Desktop,
or a path you pass). Then:
  ~/.perplexity/secrets/bo2bot.env
  ~/.perplexity/skills/bo2bot-messaging/
  ~/.perplexity/skills/bo2bot-messaging.zip
On Mac: copies kickoff.txt to the clipboard, reveals the zip, opens Perplexity.
EOF
}

for arg in "$@"; do
  case "$arg" in
    -h|--help) usage; exit 0 ;;
    --no-open) NO_OPEN=1 ;;
    -*) echo "FAIL: unknown flag $arg" >&2; usage >&2; exit 1 ;;
    *) ENV_SRC="$arg" ;;
  esac
done

if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "FAIL: $SRC/SKILL.md not found" >&2
  exit 1
fi

field_value() {
  local file="$1" key="$2" line
  line="$(grep -E "^${key}=" "$file" | tail -n 1 || true)"
  printf '%s' "${line#${key}=}"
}

env_complete() {
  local file="$1" key val
  [[ -f "$file" ]] || return 1
  for key in "${REQUIRED[@]}"; do
    val="$(field_value "$file" "$key")"
    [[ -n "$val" ]] || return 1
  done
  return 0
}

resolve_env() {
  local c
  if [[ -n "$ENV_SRC" ]]; then
    echo "$ENV_SRC"
    return 0
  fi
  for c in \
    "$CREDS_DST" \
    "${HOME}/Downloads/bo2bot.env" \
    "${HOME}/Desktop/bo2bot.env" \
    "${PWD}/bo2bot.env"
  do
    if env_complete "$c"; then
      echo "$c"
      return 0
    fi
  done
  return 1
}

echo "==> Bo2bot · Perplexity install"

FOUND=""
if ! FOUND="$(resolve_env)"; then
  echo "No complete bo2bot.env found (looked in ~/.perplexity/secrets, Downloads, Desktop)."
  if [[ -t 0 ]]; then
    read -r -p "Path to bo2bot.env (Enter to abort): " ENV_SRC
  fi
  FOUND="$(resolve_env || true)"
fi
if [[ -z "$FOUND" ]] || ! env_complete "$FOUND"; then
  echo "FAIL: need a complete bo2bot.env with ${REQUIRED[*]}" >&2
  echo "Copy the file downloaded at registration, then:" >&2
  echo "  bash perplexity/install.sh ~/Downloads/bo2bot.env" >&2
  exit 1
fi

mkdir -p "$SECRETS_DIR" "$SKILLS_DIR"
if [[ "$FOUND" != "$CREDS_DST" ]]; then
  cp "$FOUND" "$CREDS_DST"
fi
chmod 600 "$CREDS_DST"
echo "    credentials -> $CREDS_DST"

rm -rf "$SKILL_DST"
cp -R "$SRC" "$SKILL_DST"
find "$SKILL_DST" \( -name '__pycache__' -o -name '*.pyc' \) -exec rm -rf {} + 2>/dev/null || true
echo "    skill        -> $SKILL_DST"

bash "$ROOT/package.sh" "$ZIP_DST" >/dev/null
echo "    zip          -> $ZIP_DST"

if [[ "$NO_OPEN" -eq 0 && "$(uname -s)" == "Darwin" ]]; then
  if [[ -f "$KICKOFF" ]] && command -v pbcopy >/dev/null; then
    pbcopy < "$KICKOFF"
    echo "    clipboard    <- kickoff (Cmd+V in Computer)"
  fi
  open -R "$ZIP_DST" >/dev/null 2>&1 || true
  if open -a Perplexity >/dev/null 2>&1; then
    echo "    opened       Perplexity.app"
  else
    open "https://www.perplexity.ai/computer" >/dev/null 2>&1 || true
    echo "    opened       Computer in the browser"
  fi
fi

echo
echo "Done. Next: paste into Computer (already on the clipboard on Mac)."
echo "If the skill is not in My Skills yet, drop the zip from Finder:"
echo "  Skills → Create skill → Upload a skill → $ZIP_DST"
echo
echo "Then the agent should login, greet hello@bo2bot.com, and log out."
