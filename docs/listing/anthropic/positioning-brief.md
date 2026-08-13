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

An installable, skills-only agent plugin. Ten skills ship as one suite, invoked
with a `diffbot-` prefix:

| Skill | Capability |
| --- | --- |
| `/diffbot-news` | News and articles from the KG — by mentioned entity, topic taxonomy, publisher, language, date range, or sentiment. Newest-first by default. |
| `/diffbot-organizations` | Company search by industry, headquarters, headcount, revenue, funding, ownership, or leadership — plus `similarTo` lookalike lists. |
| `/diffbot-people` | People by job title, employer, employer industry, skills, education, location, or nationality. |
| `/diffbot-places` | Cities, counties, states, countries, and points of interest by population, prominence, containing place, or proximity. |
| `/diffbot-deals` | Funding rounds, investments, and acquisitions by industry, date, size, series, investor, or company. |
| `/diffbot-dql` | **Headline.** Ontology-aware Knowledge Graph querying in DQL — explore types/fields, probe selectivity in parallel, export typed JSON or CSV. The general-purpose layer the five skills above are built on. |
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
  (`~/.diffbot/venv/bin/db`, venv creation, `pip install`, plus `jq` on the KG skills).
  No broad `Bash(*)`. Credentials are user-managed at `~/.diffbot/credentials`,
  never in the repo.

## Quality proof

- `claude plugin validate .` → passes (one benign warning: root `CLAUDE.md` is
  maintainer docs, intentionally not shipped as plugin context).
- All ten skills smoke-tested against PyPI `diffbot-python` 0.1.0.
- The six Knowledge Graph skills each run a real query E2E — ontology cache,
  parallel probe, export to `~/.diffbot/tmp/`, formatted results — with no
  permission loops.
- Every DQL string shipped in the five new SKILL.md files was executed against the
  live KG before being written; documented traps were verified by observation.

See `validation-proof.md` for the captured logs.

## Pinned release

- **Tag:** `v1.1.0`
- **SHA:** _recorded post-tag_
- **Repo:** https://github.com/diffbot/diffbot-skills
