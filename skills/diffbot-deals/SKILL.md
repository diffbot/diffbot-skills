---
name: diffbot-deals
description: "Search funding rounds, investments, and acquisitions in the Diffbot Knowledge Graph by date, deal size, round series, investor, acquirer, or industry — returns deals as rows: target, counterparty, amount, currency, date. MUST USE skill when the answer is a list of deals: deal flow, funding history for a company, or an investor's recent activity. When the rows should be companies instead (portfolio companies, everything Microsoft acquired), use diffbot-organizations. Triggers on: funding rounds, raised, Series A, venture funding, funding history, deal flow, deal size, investments in, acquisitions, M&A, acquired for, valuation round."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*), Bash(jq:*)
---

# Diffbot Deal Search

Find funding rounds, acquisitions, and transactions in the Diffbot Knowledge Graph. Deals live in two places — as standalone `Investment`/`Transaction` records, and as fields hanging off the `Organization` involved. **Choosing the right one is the whole skill**; see the routing table below.

**First, check the row shape.** This skill is for when the rows are deals — target, acquirer/investors, amount, date, series. If the rows the user wants are *companies* ("everything Microsoft acquired", "companies Sequoia backed"), hand off to `/diffbot-organizations`; it filters on the same `acquiredBy` and `investments` fields but presents companies.

Sibling skills: `/diffbot-organizations` (companies as rows), `/diffbot-news`, `/diffbot-places`. Use `/diffbot-dql` for anything outside these shapes.

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

### Step 2 — route the question

| The user asks about | Query | Why |
| --- | --- | --- |
| Funding rounds by date, size, series, or investor | `type:Investment` | One row per round, with amount, series, date, investors |
| Deals in an **industry / location / company-size** segment | `type:Organization` + `investments.{...}` | Industry lives on the company, not the deal — see the gap below |
| Acquisitions ("who bought X", "everything Microsoft acquired") | `type:Organization isAcquired:true acquiredBy.name:"…"` | `Acquisition` records are name-only stubs |
| Any money movement, not just equity | `type:Transaction` | Superset: `Investment` and `Acquisition` are both subtypes |

#### The industry gap — read this before filtering deals by sector

`investee` on an `Investment` is a `LinkedEntity`, which carries only `name`, `types`, `summary`, `image`, `diffbotUri`. It has **no `categories`**, so `investee.categories.name:"…"` returns zero — it looks like "no such deals" rather than "no such field."

Flip the query to the company side instead, and use `{}` so the round's conditions co-constrain:

```
type:Organization categories.name:"Artificial Intelligence Software" investments.{amount.value>50000000 date>="2026-01-01"}
type:Organization categories.name:"Artificial Intelligence Software" investments.{series:"Series A" date>="2026-01-01"}
```

Without `{}` the clauses are independent — a company with *any* $50M round and *any* 2026 round matches, even if they're different rounds.

### Step 3 — field reference

**`type:Investment`** — a funding round.

| Field | Type | Notes |
| --- | --- | --- |
| `investee` | LinkedEntity (Organization) | `investee.name` — the company raising |
| `investment.series` | String | `"Series A"`, `"Series B"`, `"Series Unknown"`, … |
| `investment.amount.value` | Float | Raw number; pair with `.currency` |
| `investment.amount.currency` | String | `"USD"`, … — **always filter or display currency**, values are not normalized |
| `investment.date` | DDate | `investment.date>="2026-01-01"` |
| `investment.investors` | list of LinkedEntity | `investment.investors.name` |
| `date`, `name`, `amount` | | Inherited from `Transaction`; `date` mirrors `investment.date` |

**`type:Transaction`** — any transaction; `Investment` and `Acquisition` are subtypes (filter with `types:"Acquisition"`).

| Field | Notes |
| --- | --- |
| `payee` | LinkedEntity (Organization) — receiving side |
| `payers` | list of LinkedEntity — paying side |
| `amount.value` / `amount.currency` | |
| `date` | DDate |
| `name` | e.g. `"Venture Round - OpenAI"` |

**`Organization.acquiredBy`** — the reliable path for M&A.

| Field | Notes |
| --- | --- |
| `acquiredBy.name` | The acquirer |
| `acquiredBy.amount.value` | Deal size |
| `acquiredBy.date` | |
| `isAcquired` | Boolean flag on the target |

Also on Organization: `investments` (full round history), `totalInvestment.value`, `nbUniqueInvestors`.

