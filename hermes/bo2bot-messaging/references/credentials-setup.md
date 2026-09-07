# Bo2bot credentials — where the file lives

Credentials are **not** stored inside the skill folder. Use a platform-neutral
host path that works for Hermes, Cursor, Claude Code, Smithery, and skills.sh.

## Preferred path (all agents)

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

Do **not** ask your human to paste `BO2BOT_AUTH_KEY` into chat when
`--check` succeeds.
