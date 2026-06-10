/*
  Validation proof — captured during pre-release (Phase 1), v1.0.0.
  Pinned commit: 44a20a931193596243d786ffb02959c8d75a5e8f
*/

# Validation proof — diffbot-skills v1.0.0

Captured on 2026-06-10 against PyPI `diffbot-python` **0.1.0**, with a valid token
at `~/.diffbot/credentials`.

## Manifest / structure

```
$ claude plugin validate .
Validating plugin manifest: .../.claude-plugin/plugin.json
Validating plugin: .../CLAUDE.md
⚠ Found 1 warning:
  ❯ root: CLAUDE.md at the plugin root is not loaded as project context.
    To ship context with your plugin, use a skill (skills/<name>/SKILL.md) instead.
✔ Validation passed with warnings
```

The single warning is expected: `CLAUDE.md` is maintainer documentation, not
user-facing plugin context. All four manifests are in sync (name, version,
license, repository, homepage, keywords); descriptions differ only by agent
noun (Claude / Cortex / agent / droid).

## CLI smoke tests (PyPI diffbot-python 0.1.0)

All eight subcommands the skills rely on are present:
`ask, crawl, crawl-delete-job, crawl-list-jobs, dql, entities, extract, web-search`.

| Skill | Command | Result |
| --- | --- | --- |
| DQL | `db dql init` | ontology refreshed, token found |
| DQL | `db dql probe 'type:Organization name:"Diffbot"'` | `4` hits |
| DQL | `db dql export ... --out ~/.diffbot/tmp/semis.csv` | saved 743 bytes, formatted CSV |
| web-search | `db web-search "Diffbot"` | ranked results with scores |
| extract | `db extract https://example.com` | markdown content |
| entities | `db entities "Apple CEO Tim Cook"` | Apple Inc. + Tim Cook resolved, Diffbot IDs (no `jq` needed) |
| crawl | `db crawl-list-jobs` | read-only: "No crawler jobs found." |

## Live DQL E2E

`db dql export 'type:Organization isPublic:true industries:"Semiconductor"
location.country.name:"United States"' --out ~/.diffbot/tmp/semis.csv` produced
formatted rows (Intel, Nvidia, Qualcomm, …) — confirming the full path:
ontology cache → parallel probe → export to `~/.diffbot/tmp/` → formatted output,
with no repeated permission prompts.

## Permissions summary

Each SKILL.md pre-authorizes only a fixed-path Bash allowlist:

```
Bash(~/.diffbot/venv/bin/db:*)
Bash(python3 -m venv ~/.diffbot/venv:*)
Bash(~/.diffbot/venv/bin/pip install:*)
Bash(jq:*)              # diffbot-dql only
```

No broad `Bash(*)`. Credentials are user-managed at `~/.diffbot/credentials`.
