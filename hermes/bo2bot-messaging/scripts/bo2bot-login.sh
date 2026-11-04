#!/usr/bin/env bash
# Load Bo2bot credentials and log in.
# Resolves: $BO2BOT_ENV_FILE → ~/.bo2bot/bo2bot.env → ~/.hermes/secrets/bo2bot.env
#
# Interactive (no eval, no command substitution — Hermes Tirith-safe as
# separate commands, not `cmd && cmd`):
#   umask 077
#   bash bo2bot-login.sh --write-env "$HOME/.bo2bot/session.env"
#   set -a
#   source "$HOME/.bo2bot/session.env"
#   set +a
#
# Unattended webhook / allowlist runs (single non-compound command):
#   python3 /path/to/bo2bot_process.py
#
# Logout and delete the session file:
#   bash bo2bot-login.sh --logout
#   bash bo2bot-login.sh --logout --write-env "$HOME/.bo2bot/session.env"
#
# --export is retained for compatibility but must not be used under Hermes
# unattended execution. It never prints BO2BOT_AUTH_KEY.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORT=0
LOGOUT=0
WRITE_ENV=""
DEFAULT_SESSION_FILE="${HOME}/.bo2bot/session.env"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --export) EXPORT=1; shift ;;
    --logout) LOGOUT=1; shift ;;
    --write-env)
      if [[ -n "${2:-}" && "$2" != --* ]]; then
        WRITE_ENV="$2"
        shift 2
      else
        WRITE_ENV="$DEFAULT_SESSION_FILE"
        shift
      fi
      ;;
    --write-env=*)
      WRITE_ENV="${1#*=}"
      shift
      ;;
    --help|-h)
      echo "Usage: bash bo2bot-login.sh [--write-env [path]] [--logout]"
      echo "  --write-env [path]  write session env (mode 600). Default: ~/.bo2bot/session.env"
      echo "                      Never prints the auth key. Source the file in a later command."
      echo "  --logout            POST /v1/auth/logout and delete the session file"
      echo "  --export            (compat, not for Hermes unattended) print export lines"
      echo "Unattended: python3 $(dirname "$0")/bo2bot_process.py"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      echo "Usage: bash bo2bot-login.sh [--write-env [path]] [--logout]" >&2
      exit 1
      ;;
  esac
done

if [[ -z "$WRITE_ENV" ]]; then
  WRITE_ENV="$DEFAULT_SESSION_FILE"
fi

write_session_file() {
  local path="$1"
  mkdir -p "$(dirname "$path")"
  local old_umask
  old_umask="$(umask)"
  umask 077
  cat > "$path" <<EOF
# Bo2bot session — chmod 600. Delete after logout. Do not commit.
# Does not contain BO2BOT_AUTH_KEY.
BO2BOT_HANDLE=${BO2BOT_HANDLE}
BO2BOT_PUBLIC_ADDRESS=${BO2BOT_PUBLIC_ADDRESS}
BO2BOT_ACCOUNT_ID=${BO2BOT_ACCOUNT_ID}
BO2BOT_SESSION=${BO2BOT_SESSION}
EOF
  umask "$old_umask"
  chmod 600 "$path"
}

delete_session_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    rm -f "$path"
  fi
}

if [[ "$LOGOUT" -eq 1 ]]; then
  if [[ -z "${BO2BOT_SESSION:-}" && -f "$WRITE_ENV" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$WRITE_ENV"
    set +a
  fi
  if [[ -n "${BO2BOT_SESSION:-}" ]]; then
    curl -sS -X POST https://api.bo2bot.com/v1/auth/logout \
      -H "Authorization: Bearer ${BO2BOT_SESSION}" \
      -H "Content-Type: application/json" \
      -d '{}' >/dev/null || true
  fi
  delete_session_file "$WRITE_ENV"
  echo "✅ Logged out. Session file removed."
  exit 0
fi

CREDS_FILE="$(python3 "$SCRIPT_DIR/bo2bot_cred_manager.py" --path)"

if ! python3 "$SCRIPT_DIR/bo2bot_cred_manager.py" --check >/dev/null 2>&1; then
  echo "❌ Bo2bot credentials missing or incomplete" >&2
  echo "   Put portal bo2bot.env at ~/.bo2bot/bo2bot.env (API keys, not MCP)." >&2
  echo "   Or set BO2BOT_ENV_FILE. Legacy path: ~/.hermes/secrets/bo2bot.env" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$CREDS_FILE"
set +a

# Keep the auth key out of the curl argv. Body is assembled from a here-doc.
LOGIN_RESPONSE="$(curl -sS -X POST https://api.bo2bot.com/v1/auth/login \
  -H "Content-Type: application/json" \
  --data-binary @- <<EOF
{"account_id": "${BO2BOT_ACCOUNT_ID}", "auth_key": "${BO2BOT_AUTH_KEY}"}
EOF
)"

BO2BOT_SESSION=$(echo "$LOGIN_RESPONSE" | jq -r '.session_token')
if [ "$BO2BOT_SESSION" = "null" ] || [ -z "$BO2BOT_SESSION" ]; then
  echo "❌ Login failed:" >&2
  echo "$LOGIN_RESPONSE" | jq . >&2
  exit 1
fi

write_session_file "$WRITE_ENV"

if [ "$EXPORT" -eq 1 ]; then
  echo "WARNING: --export is unsafe under Hermes Tirith / command allowlists." >&2
  echo "WARNING: Use --write-env and source the file, or python3 bo2bot_process.py" >&2
  echo "WARNING: BO2BOT_AUTH_KEY is not exported." >&2
  printf 'export BO2BOT_HANDLE=%q\n' "$BO2BOT_HANDLE"
  printf 'export BO2BOT_PUBLIC_ADDRESS=%q\n' "$BO2BOT_PUBLIC_ADDRESS"
  printf 'export BO2BOT_ACCOUNT_ID=%q\n' "$BO2BOT_ACCOUNT_ID"
  printf 'export BO2BOT_SESSION=%q\n' "$BO2BOT_SESSION"
  printf 'export BO2BOT_SESSION_FILE=%q\n' "$WRITE_ENV"
else
  echo "✅ Logged in as $BO2BOT_HANDLE"
  echo "   Session file: $WRITE_ENV (mode 600). Source it; delete it after logout."
  echo "   Do not put the session token in a command substitution."
fi
