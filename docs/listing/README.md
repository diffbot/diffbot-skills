# Marketplace listing playbooks

Internal docs for getting `diffbot` into each harness's curated catalog.

**Universal install (any Agent Skills harness):** `npx skills add diffbot/diffbot-skills` — see the README Install section. That path does not require marketplace listing.

**Plugin / marketplace install:** native plugin commands and curated catalogs below. Git-based plugin install from this repo also works on every listed platform today.

**Pinned release:** `v1.1.0` @ `466f802ebadd8126bb09dc9fe9e81b736a8814b6`

| Platform | Catalog | Submission path | Folder |
| --- | --- | --- | --- |
| Claude Code | `claude-plugins-official` | Partner / curator handoff (no public form) | [`anthropic/`](anthropic/) |
| GitHub Copilot | `awesome-copilot` | External-plugin intake issue | [`github/`](github/) |
| Snowflake Cortex Code | Official Cortex marketplace | Partner channel (no public PR form) | [`cortex/`](cortex/) |
| Factory (Droid) | `factory-plugins` | PR to `Factory-AI/factory-plugins` | [`factory/`](factory/) |

Manifests in this repo (keep in sync):

| Harness | Path |
| --- | --- |
| Claude Code | `.claude-plugin/plugin.json` |
| Cortex Code | `.cortex-plugin/plugin.json` |
| Copilot / VS Code | `.github/plugin/plugin.json` |
| Factory (Droid) | `.factory-plugin/plugin.json` |

Skills auto-discover from `skills/` at the repo root (`diffbot-*` dirs with required `name:` frontmatter for both plugin hosts and `npx skills`). No `skills` path override in any manifest.
