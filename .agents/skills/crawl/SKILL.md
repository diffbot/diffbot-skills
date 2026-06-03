---
name: crawl
description: "Crawl a website or manage Diffbot crawler jobs. Use when the user wants to crawl a site for structured content, list existing crawl jobs, or delete a crawl job. Triggers on: crawl website, crawl site, crawler job, list crawl jobs, delete crawl job, diffbot crawl."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*)
---

# Diffbot Crawler

Crawl websites for structured content via the Diffbot Crawlbot API, and manage crawler jobs.

## The `db crawl*` CLI commands

**Always invoke with the fixed path `~/.diffbot/venv/bin/db`.**

```
~/.diffbot/venv/bin/db crawl <SITE> [options]            # start a crawl and stream events
~/.diffbot/venv/bin/db crawl-list-jobs [JOB_NAME]        # list all jobs or inspect one
~/.diffbot/venv/bin/db crawl-delete-job <JOB_NAME>       # delete a job
```

### `db crawl` options

| Flag | Default | Description |
|------|---------|-------------|
| `--hops` | `2` | Maximum link depth from seed URLs |
| `--job-name` | auto-generated | Name for the crawler job |
| `--max-to-crawl` | `100` | Maximum pages to crawl |
| `--max-to-process` | `100` | Maximum pages to process |
| `--restrict-domain` | `true` | Only follow links on the same domain as seeds |
| `--api-url` | `""` | Diffbot API endpoint for processing (default: auto/analyze) |
| `--crawl-delay` | `-1` | Delay between requests to same domain (seconds) |
| `--url-crawl-pattern` | none | Only crawl URLs matching this pattern |
| `--url-process-pattern` | none | Only process URLs matching this pattern |
| `--obey-robots` | off | Obey robots.txt |
| `--use-proxies` | off | Use proxies for crawling |
| `--custom-headers` | none | Newline-separated custom HTTP headers |
| `-f`, `--format` | `markdown` | Output: `markdown` or `json` |
| `-o`, `--output` | stdout | Write output to file |

## Workflow

### Step 1 — bootstrap

```
[ -d ~/.diffbot/venv ] || python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install -q diffbot-python
```

The token is read from `DIFFBOT_API_TOKEN` env var or `~/.diffbot/credentials`. If missing:

```
echo "DIFFBOT_API_TOKEN=YOUR_TOKEN_HERE" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials
```

### Step 2 — crawl a site

Basic crawl with defaults (100 pages, 2 hops deep):

```
~/.diffbot/venv/bin/db crawl "https://example.com"
```

Deep crawl of a documentation site, saving to JSON:

```
~/.diffbot/venv/bin/db crawl "https://docs.example.com" \
  --hops 3 \
  --max-to-crawl 500 \
  --max-to-process 500 \
  --restrict-domain \
  -f json \
  -o ~/.diffbot/tmp/crawl_results.json
```

Crawl only blog posts (by URL pattern):

```
~/.diffbot/venv/bin/db crawl "https://example.com" \
  --url-process-pattern "/blog/" \
  --max-to-process 200
```

### Step 3 — manage jobs

List all active jobs:

```
~/.diffbot/venv/bin/db crawl-list-jobs
```

Inspect a specific job:

```
~/.diffbot/venv/bin/db crawl-list-jobs my-job-name
```

Delete a job:

```
~/.diffbot/venv/bin/db crawl-delete-job my-job-name
```

## Understanding crawl output

The `crawl` command streams events as they happen. In markdown format (default):

```
# Job: my-crawl-job-1234567890

- [Success] https://example.com/
- [Success] https://example.com/about
- [!] https://example.com/403-page
```

`[!]` marks pages that were crawled but failed extraction (not HTTP failures — those are skipped silently).

In JSON format each event has `event_type`, `timestamp`, and `details`. Event types:
- `job_created` — job was created on the server; `details.job_name` has the job name
- `url_processed` — a page was processed; `details.url` and `details.status` (`Success` or error)

## Tips

- `--restrict-domain` is on by default — disable it only if you intentionally want to follow external links.
- Use `--url-process-pattern` to focus extraction on specific path segments without narrowing crawling.
- Job names are stable identifiers — always set `--job-name` if you want to look up or delete a job later.
- For large crawls, write output to a file with `-o` rather than reading it all into the conversation.
