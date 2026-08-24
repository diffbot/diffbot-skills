# Diffbot — structured web knowledge for agents

Give your agent access to Diffbot's Knowledge Graph and web structuring APIs. Query over a trillion facts on organizations, people, and news; Crawl and extract sites to build your own structured knowledge graphs.

Compatible with Claude Code, GitHub Copilot (CLI + VS Code), Snowflake Cortex Code, Factory.ai (Droid), and pi.dev. 

## Install

Two supported paths from the same repo: `npx skills` for a one-command install into every detected agent, or the native plugin install for each harness.

### Universal (`npx skills`)

```bash
npx skills add diffbot/diffbot-skills
```

Pulls this repo from GitHub (the skills are not published to npm). The CLI detects your installed agents and writes the skills into each one's skills directory — no marketplace listing involved.

```bash
# Preview the skills in the repo
npx skills add diffbot/diffbot-skills --list

# Install all ten skills globally to every detected agent
npx skills add diffbot/diffbot-skills -g --all

# Install to specific agents (includes Pi, Cursor, Codex, ForgeCode, …)
npx skills add diffbot/diffbot-skills -g -a claude-code -a cursor -a pi -y

# Pin a release tag (git ref via URL or #fragment — @name selects a skill, not a tag)
npx skills add https://github.com/diffbot/diffbot-skills/tree/v1.1.1
npx skills add diffbot/diffbot-skills#v1.1.1
```

