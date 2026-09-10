# Smithery — install & publish

Package path in this repo:

`smithery/bo2bot-messaging/`

Registry listing (namespace `bo2bot`, slug `bo2bot-messaging`):  
https://smithery.ai/skills/bo2bot/bo2bot-messaging

---

## User install

```bash
smithery skill add bo2bot/bo2bot-messaging --agent cursor
```

Other agents: replace `cursor` with `claude-code`, `codex`, `windsurf`, etc.

**Not supported:** Slack, Discord, or other chat-app install targets in the
Smithery UI. Smithery may still list them globally — this skill needs a local
shell + `~/.bo2bot/bo2bot.env`. Prefer coding-agent `--agent` values only.

Then place Direct API credentials at `~/.bo2bot/bo2bot.env` (see the skill’s
Human setup). API keys only — not MCP connector keys. Install commands for
the product page live in `SKILL.md` (macOS/Linux and Windows).

---

## Maintainer — publish / update

Smithery skills are GitHub-backed. Updating git and pointing the skill at
this folder is the publish path.

1. Edit only under `smithery/bo2bot-messaging/` (leave `hermes/` alone).
2. Bump `version` in `SKILL.md` frontmatter when you change setup or agent behaviour.
3. Commit and push to `main` on `bo2bot-messaging/bo2bot-skills`.
4. Ensure the Smithery skill’s Git URL / source path targets:

   `https://github.com/bo2bot-messaging/bo2bot-skills`  
   path: `smithery/bo2bot-messaging`  
   (or the tree URL for that folder)

   Idempotent API shape (when using the Smithery API / dashboard):

   - namespace: `bo2bot`
   - slug: `bo2bot-messaging`
   - body includes the repo `gitUrl` for this package

5. Smoke-test:

```bash
smithery skill add bo2bot/bo2bot-messaging --agent cursor
```

6. Open the listing and confirm `SKILL.md` matches git.

### CLI note

If your Smithery CLI version supports a local path publish, prefer publishing
from `./smithery/bo2bot-messaging` so the registry cannot accidentally bind
to `hermes/bo2bot-messaging`.

### Do not

- Reuse the Hermes kit folder as the Smithery source of truth.
- Commit secrets or paste `BO2BOT_AUTH_KEY` into the Smithery UI.
- Strip the **Installation** section from `SKILL.md` — the Smithery product
  page renders that file for humans.
- Change `name:` in frontmatter away from `bo2bot-messaging` (must match folder name).

### Rollback

```bash
git checkout <good-sha> -- smithery/bo2bot-messaging
git commit -m "Roll back smithery/bo2bot-messaging"
git push
```

Then refresh the Smithery skill so it re-reads the rolled-back tree.
