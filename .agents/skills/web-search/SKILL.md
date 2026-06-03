---
name: web-search
description: "Search the web using the Diffbot LLM web search API. Use when the user wants to search the web, find recent news or pages, or get ranked web results with snippets. Triggers on: web search, search the web, diffbot search, search online, find web pages, web results."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*)
---

# Diffbot Web Search

Search the web using the Diffbot LLM web search API. Returns ranked results with scores, URLs, dates, and content snippets.

## The `db web-search` CLI

**Always invoke with the fixed path `~/.diffbot/venv/bin/db`.**

```
~/.diffbot/venv/bin/db web-search "<query>" [-n <N>] [-m <max-tokens>] [-f list|json|text]
```

| Flag | Default | Description |
|------|---------|-------------|
| `-n`, `--num-results` | API default | Number of results to return |
| `-m`, `--max-tokens` | none | Limit total response tokens (for agentic use) |
| `-f`, `--format` | `list` | Output format: `list` (rich terminal), `json` (raw API), `text` (plain/agent-friendly) |

## Workflow

### Step 1 — bootstrap

```
[ -d ~/.diffbot/venv ] || python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install -q diffbot-python
```

The token is read from `DIFFBOT_API_TOKEN` env var or `~/.diffbot/credentials`. If missing:

```
echo "DIFFBOT_API_TOKEN=YOUR_TOKEN_HERE" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials
```

### Step 2 — search

Basic search (interactive rich display):

```
~/.diffbot/venv/bin/db web-search "AI chip startups 2024"
```

Get top 5 results:

```
~/.diffbot/venv/bin/db web-search "diffbot knowledge graph" -n 5
```

Plain text output (for piping or agentic use):

```
~/.diffbot/venv/bin/db web-search "recent earnings reports Tesla" -f text
```

Full raw JSON:

```
~/.diffbot/venv/bin/db web-search "query" -f json -n 10
```

## Result fields

Each result in the `search_results` array contains:

| Field | Description |
|-------|-------------|
| `score` | Relevance score (0–1); `>0.85` is excellent, `0.7–0.85` good, `0.5–0.7` fair |
| `title` | Page title |
| `pageUrl` | URL |
| `date` | Publication date (RFC 2822 format) |
| `content` | Full text content of the result (may be markdown) |

## Output formats

- **`list`** (default): rich terminal rendering with colored score badges, URL, date, and snippet. Best for interactive reading.
- **`text`**: plain numbered list — `[1] Title (score: 0.923)\nURL: ...\nContent: ...`. Use this when piping results to another command or tool.
- **`json`**: full raw API response including `timeMs` and the complete `search_results` array.

## Tips

- Use `-f text` when you need to parse or relay results in a tool pipeline — it avoids rich markup.
- Use `-m` to cap token usage for integrations where you have a budget.
- Scores above 0.7 are generally trustworthy; below 0.5 suggests the result is loosely related.
- For very recent events, prefer `web-search` over `dql` — the KG updates on a crawl schedule while web search is live.
