/*
  Draft PR description for Factory-AI/factory-plugins.
  Vendoring: copy skills/ and a slim plugin.json into plugins/diffbot/ before opening the PR.
*/

# Add diffbot plugin — structured web knowledge (DQL-led)

## Summary

Adds the **diffbot** plugin: ten skills for Diffbot's structured web knowledge APIs, led by **DQL** (ontology-aware Knowledge Graph querying). Five use-case Knowledge Graph skills sit on top of DQL — news, organizations, people, places, deals — alongside web-search, extract, entities, and crawl. Skill names are prefixed `diffbot-` for flat-namespace collision safety.

**Upstream:** https://github.com/diffbot/diffbot-skills (sync from tag `v1.1.0`, SHA recorded post-tag).

## Plugin layout

```
plugins/diffbot/
├── .factory-plugin/plugin.json
└── skills/
    ├── diffbot-dql/SKILL.md
    ├── diffbot-news/SKILL.md
    ├── diffbot-organizations/SKILL.md
    ├── diffbot-people/SKILL.md
    ├── diffbot-places/SKILL.md
    ├── diffbot-deals/SKILL.md
    ├── diffbot-web-search/SKILL.md
    ├── diffbot-extract/SKILL.md
    ├── diffbot-entities/SKILL.md
    └── diffbot-crawl/SKILL.md
```

## Marketplace entry

```json
{
  "name": "diffbot",
  "description": "Structured web knowledge tools for development and research. Enables querying of Diffbot’s Knowledge Graph (for organizations, people, and news articles) as well as web extraction, crawling, entity resolution, and web search.",
  "source": "./plugins/diffbot",
  "category": "research"
}
```

## Install (after merge)

```bash
droid plugin marketplace add https://github.com/Factory-AI/factory-plugins
droid plugin install diffbot@factory-plugins
```

## Setup (user)

- Diffbot API token at `~/.diffbot/credentials` ([get token](https://app.diffbot.com/get-started/))
- Python 3.10+ — first skill run bootstraps `~/.diffbot/venv` and installs `diffbot-python` from PyPI

## Security / audit notes

- Skills-only plugin — no hooks, MCP servers, or bundled scripts
- Each skill pre-authorizes a fixed-path Bash allowlist (`~/.diffbot/venv/bin/db`, venv creation, `pip install`, `jq` on the KG skills)
- No secrets in repo; credentials user-managed

## Test plan

- [ ] `droid plugin marketplace add` (fork) + `droid plugin install diffbot@factory-plugins`
- [ ] `/diffbot-dql` discovers and runs a real KG query E2E with a valid API token
- [ ] All ten skills appear in the plugin skill list

## Post-listing

Users can also install directly from Git (no marketplace):

```bash
droid plugin install https://github.com/diffbot/diffbot-skills.git
```
