<!--
  Draft PR description for xai-org/plugin-marketplace (their PULL_REQUEST_TEMPLATE, filled in).
  Replace <SHA> with the pinned commit before opening.
-->

## What this PR does

Adds the **diffbot** plugin: ten skills for Diffbot's structured web knowledge APIs, led by **DQL** (ontology-aware querying of the Diffbot Knowledge Graph). Five use-case Knowledge Graph skills sit on top of DQL — news, organizations, people, places, deals — alongside web search, page extraction, entity resolution, and site crawling. Skill names are prefixed `diffbot-` so they cannot collide with other plugins in the flat skill namespace.

- Plugin name: `diffbot`
- Type: remote source
- Source URL + pinned SHA (remote): `https://github.com/diffbot/diffbot-skills.git` @ `<SHA>`
- Homepage: https://github.com/diffbot/diffbot-skills

## Ownership

- [x] I own this plugin or have the right to distribute it.
- [x] The `source` repo is published under our official org (`diffbot/`).

## Checklist

- [x] Added/updated exactly one entry in `.grok-plugin/marketplace.json` (valid JSON, kebab-case `name`).
- [x] Remote source pins a full 40-char lowercase commit `sha`, and that commit is public + reachable.
- [x] Regenerated `.grok-plugin/plugin-index.json` (`python3 scripts/generate-plugin-index.py`).
- [x] `python3 scripts/validate-catalog.py` passes locally.
- [x] `python3 scripts/generate-plugin-index.py --check` passes locally.
- [x] `homepage` + clear `description` set; the plugin ships `.grok-plugin/plugin.json` and a `README.md`.
- [x] License is stated (MIT, in the manifest and `LICENSE`).

## Security

- [x] No `curl | bash`, remote-code download/exec, or `postinstall` RCE.
- [x] No reading/exfiltration of secrets, tokens, `.env`, or env vars.
- [x] Hooks and MCP scope are least-privilege — the plugin has no hooks and no MCP servers.
- Network endpoints this plugin calls (and why):
  - `pypi.org` / `files.pythonhosted.org` — first run creates `~/.diffbot/venv` and `pip install`s [`diffbot`](https://pypi.org/project/diffbot/) (>= 3.0.0, formerly `diffbot-python`), the `db` CLI every skill shells out to. Source: https://github.com/diffbot/diffbot-python.
  - `kg.diffbot.com` — Knowledge Graph: DQL queries (`/kg/v3/dql`) and the ontology (`/kg/ontology`).
  - `api.diffbot.com` — Extract (`/v3/*`) and Crawl (`/v3/crawl`).
  - `llm.diffbot.com` — web search (`/api/v1/web_search`).
  - `nl.diffbot.com` — entity recognition and linking (`/v1/`).
- Credentials/permissions it requires (and why):
  - A Diffbot API token, read from `DIFFBOT_API_TOKEN` or `~/.diffbot/credentials`. The user writes that file; the skills never write credentials and are instructed never to echo the token. Free tier at https://app.diffbot.com/get-started/.
  - Each SKILL.md pre-authorizes a fixed-path Bash allowlist only: `~/.diffbot/venv/bin/db`, `python3 -m venv ~/.diffbot/venv`, `~/.diffbot/venv/bin/pip install`, and `jq` (Knowledge Graph skills only). No `Bash(*)`.

## Notes for reviewers

- Skills-only plugin: `skills/*/SKILL.md` plus manifests. No `commands/`, `agents/`, `hooks/`, `.mcp.json`, or bundled scripts.
- The same repo is already installable as a plugin in Claude Code, GitHub Copilot, Snowflake Cortex Code, and Factory Droid, and via `npx skills add diffbot/diffbot-skills`; the Grok Build manifest at `.grok-plugin/plugin.json` mirrors those.
- Not a duplicate of firecrawl / exa / tavily / tinyfish: those are web search and scraping. The headline capability here is DQL over a pre-built Knowledge Graph (organizations, people, places, articles, funding rounds, and more), with extraction and crawling as secondary API skills.
- Diffbot is the company behind the plugin (https://diffbot.com); the source is under the `diffbot` GitHub org.
