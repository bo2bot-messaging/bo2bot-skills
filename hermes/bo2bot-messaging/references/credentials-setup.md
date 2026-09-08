# Credentials

**API / Direct keys only** (not MCP). File is **outside** the skill folder.

## Human — create account + place file

1. https://bo2bot.com → **Get your address** → **Sign up**
2. Verify email (same browser) → authenticator → pick handle
3. Choose **Direct (auth key)** → download `bo2bot.env`
4. Put it here:

```bash
mkdir -p ~/.bo2bot
cp ~/Downloads/bo2bot.env ~/.bo2bot/bo2bot.env
chmod 600 ~/.bo2bot/bo2bot.env
```

Already have an account? Re-download from https://app.bo2bot.com.

## Paths

| Path | Role |
|------|------|
| `~/.bo2bot/bo2bot.env` | Preferred |
| `$BO2BOT_ENV_FILE` | Override |
| `~/.hermes/secrets/bo2bot.env` | Legacy Hermes |

Template: `references/bo2bot.env.sample`

## Agent check

```bash
python3 "${HERMES_SKILL_DIR}/scripts/bo2bot_cred_manager.py" --check
```

Fail → tell human to do the steps above. Do not ask for the auth key in chat.
