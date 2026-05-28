# Diffbot Agent Skills

A set of agent skills for fetching knowledge on the public web. Compatible with Claude Code and most harnesses.

## List of Skills

**/dql**
Query the [Diffbot Knowledge Graph](https://docs.diffbot.com/docs/getting-started-with-diffbot) in natural language. Claude constructs and runs the DQL query.

**/web-search**
Search the web via the Diffbot Web Search API. Returns a ranked list of 10 results. Chunks per result included to avoid secondary fetch actions.

**/extract**
Fetch and extract structured JSON or markdown from any URL with the [Diffbot Extract API](https://docs.diffbot.com/reference/extract-introduction).

**/entities**
Identify and resolve named entities in text using the [Diffbot NLP API](https://docs.diffbot.com/reference/introduction-to-natural-language-api). Helpful for validating LLM responses or pulling in additional context from Diffbot Knowledge Graph. Entities are linked to KG records in addition to returning confidence, salience, and sentiment scores.

**/crawl**
Crawl a website with the [Diffbot Crawl API](https://docs.diffbot.com/reference/crawl-introduction). Helpful for archival or offline site search.

## Dependencies

- **`Python 3.10+`**
- **`diffbot-python`** — Diffbot Python Library

## Setup

**1. Get a Diffbot API token** from https://app.diffbot.com/get-started/

**2. Open this project in your harness** and run any skill.

That's it. Run any skill again and it's ready.

## Usage

### /dql
```
/dql find large tech companies in Austin, Texas
/dql show me CTOs at public biotech companies
/dql recent negative articles about OpenAI
/dql top cities where data scientists work
/dql software startups in Berlin under 100 employees with a female CEO
```

Claude constructs the DQL query, executes it against the Diffbot API, and returns formatted results. You can ask for the next page, refine the query, or request a different format.

### /web-search
```
/web-search AI chip startups 2024
/web-search recent earnings reports Tesla
/web-search latest news on Anthropic
```

Returns ranked results with relevance scores, URLs, publication dates, and content chunks.

### /extract
```
/extract https://example.com/article
/extract https://example.com/product-page
```

Returns a clean markdown rendering of the page by default. Pass Supports auto-detect or forcing a specific extractor (`article`, `product`, `image`, etc.).

### /entities
```
/entities Apple CEO Tim Cook announced record quarterly earnings.
/entities Elon Musk founded Tesla and SpaceX.
```

Returns a table of entities with type, confidence, salience, sentiment, and Diffbot KG ID. Use `-f dql` to pipe entity IDs directly into a `/dql` query.

### /crawl
```
/crawl https://docs.example.com
/crawl https://example.com --url-process-pattern /blog/ --max-to-process 200
/crawl list jobs
/crawl delete job my-job-name
```

Streams crawl events as they happen. Jobs can be named, listed, and deleted.

## Credentials file format

```
DIFFBOT_API_TOKEN=YOUR_DIFFBOT_TOKEN_HERE
```

The file lives at `~/.diffbot/credentials` on your local machine and is never part of this repository.
