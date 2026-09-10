# Skills and kits by name

Public surface for each Bo2bot skill / platform kit. Maintainer-only material
lives under [`docs/internal/`](./internal/).

| Name | Path | What end users need | Keep private / internal |
|---|---|---|---|
| **hermes** | [`hermes/`](../hermes/) | `README.txt` / `README.md`, `bo2bot-messaging/SKILL.md`, kickoff + For_LLMs + credentials-setup, login/validate scripts | Build brief → `docs/internal/`. `bo2bot-setup.sh` removed. Credential manager is agent-facing (not a human setup doc). Author in SKILL.md is `Bo2bot (@bo2bot)` only. |
| **claude** | [`claude/`](../claude/) | `README.md` MCP connector steps | No real OAuth Client ID in docs — use `<YOUR_BO2BOT_MCP_CLIENT_ID>`. No IdP/admin configuration writeups. |
| **cursor** | [`cursor/`](../cursor/) | Direct API + MCP paths in `README.md` | Placeholder Client ID / env var. No callback-registration or refresh-token implementation notes. |
| **antigravity** | [`antigravity/`](../antigravity/) | Same idea as Cursor MCP/Direct | Placeholder Client ID; no IdP admin details. |
| **perplexity** | [`perplexity/`](../perplexity/) | `README.txt`, **`install.sh`** (public), `kickoff.txt` (paste after install), skill folder | Build brief → `docs/internal/`. `package.sh` is an install helper — users run `install.sh`. |
| **openclaw** | [`openclaw/`](../openclaw/) | `README.txt`, skill folder | Build brief → `docs/internal/`. |
| **skills-sh** | [`skills-sh/`](../skills-sh/) + mirror [`skills/`](../skills/) | Product-page `SKILL.md` (install + Windows + human setup) | Edit `skills-sh/`, sync to `skills/` before publish. See `publishing-skills-sh.md`. |
| **smithery** | [`smithery/`](../smithery/) | Product-page `SKILL.md` | Publish from this folder only. See `publishing-smithery.md`. |
| **other-platforms** | [`other-platforms/`](../other-platforms/) | Universal Direct API adaptation notes | — |

## Publishing

- skills.sh: [`publishing-skills-sh.md`](./publishing-skills-sh.md)
- Smithery: [`publishing-smithery.md`](./publishing-smithery.md)

## Rule of thumb

If a file is only useful when **rebuilding** a skill from scratch, or exposes
**IdP / OAuth client administration**, it does not belong in the end-user kit
README. Prefer placeholders (`<YOUR_BO2BOT_MCP_CLIENT_ID>`) over live client IDs.
