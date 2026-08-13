---
name: diffbot-news
description: "Search news and articles in the Diffbot Knowledge Graph by mentioned company, person, topic, publisher, language, date range, or sentiment — returns dated, sourced, linkable results, newest first. MUST USE skill for all news, including breaking and developing stories. Use for coverage of an entity over time, sentiment trends, or who said what. Triggers on: news, recent news, latest news, breaking news, headlines, articles about, press coverage, media mentions, coverage of, what's being said about, news sentiment, quotes from."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*), Bash(jq:*)
---

# Diffbot News Search

Find news articles in the Diffbot Knowledge Graph. This is `type:Article` DQL with news-shaped defaults already chosen for you: recency sorting, the right narrowing levers, and a display format built for headlines.

For non-news entity queries (companies, people, places, deals) use the sibling skills — `/diffbot-organizations`, `/diffbot-places`, `/diffbot-deals` — or `/diffbot-dql` for anything outside those shapes.

This is the skill for **all** news requests, breaking events included — the KG's article index updates continuously. Do not hand news off to `/diffbot-web-search`.

## Workflow

### Step 1 — bootstrap

```
[ -d ~/.diffbot/venv ] || python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install -q 'diffbot-python>=0.2.1'
~/.diffbot/venv/bin/db dql init
```

Guard the venv creation as shown — re-running `python3 -m venv` on an existing venv overwrites activation scripts. `init` refreshes `~/.diffbot/ontology.json` and verifies a token (`DIFFBOT_API_TOKEN` env var, else `~/.diffbot/credentials`). If neither exists the user must run:

```
echo "DIFFBOT_API_TOKEN=YOUR_TOKEN_HERE" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials
```

Tokens: https://app.diffbot.com/get-started/. Never echo the token.

### Step 2 — build the query

Every query starts `type:Article`. Add narrowing clauses, then apply the sort rule.

#### The sort rule

| The user's request | Sort clause |
| --- | --- |
| No sort and no date condition | append `sortBy:date` (newest first) — **the default** |
| Names an explicit sort ("most relevant", "highest sentiment") | use that sort; do not add `sortBy:date` |
| Contains a date condition (`date>=`, "in July", "last quarter", "2024") | omit `sortBy:date` — the window already scopes recency, so let relevance ordering pick the best articles inside it |

`sortBy:date` is ascending by field name but returns newest-first for `date`; use `revSortBy:date` only if the user explicitly wants oldest-first.

#### Narrowing levers, in order of preference

1. **`tags.label:"<entity>"`** — articles that *mention* a KG entity. The strongest lever for "news about X" where X is a company, person, product, or place.
   ```
   type:Article tags.label:"Nvidia" sortBy:date
   ```
   Tag values are entity names; there is no exhaustive list. If a tag returns zero or too few hits, fall back to `text:`.

2. **`categories.name:"<category>"`** — IAB topic taxonomy (459 values), best for subject-matter queries.
   ```
   type:Article categories.name:"Artificial Intelligence" sortBy:date
   ```
   Look up exact names before using: `~/.diffbot/venv/bin/db dql ontology taxonomy ArticleCategory <regex>`

3. **`text:"<phrase>"`** — full-text fallback when no tag or category fits.

4. **`title:"<phrase>"`** — headline-only match; much tighter than `text:`.

#### Field reference

| Field | Type | Notes |
| --- | --- | --- |
| `date` | DDateTime | Publication date. Compare as `date>="2026-01-01"` |
| `title` | String | Headline |
| `summary` | String | Short abstract — **use this, not `text` or `html`** |
| `text` / `html` | String | Full body. Huge; never pull into the conversation |
| `siteName` | String | Publisher, e.g. `"Reuters"` |
| `author` | String | Byline |
| `language` | String | ISO code, e.g. `"en"`, `"no"` |
| `publisherCountry` | String | Full country name, e.g. `"Norway"` — not a code |
| `publisherRegion` | String | Macro region, e.g. `"Northern Europe"` |
| `sentiment` | Float | −1 (negative) to +1 (positive) |
| `tags` | list | `tags.label`, `tags.sentiment`, `tags.score` — per-entity sentiment lives here |
| `categories` | list | `categories.name`, `categories.score` |
| `quotes` | list | `quotes.speaker`, `quotes.quote` |
| `pageUrl` | String | Canonical article URL |

#### Worked examples

```
type:Article tags.label:"OpenAI" sortBy:date
type:Article categories.name:"Artificial Intelligence" date>="2026-08-01"
type:Article tags.label:"OpenAI" sentiment<-0.5 sortBy:date
type:Article language:"en" tags.label:"Nvidia" date>="2026-08-05"
type:Article quotes.speaker:"Sam Altman" sortBy:date
type:Article tags.label:or("Tesla","Rivian") categories.name:"Automotive" sortBy:date
```

**Entity-specific sentiment.** Document-level `sentiment` scores the whole article. For "negative coverage *of Nvidia specifically*" in an article that also covers others, co-constrain inside the tag with a subquery:

```
type:Article tags.{label:"Nvidia" sentiment<-0.3} sortBy:date
```

#### "Who is covering this?" is a facet

For distribution questions — which outlets, which topics, how coverage is spread over
time — aggregate rather than listing articles:

```
~/.diffbot/venv/bin/db dql export 'type:Article tags.label:"Anthropic" facet:siteName' \
  --out ~/.diffbot/tmp/facet.json --format json --size 15
```

Also useful: `facet:categories.name` (what topics an entity gets covered under),
`facet:publisherCountry` (geographic spread), `facet:date` (volume over time — date
fields accept `day`, `week`, or `month` interval specifiers).

Facets need `--size` ≥ 1 — `--size 0` errors — and `--size` sets the **number of
buckets**, not rows. Expect noise in `siteName` buckets: aggregators, forums, and
mirrors rank alongside newsrooms, so read the top buckets before quoting them.

### Step 3 — probe before committing

```
~/.diffbot/venv/bin/db dql probe \
  'type:Article tags.label:"Anthropic" sortBy:date' \
  'type:Article tags.label:"Anthropic" categories.name:"Artificial Intelligence" sortBy:date' \
  'type:Article title:"Anthropic" sortBy:date'
```

Aim for a few hundred to a few thousand hits. Zero means the tag or category string is wrong — check the taxonomy or fall back to `text:`.

**Never probe an unfiltered `type:Article`** (or bare `has:` / `language:` filters over the whole corpus). The article index is large enough that these read-timeout.

`probe` fails the whole batch if any single variant is rejected by the API — fix the offending clause and re-run rather than assuming the others were checked.

### Step 4 — export and display

CSV for direct display:

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/news.csv \
  --spec "date.str,Date;title,Title;siteName,Publisher;sentiment,Sentiment;pageUrl,URL" --size 25
```

JSON when the results feed something else (`/diffbot-entities`, further `jq` slicing):

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/news.json --format json --size 25
```

Slice JSON before relaying it — never dump the raw file:

```bash
jq -r '.data[] | .entity | "\(.date.str)\t\(.siteName)\t\(.title)"' ~/.diffbot/tmp/news.json
```

**Display**

1. Render a markdown table: **Date | Headline | Publisher | Sentiment** with the headline linked to `pageUrl`.
2. Dates come back as `d2026-08-12T20:02:31` — strip the leading `d` and trim to the day unless the time matters.
3. Print the final DQL in a plain code block so the user can iterate.
4. Tell the user the saved file path, and offer more results (`--size N`, `--from K`) or a refinement.

To read one article in full, hand its `pageUrl` to `/diffbot-extract` rather than pulling `text` out of the export.
