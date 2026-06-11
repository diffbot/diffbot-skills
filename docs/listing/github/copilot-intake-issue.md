/*
  Draft for the awesome-copilot external-plugin intake issue.
  File at: https://github.com/github/awesome-copilot (External Plugin issue form).
  Do NOT PR plugins/external.json directly — use the issue form.
*/

# awesome-copilot external plugin intake — diffbot

## Field values

| Field | Value |
| --- | --- |
| Plugin name | `diffbot` |
| Repository | `diffbot/diffbot-skills` |
| Plugin path | `/` (repo root) |
| Ref | `v1.0.0` |
| SHA | `44a20a931193596243d786ffb02959c8d75a5e8f` |
| Version | `1.0.0` |
| License | `MIT` |
| Author | Diffbot — https://diffbot.com |
| Homepage | https://github.com/diffbot/diffbot-skills |
| Keywords | `web-knowledge`, `structured-data`, `dql`, `knowledge-graph`, `entity-search`, `company-research`, `developer-tools` |

## Description (paste into issue body)

Structured web knowledge tools for development and research. Enables querying of
Diffbot’s Knowledge Graph (for organizations, people, and news articles) as well
as web extraction, crawling, entity resolution, and web search. Five skills,
prefixed `diffbot-` for flat-namespace collision safety: `/diffbot-dql`,
`/diffbot-web-search`, `/diffbot-extract`, `/diffbot-entities`, `/diffbot-crawl`.

## Pre-submission checklist (already met)

- [x] `.github/plugin/plugin.json` present (with the `plugin/` subdir Copilot/VS Code reads)
- [x] `name`, `description`, `version`, `license`, `author`, `keywords`, `repository` (HTTPS)
- [x] Skills auto-discover from `skills/` at repo root
- [x] Public GitHub repo with immutable `ref` (`v1.0.0`) + `sha`

## Intake automation expectations

After the issue opens, automation will:
1. Validate metadata
2. Run `skill-validator check --plugin` on the submitted ref/sha
3. Smoke-test install via Copilot CLI

If gates fail (`requires-submitter-fixes`): fix the plugin, then comment
`/rerun-intake` on the issue.

## Post-approval

Maintainers add an entry to `plugins/external.json`
(`source.source: "github"`, `source.repo: "diffbot/diffbot-skills"`, `path: "/"`).
Users install via:

```
/plugin install diffbot@awesome-copilot
```
