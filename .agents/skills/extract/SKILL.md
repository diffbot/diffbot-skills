---
name: extract
description: "Extract markdown or structured content from a URL using the Diffbot Extract API. Use when the user wants to scrape, parse, fetch, or extract content from a webpage. Triggers on: extract URL, fetch page, parse webpage, get content from URL, extract article, extract structured data."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*)
---

# Diffbot Extract

Extract structured content from any URL via the Diffbot Extract API. The CLI returns a clean markdown rendering of the page by default.

## The `db extract` CLI

All work in this skill is driven by the `db` CLI from the [`diffbot-python`](https://github.com/diffbot/diffbot-python) library. **Always invoke with the fixed path `~/.diffbot/venv/bin/db`.**

```
~/.diffbot/venv/bin/db extract <URL> [-f markdown|json] [-a <api>] [-o <outfile>]
```

| Flag | Default | Description |
|------|---------|-------------|
| `-f`, `--format` | `markdown` | Output format: `markdown` (cleaned text) or `json` (full raw API response) |
| `-a`, `--api` | `analyze` | Diffbot API to use: `analyze` (auto-detect), `article`, `product`, `image`, `video`, `discussion` |
| `-o`, `--output` | stdout | Write output to file instead of stdout |

## Workflow

### Step 1 — bootstrap

```
[ -d ~/.diffbot/venv ] || python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install -q diffbot-python
```

The token is read from `DIFFBOT_API_TOKEN` env var or `~/.diffbot/credentials`. If missing:

```
echo "DIFFBOT_API_TOKEN=YOUR_TOKEN_HERE" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials
```

### Step 2 — extract content

For a quick read of a page:

```
~/.diffbot/venv/bin/db extract "https://example.com/article"
```

For the full raw JSON (useful to inspect all fields Diffbot returns):

```
~/.diffbot/venv/bin/db extract "https://example.com/article" -f json -o ~/.diffbot/tmp/extracted.json
```

Force a specific extractor when auto-detect isn't right:

```
~/.diffbot/venv/bin/db extract "https://example.com/product-page" -a product
~/.diffbot/venv/bin/db extract "https://example.com/article" -a article
```

### Step 3 — display

- For markdown format: the CLI renders `Title`, `URL`, and `Content` directly. Relay it to the user.
- For JSON format: large payloads should be written to a file with `-o`. Read the file and summarize the key fields.

## Common fields in the JSON response

The `objects[0]` structure from the `analyze`/`article` API includes:

| Field | Description |
|-------|-------------|
| `title` | Page/article title |
| `text` | Plain text of the main content |
| `content` | Markdown-formatted content |
| `pageUrl` | Canonical URL |
| `date` | Publication date (ISO 8601) |
| `author` | Author name |
| `tags` | Entity tags (from Diffbot KG) |
| `images` | Extracted images |
| `links` | Outbound links |
| `type` | Detected page type (`article`, `product`, etc.) |

## Tips

- The CLI normalizes URLs automatically — you can omit `https://`.
- For saving article content to disk for later processing, use `-o` to avoid bloating the conversation context.
- If extraction fails with a 4xx/5xx error code, the page may be behind auth, Cloudflare, or a JS SPA. Try `-a article` explicitly as a fallback.