**Sorting.** There *is* a useful default: unsorted, `investment.investors.name:"Sequoia
Capital"` returns the headline rounds (OpenAI $122B, Anthropic $50B, OpenAI $40B),
whereas `revSortBy:investment.date` returns whatever closed most recently regardless of
size. Leave the sort off unless the ordering is the question, then use:

```
revSortBy:investment.date        # newest rounds first
revSortBy:investment.amount.value # largest rounds first
```

#### Worked examples

```
type:Investment investment.investors.name:"Sequoia Capital" revSortBy:investment.date
type:Investment investment.series:"Series A" investment.date>="2026-01-01" revSortBy:investment.amount.value
type:Investment investment.amount.value>100000000 investment.amount.currency:"USD" revSortBy:investment.date
type:Investment investee.name:"OpenAI" revSortBy:investment.date
type:Organization isAcquired:true acquiredBy.name:"Microsoft" revSortBy:acquiredBy.amount.value
type:Organization categories.name:"Semiconductor Companies" investments.{amount.value>100000000 date>="2025-01-01"}
type:Transaction types:"Acquisition" sortBy:date
```

**Note on `type:Acquisition`.** These records exist (~209k) but are near-empty stubs — typically just a `name` like `"Reliance Motor Car Company acquired by General Motors"`, with `date`, `amount`, `payee`, and `payers` all null. Don't build a deal table from them; route acquisitions through `Organization.acquiredBy`.

#### Distribution questions are facets, not row lists

"What stage is most funding at?", "which investors are most active?" — aggregate
instead of listing:

```
~/.diffbot/venv/bin/db dql export 'type:Investment investment.date>="2026-01-01" facet:investment.series' \
  --out ~/.diffbot/tmp/facet.json --format json --size 12
```

Returns buckets like `Seed 4568 · Grant 3796 · Series A 2061 · Debt Financing 2015 ·
Pre Seed 1965`. Also useful: `facet:investment.investors.name` (most active
investors), `facet:investment.amount.value` (auto-bucketed deal sizes).

Facets need `--size` ≥ 1 — `--size 0` errors — and `--size` sets the **number of
buckets**, not rows. A facet response has `value`/`count` per bucket, not entities,
so don't use it when the user wants individual deals.

**`or()` is usually unnecessary on `series`.** `investment.series:"Series A"` is a
contains match and already covers `"Series A-1"`; `or("Series A","Series A-1")`
returns the identical count. Reach for `or()` only across genuinely different
strings.

### Step 4 — probe before committing

```
~/.diffbot/venv/bin/db dql probe \
  'type:Investment investment.series:"Series A" investment.date>="2026-01-01"' \
  'type:Investment investment.amount.value>100000000' \
  'type:Organization categories.name:"Artificial Intelligence Software" investments.{amount.value>50000000 date>="2026-01-01"}'
```

Zero hits on an `investee.<something>` path almost always means the field doesn't exist on `LinkedEntity` — re-read the gap above rather than loosening the filter. `probe` fails the whole batch if any one variant is rejected by the API, so fix the bad clause and re-run.

### Step 5 — export and display

Rounds:

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/deals.csv \
  --spec "investee.name,Company;investment.series,Round;investment.amount.value,Amount;investment.amount.currency,Currency;investment.date.str,Date;investment.investors.name,Lead Investor" \
  --size 50
```

Acquisitions:

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/acquisitions.csv \
  --spec "name,Target;acquiredBy.name,Acquirer;acquiredBy.amount.value,Amount;acquiredBy.date.str,Date;categories.name,Industry" \
  --size 50
```

Export JSON when the full investor list matters — `--spec` renders only the **primary** value of a list field, so the CSV shows one investor even when a round had thirty:

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/deals.json --format json --size 50
jq -r '.data[].entity | "\(.investment.date.str)\t\(.investee.name)\t\(.investment.series)\t\([.investment.investors[]?.name] | join(", "))"' ~/.diffbot/tmp/deals.json
```

**Display**

1. Render a markdown table: **Date | Company | Round | Amount | Investors**.
2. **Reformat amounts.** CSV emits scientific notation (`3.0E8`) — show `$300M`. Never present a bare number without its currency.
3. Dates come back as `d2026-07-23` — strip the leading `d`.
4. Blank amount means the round was reported without a disclosed size — label it "undisclosed", not `0`.
5. `"Series Unknown"` is a real value in the data, not a lookup failure.
6. Print the final DQL in a plain code block, give the saved file path, and offer more rows (`--size N`, `--from K`) or a refinement.
