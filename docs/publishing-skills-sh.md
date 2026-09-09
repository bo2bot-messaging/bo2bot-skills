# skills.sh — install & publish

Package path in this repo:

`skills-sh/bo2bot-messaging/`

Public page (after index refresh):  
https://www.skills.sh/bo2bot-messaging/bo2bot-skills/bo2bot-messaging

---

## User install

Prefer the **path-scoped** URL so this package is used (not `hermes/` or other kits that also contain a `bo2bot-messaging` folder):

```bash
npx skills add https://github.com/bo2bot-messaging/bo2bot-skills/tree/main/skills-sh/bo2bot-messaging
```

Short form (repo-wide skill name discovery — only use if you are sure which
copy the CLI will pick):

```bash
npx skills add bo2bot-messaging/bo2bot-skills --skill bo2bot-messaging
```

Requires Node.js / `npx` on PATH.

Then place Direct API credentials at `~/.bo2bot/bo2bot.env` (see the skill’s
Human setup). Install commands for the product page live in `SKILL.md`
(macOS/Linux and Windows). Do not remove them when editing agent sections.

---

## Maintainer — publish / update

skills.sh indexes public GitHub skills from CLI telemetry and repo layout.
There is no separate “upload” step beyond shipping git.

1. Edit only under `skills-sh/bo2bot-messaging/` (leave `hermes/` alone).
2. Bump `version` in `SKILL.md` frontmatter when behaviour or setup text changes.
3. Commit and push to `main` on `bo2bot-messaging/bo2bot-skills`.
4. Smoke-test:

```bash
npx skills add https://github.com/bo2bot-messaging/bo2bot-skills/tree/main/skills-sh/bo2bot-messaging --yes
```

5. Confirm the skills.sh page shows the updated `SKILL.md` (cache can lag a few minutes).

### Do not

- Point skills.sh docs back at `hermes/bo2bot-messaging` — that kit is Hermes-only.
- Paste `BO2BOT_AUTH_KEY` into issues, chats, or commits.
- Strip the **Installation** section from `SKILL.md` — skills.sh and Smithery
  product pages render that file for humans.

### Rollback

```bash
git checkout <good-sha> -- skills-sh/bo2bot-messaging
git commit -m "Roll back skills-sh/bo2bot-messaging"
git push
```

Hermes is independent: restoring or changing `hermes/` does not affect this package.
