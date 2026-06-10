# Marketplace listing playbooks

Internal docs for getting `diffbot` into each harness's curated catalog. Git-based install from this repo works on every platform today — see the README Install section.

**Pinned release:** `v1.0.0` @ `44a20a931193596243d786ffb02959c8d75a5e8f`

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

Skills auto-discover from `skills/` at the repo root. No `skills` path override in any manifest.
