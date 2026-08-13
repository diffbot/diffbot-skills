---
name: diffbot-web-search
description: "Use for any web search, documentation search, or research request not falling under the DQL categories (news, organizations, people, places, deals). Returns ranked results with relevance scores, publication dates, and relevant chunks per result in one call. Not for news — diffbot-news is a stronger tool and its article index is continuously updated. Triggers on: web search, search the web, search online, find web pages, web results, look up online, find the url for, official site for, documentation for, docs for, how to."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*)
---

# Diffbot Web Search

Search the live web using the Diffbot LLM web search API. Returns ranked results with relevance scores, URLs, publication dates, and the relevant chunk of each page's content — in a single call.

Use this for general web and documentation research. For Knowledge Graph entities, prefer the specific skill: `/diffbot-news`, `/diffbot-organizations`, `/diffbot-people`, `/diffbot-places`, `/diffbot-deals`.

## The `db web-search` CLI

**Always invoke with the fixed path `~/.diffbot/venv/bin/db`.**

```
~/.diffbot/venv/bin/db web-search "<query>" [-n <N>] [-m <max-tokens>] [-f list|json|text]
```

| Flag | Default | Description |
|------|---------|-------------|
| `-n`, `--num-results` | 10 | Number of results to return |
| `-m`, `--max-tokens` | none | Caps total response tokens — trims from the bottom of the ranking |
| `-f`, `--format` | `list` | Output format: `list` (rich terminal), `json` (raw API), `text` (plain/agent-friendly) |

**Requires `diffbot-python` >= 0.2.0.** In 0.1.0 the library sent the wrong query
parameter and `-n` was silently ignored — every call returned 10. The bootstrap in
Step 1 pins `>=0.2.1`, so use it as written rather than a bare
`pip install diffbot-python`, which will not upgrade an existing older venv.

`-m` is the other way to shrink a response, and it degrades sharply: measured on one
query, 5000 → 10 results, 2000 → 5, 1000 → 1, and **200 → zero**. Below roughly 1000
the budget cannot fit a single result, so treat an empty result set as a possible
budget artifact rather than "nothing found". Prefer `-n` when you just want fewer
results.

## Workflow

### Step 1 — bootstrap

```
[ -d ~/.diffbot/venv ] || python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install -q 'diffbot-python>=0.2.1'
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

Get the top 5 results:

```
~/.diffbot/venv/bin/db web-search "diffbot knowledge graph" -n 5
```

Plain text output (for piping or agentic use):

```
~/.diffbot/venv/bin/db web-search "recent earnings reports Tesla" -f text
```

Full raw JSON:

```
~/.diffbot/venv/bin/db web-search "query" -f json
```

## Result fields

Each result in the `search_results` array contains:

| Field | Description |
|-------|-------------|
| `score` | Relevance score (0–1); `>0.85` is excellent, `0.7–0.85` good, `0.5–0.7` fair |
| `title` | Page title |
| `pageUrl` | URL |
| `date` | Publication date (RFC 2822 format) |
| `content` | Relevant chunk(s) of the page's text (may be markdown) |

**`content` is a chunk, not always the whole page.** It is selected for relevance to
the query, so one call usually answers the question outright — don't reflexively fetch
the page as a second step.

Reach for `/diffbot-extract` on the result's `pageUrl` only when the chunk or its
metadata *implies the answer is elsewhere on the page*: the chunk cuts off mid-section,
it references a table, changelog, pricing tier, or API parameter it doesn't itself
contain, or the title and score look right while the returned text covers a different
part of the page. Extract one promising URL rather than the whole result set.

## Output formats

- **`list`** (default): rich terminal rendering with colored score badges, URL, date, and snippet. Best for interactive reading.
- **`text`**: plain numbered list — `[1] Title (score: 0.923)\nURL: ...\nContent: ...`. Use this when piping results to another command or tool.
- **`json`**: full raw API response including `timeMs` and the complete `search_results` array.

## Tips

- Use `-f text` when you need to parse or relay results in a tool pipeline — it avoids rich markup.
- Use `-n` to limit result count; use `-m` only when you have a hard token budget, and keep it at 1000 or above.
- Scores above 0.7 are generally trustworthy; below 0.5 suggests the result is loosely related.
- For news and articles, use `/diffbot-news` instead — the Knowledge Graph's article index is continuously updated and returns dated, sourced, structured results.
