# skills/ (skills.sh discovery)

skills.sh prefers the repo `skills/` container. This folder mirrors
`../skills-sh/bo2bot-messaging` so the product page and
`npx skills add bo2bot-messaging/bo2bot-skills --skill bo2bot-messaging`
resolve the directory package.

**Edit `skills-sh/bo2bot-messaging/`, then sync here before publish:**

```bash
rsync -a --delete skills-sh/bo2bot-messaging/ skills/bo2bot-messaging/
```

See `docs/publishing-skills-sh.md`.
