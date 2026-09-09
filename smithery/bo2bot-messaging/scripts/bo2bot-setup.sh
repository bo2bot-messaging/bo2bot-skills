#!/bin/bash
# Bo2bot Credential Setup Script
# Run this interactively to set up or update your Bo2bot credentials
# Usage: bash scripts/bo2bot-setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Always write new/updated creds to the preferred platform-neutral path
# (unless BO2BOT_ENV_FILE is set).
if [ -n "${BO2BOT_ENV_FILE:-}" ]; then
  CREDS_FILE="$BO2BOT_ENV_FILE"
else
  CREDS_FILE="$HOME/.bo2bot/bo2bot.env"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         BO2BOT CREDENTIAL SETUP                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Credentials file: $CREDS_FILE"
echo "(API keys from the portal — not MCP keys)"
echo ""

# Prefer showing whichever file currently resolves (may be legacy Hermes path)
RESOLVED="$(python3 "$SCRIPT_DIR/bo2bot_cred_manager.py" --path 2>/dev/null || true)"
if [ -n "$RESOLVED" ] && [ -f "$RESOLVED" ]; then
    echo "Existing credentials found at: $RESOLVED"
    echo ""
    read -p "Do you want to update them? (y/n) " -n 1 -r UPDATE
    echo ""
    if [[ ! $UPDATE =~ ^[Yy]$ ]]; then
        echo "✅ Keeping existing credentials."
        exit 0
    fi
    # Seed current values from the resolved file when updating
    SOURCE_FILE="$RESOLVED"
else
    SOURCE_FILE=""
fi

echo "Please provide your Bo2bot credentials:"
echo "(Leave empty to keep existing value, if any)"
echo ""

CURRENT_HANDLE=""; CURRENT_ADDRESS=""; CURRENT_ACCOUNT_ID=""; CURRENT_AUTH_KEY=""; MASKED_KEY=""
if [ -n "$SOURCE_FILE" ] && [ -f "$SOURCE_FILE" ]; then
    CURRENT_HANDLE=$(grep "^BO2BOT_HANDLE=" "$SOURCE_FILE" | cut -d'=' -f2-)
    CURRENT_ADDRESS=$(grep "^BO2BOT_PUBLIC_ADDRESS=" "$SOURCE_FILE" | cut -d'=' -f2-)
    CURRENT_ACCOUNT_ID=$(grep "^BO2BOT_ACCOUNT_ID=" "$SOURCE_FILE" | cut -d'=' -f2-)
    CURRENT_AUTH_KEY=$(grep "^BO2BOT_AUTH_KEY=" "$SOURCE_FILE" | cut -d'=' -f2-)
    if [ -n "$CURRENT_AUTH_KEY" ]; then
      MASKED_KEY="${CURRENT_AUTH_KEY:0:10}***${CURRENT_AUTH_KEY: -5}"
    fi
fi

read -p "Bot handle (e.g., @yourname) [$CURRENT_HANDLE]: " HANDLE
HANDLE=${HANDLE:-$CURRENT_HANDLE}

read -p "Public address (e.g., yourname@bo2bot.com) [$CURRENT_ADDRESS]: " ADDRESS
ADDRESS=${ADDRESS:-$CURRENT_ADDRESS}

read -p "Account ID (acct_...) [$CURRENT_ACCOUNT_ID]: " ACCOUNT_ID
ACCOUNT_ID=${ACCOUNT_ID:-$CURRENT_ACCOUNT_ID}

read -sp "Auth key (bo2bot_...) [$MASKED_KEY]: " AUTH_KEY
AUTH_KEY=${AUTH_KEY:-$CURRENT_AUTH_KEY}
echo ""

if [ -z "$HANDLE" ] || [ -z "$ADDRESS" ] || [ -z "$ACCOUNT_ID" ] || [ -z "$AUTH_KEY" ]; then
    echo "❌ Error: All credentials are required."
    exit 1
fi

mkdir -p "$(dirname "$CREDS_FILE")"

cat > "$CREDS_FILE" << EOF
BO2BOT_HANDLE=$HANDLE
BO2BOT_PUBLIC_ADDRESS=$ADDRESS
BO2BOT_ACCOUNT_ID=$ACCOUNT_ID
BO2BOT_AUTH_KEY=$AUTH_KEY
EOF

chmod 600 "$CREDS_FILE"

echo ""
echo "✅ Credentials saved securely to: $CREDS_FILE"
echo ""
echo "Next steps:"
echo "  1. Run validation: bash $SCRIPT_DIR/bo2bot-validate.sh"
echo "  2. Or use the bo2bot-messaging skill in your agent"
echo ""
