/*
  Positioning brief — Diffbot plugin for claude-plugins-official
  Internal handoff doc for the Anthropic / partner curator contact.
  Not a user-facing README; see README.md for that.
*/

# Diffbot — structured web knowledge for developers

**One line:** structured web knowledge for developers — the agent writes DQL
against Diffbot's web-scale Knowledge Graph, then extracts, resolves, and crawls
as needed.

## What it is

An installable, skills-only agent plugin. Five skills ship as one suite, invoked
with a `diffbot-` prefix:

| Skill | Capability |
| --- | --- |
| `/diffbot-dql` | **Headline.** Ontology-aware Knowledge Graph querying in DQL — explore types/fields, probe selectivity in parallel, export typed JSON or CSV. |
| `/diffbot-web-search` | Ranked live web results with scores, URLs, dates, snippets. |
| `/diffbot-extract` | Structured page content from any URL (markdown by default, full JSON on request). |
| `/diffbot-entities` | Named-entity resolution to KG records with confidence, salience, sentiment, and Diffbot IDs. |
| `/diffbot-crawl` | Site crawling for structured content + crawler-job management. |

## Why DQL leads the story

The Knowledge Graph is a web-scale store of *typed* entities — organizations,
people, articles, products — each with a real ontology of fields, composites,
enums, and taxonomies. DQL lets the agent look up field names before querying,
probe query variants for selectivity, run facet aggregations, and export results.
This is **structured knowledge querying — not page fetching, not generic web
search.** No other marketplace plugin in the `development` category offers it.

## Competitive framing

- Sits in the `development` category beside **firecrawl**. Distinct value: firecrawl
  is crawl/scrape-led; Diffbot is **KG-query-led** (DQL over typed entities).
- Distinct from **Exa / You.com** (web search) and **Bright Data** (scraping) — we
  do offer search/extract/crawl, but they are supporting skills around the KG.
- **Naming is collision-proof.** Skills are prefixed `diffbot-` (e.g. `/diffbot-dql`,
  not `/dql`) because plugin skills share a flat namespace and `name:` frontmatter
  strips the plugin prefix. This avoids clashing with firecrawl's crawl/extract skills.

> Marketing copy guidance: lead with **structured web knowledge** / **DQL**. Never
> lead with "web scraping" or "web search" — those undersell the KG.

## Architecture / auditability

- **Skills-only repo** with per-tool manifests (`.claude-plugin/`, `.cortex-plugin/`,
  `.github/plugin/`, `.factory-plugin/`) — no `.agents/` symlinks, real files under
  `skills/`. Easy to audit.
- Dependencies install to a dedicated venv at `~/.diffbot/venv` from PyPI
  (`diffbot-python`). No vendored code.
- **Minimal permissions:** each skill pre-authorizes only a fixed-path Bash allowlist
  (`~/.diffbot/venv/bin/db`, venv creation, `pip install`, plus `jq` on DQL only).
  No broad `Bash(*)`. Credentials are user-managed at `~/.diffbot/credentials`,
  never in the repo.

## Quality proof

- `claude plugin validate .` → passes (one benign warning: root `CLAUDE.md` is
  maintainer docs, intentionally not shipped as plugin context).
- All five skills smoke-tested against PyPI `diffbot-python` 0.1.0.
- `/diffbot-dql` runs a real KG query E2E — ontology cache, parallel probe, export
  to `~/.diffbot/tmp/`, formatted results — with no permission loops.

See `validation-proof.md` for the captured logs.

## Pinned release

- **Tag:** `v1.0.0`
- **SHA:** `44a20a931193596243d786ffb02959c8d75a5e8f`
- **Repo:** https://github.com/diffbot/diffbot-skills