Supported agents include Claude Code, Cursor, GitHub Copilot, Codex, Pi, Factory (Droid), Snowflake Cortex Code, ForgeCode, Gemini CLI, OpenCode, and [many more](https://github.com/vercel-labs/skills#supported-agents). Discover packages at [skills.sh](https://skills.sh).

### Claude Code

```bash
/plugin marketplace add diffbot/diffbot-skills
/plugin install diffbot@diffbot-skills
```

Update with `/plugin marketplace update diffbot-skills`.

**From Git (for local tweaking)**

```bash
git clone https://github.com/diffbot/diffbot-skills.git ~/.claude/skills/diffbot-skills
```

Checkout a local copy of `diffbot-skills` and tweak it into your own at the expense of maintaining your own upstream merge schedule.

- **Restart Claude Code after cloning.** Skills-directory plugins are loaded at session start, so they will not appear in a session that is already running.
- **Clone the repository root**, not the `skills/` subdirectory. A directory placed in `~/.claude/skills/` is only discovered without a `.claude-plugin/plugin.json` when its `SKILL.md` sits at the top level.

Confirm the install with `claude plugin list` (expect `diffbot@skills-dir`, ten skills), and update later with `git -C ~/.claude/skills/diffbot-skills pull`.

### GitHub Copilot (CLI + VS Code)

Unlike Claude Code's fancy pants marketplace situation, every other harness keeps it simple.

```bash
copilot plugin install https://github.com/diffbot/diffbot-skills.git
```

### Snowflake Cortex Code (CLI)

```bash
cortex plugin install diffbot/diffbot-skills
```

Pin the release tag:

```bash
cortex plugin install github:diffbot/diffbot-skills@v1.1.1
```

#### Cortex Code Desktop

Agent Settings → Plugins → Add from GitHub → `diffbot/diffbot-skills` (append `#v1.1.1` to pin the tag).

#### Factory.ai (Droid)

```bash
droid plugin install https://github.com/diffbot/diffbot-skills.git
```

#### ForgeCode:

Old school. Copy or symlink the `skills/` directory into `.forge/skills/`.

#### pi.dev

This one comes with its own [pi-wrapped TS library](https://github.com/diffbot/diffbot-pi).

```bash
pi install git:github.com/diffbot/diffbot-pi
```

After install, invoke skills as `/diffbot-dql`, `/diffbot-news`, `/diffbot-organizations`, `/diffbot-people`, `/diffbot-places`, `/diffbot-deals`, `/diffbot-web-search`, `/diffbot-extract`, `/diffbot-entities`, and `/diffbot-crawl`.

### From a third-party catalog (when listed)

These are curated third party catalogs that we have barely any control over but some people prefer these installation paths.

| Harness | Install | Catalog | Status |
| --- | --- | --- | --- |
| Claude Code | `/plugin install diffbot@claude-plugins-official` | `claude-plugins-official` | Submission in progress — see [`docs/listing/anthropic/`](docs/listing/anthropic/). The first-party `diffbot-skills` marketplace above needs no submission. |
| GitHub Copilot | `/plugin install diffbot@awesome-copilot` | `awesome-copilot` | Submission in progress — see [`docs/listing/github/`](docs/listing/github/) |
| Factory (Droid) | `droid plugin marketplace add https://github.com/Factory-AI/factory-plugins` then `droid plugin install diffbot@factory-plugins` | `factory-plugins` | Not yet submitted — see [`docs/listing/factory/`](docs/listing/factory/) |
| Cortex Code | `cortex plugin install diffbot` | Official Cortex marketplace | No public form — partner channel; Git / `npx skills` work today — see [`docs/listing/cortex/`](docs/listing/cortex/) |

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

3. Invoke any skill — the first run bootstraps `~/.diffbot/venv` and installs [`diffbot-python`](https://pypi.org/project/diffbot-python/) (>= 0.2.1) from PyPI.

## Skills

Ten skills ship as one suite of structured-knowledge tools. **DQL is the headline capability** — ontology-aware entity querying that no other marketplace plugin offers. Five use-case skills sit on top of it for the queries people actually ask, and four API skills cover search, extraction, entity resolution, and crawling.

Skill names are prefixed `diffbot-` to avoid collisions in the flat Agent Skills / plugin namespace (e.g. `/diffbot-dql`, not `/dql`).

### Knowledge Graph

#### `/diffbot-news` — News and articles

`type:Article` search, newest-first by default. Filter by mentioned entity, topic taxonomy, publisher, language, date range, or sentiment.

```
/diffbot-news recent AI news
/diffbot-news negative coverage of OpenAI this month
/diffbot-news what has Sam Altman been quoted saying
/diffbot-news European coverage of the Nvidia earnings
```

#### `/diffbot-organizations` — Company search

`type:Organization` search by industry, headquarters, headcount, revenue, funding, ownership, or leadership.

```
/diffbot-organizations public semiconductor companies in the US
/diffbot-organizations AI software startups in Berlin under 100 employees
/diffbot-organizations companies like OpenAI, US only
/diffbot-organizations companies Sequoia has invested in
/diffbot-organizations everything Microsoft has acquired
```

#### `/diffbot-people` — People search

`type:Person` search by job title, employer, employer industry, skills, education, location, or nationality. Covers people with a public online professional presence — it is not a people-finder for private individuals.

```
/diffbot-people who runs Nvidia
/diffbot-people CTOs at biotech companies
/diffbot-people Stanford CS alumni
/diffbot-people female CEOs
```

#### `/diffbot-places` — Geographic entities

Cities, counties, states, countries, regions, and points of interest — by name, population, prominence, containing place, or proximity.

```
/diffbot-places list all countries in Europe
/diffbot-places largest cities in Japan by population
/diffbot-places counties in California
/diffbot-places national parks near Yosemite
```

#### `/diffbot-deals` — Funding and M&A

Funding rounds, investments, and acquisitions by industry, date, size, series, investor, or company.

```
/diffbot-deals AI rounds over $50M this year
/diffbot-deals Sequoia's recent investments
/diffbot-deals largest acquisitions of 2026
/diffbot-deals OpenAI funding history
```

#### `/diffbot-dql` — Raw Knowledge Graph queries

Explore all other standard entities in the Diffbot Knowledge Graph not already covered above. There are tons more like CreativeWork, Brand, Patent, SaaS, Technology, even Research. The agent translates your request into DQL, explores the ontology, probes query variants, and exports typed JSON or CSV. 

```
/diffbot-dql show me all brand marks owned by Disney
/diffbot-dql latest published research in artificial intelligence
```

#### `/diffbot-entities` — Named entity resolution

Identify and link entities in text to Diffbot KG records. Returns confidence, salience, sentiment, and Diffbot IDs usable in DQL.

```
/diffbot-entities Apple CEO Tim Cook announced record quarterly earnings.
/diffbot-entities Elon Musk founded Tesla and SpaceX.
```

### Web Structuring

#### `/diffbot-web-search` — Live web results

Ranked results with relevance scores, URLs, dates, and content snippets. For general web pages and lookups that aren't news — use `/diffbot-news` for news.

```
/diffbot-web-search AI chip startups 2024
/diffbot-web-search recent earnings reports Tesla
```

#### `/diffbot-extract` — Structured page content

Fetch and extract structured content from any URL — markdown by default, full JSON on request.

```
/diffbot-extract https://example.com/article
/diffbot-extract https://example.com/product-page
```

#### `/diffbot-crawl` — Site crawling

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
- **`diffbot-python` >= 0.2.1**, installed automatically on first run
- **Diffbot API token** (free tier available)
- A supported agent (see Install)

## Permissions

Each skill pre-authorizes a minimal fixed-path Bash allowlist: `db`, venv creation, `pip install`, and `jq` (Knowledge Graph skills only). No broad `Bash(*)` grants. Credentials are user-managed at `~/.diffbot/credentials` and never stored in this repo.

## License

MIT — see [LICENSE](LICENSE).
