# Diffbot — structured web knowledge for developers

An installable agent plugin that gives your coding agent access to Diffbot's web-scale knowledge graph and structured knowledge APIs. Query organizations, people, and articles with ontology-aware DQL — then enrich, extract, resolve entities, or crawl as needed.

Compatible with Claude Code, GitHub Copilot (CLI + VS Code), Snowflake Cortex Code, and Factory.ai (Droid).

## Install

**Claude Code** (marketplace, once listed):

```
/plugin install diffbot@claude-plugins-official
```

**Claude Code** (local):

```bash
git clone https://github.com/diffbot/diffbot-skills.git
cd diffbot-skills
claude --plugin-dir .
```

**GitHub Copilot CLI / VS Code:**

```bash
copilot plugin install https://github.com/diffbot/diffbot-skills
```

**Factory.ai (Droid):**

```bash
droid plugin install https://github.com/diffbot/diffbot-skills
```

**Snowflake Cortex Code:** clone this repo and point Cortex at the directory (reads `.cortex-plugin/plugin.json`).

**ForgeCode:** no installable manifest — copy or symlink the `skills/` tree into `.forge/skills/`.

## Setup

1. Get a Diffbot API token at [app.diffbot.com/get-started](https://app.diffbot.com/get-started/).
2. Save it to `~/.diffbot/credentials`:

```
DIFFBOT_API_TOKEN=YOUR_TOKEN_HERE
```

Run this once on your machine (the skill will not write credentials for you):

```bash
echo "DIFFBOT_API_TOKEN=YOUR_TOKEN_HERE" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials
```

3. Invoke any skill — the first run bootstraps `~/.diffbot/venv` and installs [`diffbot-python`](https://pypi.org/project/diffbot-python/) from PyPI.

## Skills

Five skills ship as one suite of structured-knowledge tools. **DQL is the headline capability** — ontology-aware entity querying that no other marketplace plugin offers.

Skill names are prefixed `diffbot-` to avoid collisions in the flat plugin namespace (e.g. `/diffbot-dql`, not `/dql`).

### `/diffbot-dql` — Knowledge Graph queries

The agent translates your request into DQL, explores the ontology, probes query variants, and exports typed JSON or CSV.

```
/diffbot-dql find public semiconductor companies in the US
/diffbot-dql show me CTOs at public biotech companies
/diffbot-dql recent negative articles about OpenAI
/diffbot-dql top cities where data scientists work
/diffbot-dql software startups in Berlin under 100 employees with a female CEO
```

### `/diffbot-web-search` — Live web results

Ranked results with relevance scores, URLs, dates, and content snippets. Useful when you need current events beyond the KG crawl schedule.

```
/diffbot-web-search AI chip startups 2024
/diffbot-web-search recent earnings reports Tesla
```

### `/diffbot-extract` — Structured page content

Fetch and extract structured content from any URL — markdown by default, full JSON on request.

```
/diffbot-extract https://example.com/article
/diffbot-extract https://example.com/product-page
```

### `/diffbot-entities` — Named entity resolution

Identify and link entities in text to Diffbot KG records. Returns confidence, salience, sentiment, and Diffbot IDs usable in DQL.

```
/diffbot-entities Apple CEO Tim Cook announced record quarterly earnings.
/diffbot-entities Elon Musk founded Tesla and SpaceX.
```

### `/diffbot-crawl` — Site crawling

Crawl a website for structured content and manage crawler jobs.

```
/diffbot-crawl https://docs.example.com
/diffbot-crawl https://example.com --url-process-pattern /blog/ --max-to-process 200
```

## Why DQL

The Diffbot Knowledge Graph is a web-scale store of structured entities — organizations, people, articles, products, and more — each with a typed ontology of fields, composites, enums, and taxonomies. DQL lets the agent:

- Look up field names and types before constructing queries (`db dql ontology`)
- Probe query variants in parallel to validate selectivity
- Export results as JSON (for downstream analysis) or CSV (for display)
- Run facet aggregations for distribution questions

This is structured knowledge querying — not page fetching, not generic web search.

## Requirements

- **Python 3.10+** (used to bootstrap `~/.diffbot/venv`)
- **Diffbot API token** (free tier available)
- A supported agent harness with plugin support (see Install)

## Permissions

Each skill pre-authorizes a minimal fixed-path Bash allowlist: `db`, venv creation, `pip install`, and `jq` (DQL only). No broad `Bash(*)` grants. Credentials are user-managed at `~/.diffbot/credentials` and never stored in this repo.

## License

MIT — see [LICENSE](LICENSE).
