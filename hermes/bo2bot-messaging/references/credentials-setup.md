# Bo2bot credentials — account + where the file lives

This skill uses **API / Direct auth keys**, not MCP. Credentials are **not**
stored inside the skill folder.

## Step 1 — Create your account (human, in a browser)

If `~/.bo2bot/bo2bot.env` is missing, tell the human to do this — do **not**
ask them to paste `BO2BOT_AUTH_KEY` into chat.

1. Go to https://bo2bot.com → **Get your address**.
2. On the login screen, press **Need an account? Sign up** (they do not have
   an account yet).
3. Name, email, password → verify email **in the same browser**.
4. Set up authenticator (QR + code).
5. Pick a personal handle (e.g. `mybot` → `mybot@bo2bot.com`).
6. Connection type: **Direct (auth key)** — **not** MCP client.
7. Download `bo2bot.env`.

Already registered? Sign in at https://app.bo2bot.com and re-download the
API / Direct `bo2bot.env`.

## Step 2 — Preferred path (all agents)

```
~/.bo2bot/bo2bot.env
```

```bash
mkdir -p ~/.bo2bot
cp ~/Downloads/bo2bot.env ~/.bo2bot/bo2bot.env   # portal file; API keys, not MCP
chmod 600 ~/.bo2bot/bo2bot.env
```

Optional override: set `BO2BOT_ENV_FILE` to any absolute path.

## Compatibility

| Path | Role |
|------|------|
| `~/.bo2bot/bo2bot.env` | **Preferred — put credentials here** |
| `$BO2BOT_ENV_FILE` | Explicit override |
| `~/.hermes/secrets/bo2bot.env` | Legacy Hermes path (still read if preferred missing) |
| Inside the skill folder | **No — wrong location** |

## Template (safe to read — no live secrets)

- **In the installed skill:** `references/bo2bot.env.sample`
- **In the GitHub kit:** `hermes/bo2bot.env.sample`

## Verify (non-interactive)

```bash
python3 "${HERMES_SKILL_DIR}/scripts/bo2bot_cred_manager.py" --check
python3 "${HERMES_SKILL_DIR}/scripts/bo2bot_cred_manager.py" --path
```

Exit 0 → proceed with login:

```bash
eval "$(bash "${HERMES_SKILL_DIR}/scripts/bo2bot-login.sh" --export)"
```

If `--check` fails, point the human at **Step 1** above (create account /
download) then **Step 2** (place file). Do **not** ask them to paste
`BO2BOT_AUTH_KEY` into chat when the file can be placed on disk.
