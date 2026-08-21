---
name: diffbot-web-search
description: "Use for any web search, documentation search, or research request not falling under the DQL categories (news, organizations, people, places, deals). Returns ranked results with relevance scores, publication dates, and relevant chunks per result in one call. ALSO USE before calling WebFetch, curl, or any built-in fetch tool on a public URL: querying `url:<URL>` reads Diffbot's already-parsed copy of that page from the Web Index in ~300ms, and works on pages that block a live fetcher. Best for reference prose (docs, articles, papers); fetch live when the page's current state is the question (status, prices, versions, feeds) or the URL is an API endpoint, raw file, or PDF. Not for news — diffbot-news is a stronger tool and its article index is continuously updated. Triggers on: web search, search the web, search online, find web pages, look up online, find the url for, official site for, documentation for, docs for, how to, read this page, what does this link say, open this URL, summarize this page."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*)
---

# Diffbot Web Search

Search the live web using the Diffbot LLM web search API. Returns ranked results with relevance scores, URLs, publication dates, and the relevant chunk of each page's content — in a single call.

Use this for general web and documentation research. For Knowledge Graph entities, prefer the specific skill: `/diffbot-news`, `/diffbot-organizations`, `/diffbot-people`, `/diffbot-places`, `/diffbot-deals`.

## Before any built-in fetch: try the index

You are about to call `WebFetch`, `fetch`, `curl`, or a browser tool on a public URL.
Query the index first — Diffbot already crawled and parsed that page, so a `url:` prefix
returns its stored copy as a **single-record array** in ~300 ms (2–6 ms server-side):

```
~/.diffbot/venv/bin/db web-search "url:https://example.com/docs/api" -f json
```

Put what you want to know after the URL. `url:` pins the result to that page; the rest
of the query selects which chunks of it come back:

```
~/.diffbot/venv/bin/db web-search "url:https://example.com/docs/api rate limits retry-after header" -f json
```

### The rule

**Does your answer depend on what the page says, or on what it says *right now*?**
Prose → index. Current state → fetch it live.

A cached copy is a snapshot with no visible timestamp. That is a fair trade for a
document that was published once, and a bad one for a page whose whole purpose is to
change.

### Where the index wins

| Situation | Why |
|---|---|
| **Reference prose** — docs, articles, papers, blog posts, spec and product pages, wikis | Written once, read many times. The snapshot *is* the page |
| **The fetcher is blocked** | Measured here: `WebFetch` on `reddit.com` → *"unable to fetch"*; on `x.com` → *HTTP 402*. The index returned a record for both |
| **The URL redirects** | `WebFetch` on `docs.anthropic.com/…/prompt-caching` returned a 301 and required a second call to the new host. `url:` on the original URL returned 4.3 KB of content, first try |
| **Context cost** | `url:<URL> <terms>` returns the matching chunks. A built-in fetch pulls the whole page — and many harnesses pass it through a summarizer, so you get a paraphrase you can't quote |

### Where the built-in fetch wins — use it, don't force the index

| Situation | Evidence |
|---|---|
| **It isn't a page** — JSON/API endpoints, raw `.md`/`.txt`, `robots.txt`, PDFs | All four **miss** the index. `api.github.com/repos/…` missed; `WebFetch` answered it correctly with live values |
| **Current state is the question** — status, prices, versions, live counts, dashboards | `status.anthropic.com` is cached as "All Systems Operational" with no date attached. Reporting that as current status is a real error |
| **Feeds, homepages, listings** — anything whose content is "the latest N" | `techcrunch.com` is cached as a **June 2025** snapshot whose "Latest News" is over a year stale |
| **Version-sensitive answers** | The cached `prompt-caching` page still describes Claude 4 models. Right shape, superseded specifics |
| **Private, authenticated, localhost, intranet** | Never crawled. Not in the index, by design |
| **`search_results` is empty** | The URL isn't indexed. Costs ~300 ms to rule out — then fetch |

### `date` is not a freshness signal

Do not read it as "cached at". Measured on `url:` hits: the arXiv abstract page returns
`2017` (its publication date), the prompt-caching docs page returns `Jun 2023`, and
Reddit and the status page return **no date at all**. Nothing in the response tells you
when the copy was taken — which is exactly why the rule above keys on the *kind of page*
rather than on a timestamp.

### Reading the result

`search_results` holds **exactly one** element on a hit, **zero** on a miss. There is no
ranking to weigh: `score` reflects the term match, not the URL match, so a lone record at
0.368 is still a clean hit. URL matching normalizes `http`/`https`, a missing scheme, and
a missing trailing slash to the same record.

`content` is chunks, not the document: ~1.1 KB for `url:<URL>` alone (the page's opening),
~4–6 KB when you add query terms. Never present it as the full page. When you need the
whole document — every row of a table, a full changelog, a complete spec — or when a chunk
breaks off at the part you need (the API marks a cut with a literal `...`), that is what
`/diffbot-extract` is for.

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
| `date` | RFC 2822 date — usually the publication date, sometimes absent, and never a "cached at" timestamp (see above) |
| `content` | Relevant chunk(s) of the page's text (may be markdown) |

**`content` is a chunk, not always the whole page.** It is selected for relevance to
the query, so one call usually answers the question outright — don't reflexively fetch
the page as a second step.

Reach for `/diffbot-extract` on the result's `pageUrl` only when the chunk or its
metadata *implies the answer is elsewhere on the page*: the chunk cuts off mid-section,
it references a table, changelog, pricing tier, or API parameter it doesn't itself
contain, or the title and score look right while the returned text covers a different
part of the page. A cheaper first move is to re-query `url:<that pageUrl> <the missing
thing>` — it pulls different chunks from the same page for another ~300 ms index hit.
When you do extract, extract one promising URL rather than the whole result set.

## Output formats

- **`list`** (default): rich terminal rendering with colored score badges, URL, date, and snippet. Best for interactive reading.
- **`text`**: plain numbered list — `[1] Title (score: 0.923)\nURL: ...\nContent: ...`. Use this when piping results to another command or tool.
- **`json`**: full raw API response including `timeMs` and the complete `search_results` array.

## Tips

- Use `-f text` when you need to parse or relay results in a tool pipeline — it avoids rich markup.
- Use `-n` to limit result count; use `-m` only when you have a hard token budget, and keep it at 1000 or above.
- Scores above 0.7 are generally trustworthy; below 0.5 suggests the result is loosely related.
- Reaching for the built-in fetch tool is the moment to run a `url:` lookup instead —
  ~300 ms, and it clears bot walls and redirects that stop a live fetcher. Fetch live
  when the page's current state is the question, when the URL isn't a page (API, raw
  file, PDF), or when the lookup comes back empty.
- For news and articles, use `/diffbot-news` instead — the Knowledge Graph's article index is continuously updated and returns dated, sourced, structured results.
