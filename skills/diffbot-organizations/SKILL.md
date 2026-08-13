---
name: diffbot-organizations
description: "Search companies and organizations in the Diffbot Knowledge Graph by industry, headquarters, headcount, revenue, funding raised, ownership, or leadership — plus similarTo lookalike lists for competitor mapping. MUST USE skill when the answer is a list of companies: prospecting, market maps, competitor sets, or who-does-X. Returns companies as rows; when the rows should be transactions, investments, or deals, use diffbot-deals. Triggers on: find companies, list companies, company search, competitors, companies like, startups in, firms, vendors, suppliers, who makes, market map, prospect list, company lookup."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*), Bash(jq:*)
---

# Diffbot Organization Search

Find organizations in the Diffbot Knowledge Graph. This is `type:Organization` DQL with the company-research levers pre-selected: industry taxonomy, headquarters vs. offices, headcount and revenue bands, funding, and ownership.

**The organizations/deals boundary is the row shape.** If the rows the user wants are companies, this skill owns it — including "everything Microsoft acquired", which is a list of target companies. If the rows are transactions, investments, or deals, hand off to `/diffbot-deals`. Both filter on the same `acquiredBy` and `investments` fields; what differs is what ends up in the table.

Sibling skills: `/diffbot-news` (articles), `/diffbot-places` (geography), `/diffbot-deals` (deals as rows). Use `/diffbot-dql` for people, products, or anything outside these shapes.

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

Every query starts `type:Organization`. Layer the clauses below.

#### Industry — start here

`categories.name` is almost always the best first filter. Look up the exact string before using it; the taxonomy is title-cased and often plural (`"Semiconductor Companies"`, `"Artificial Intelligence Software"`).

```
~/.diffbot/venv/bin/db dql ontology taxonomy OrganizationCategory <regex>
```

```
type:Organization categories.name:"Semiconductor Companies" isPublic:true
```

When no category fits the niche, fall back to **`descriptors`** — short free-text capability tags:

```
type:Organization descriptors:"GPU"
type:Organization descriptors:"mexican restaurant" near(type:Organization name:"Diffbot")
```

#### Location — singular is headquarters, plural is any office

| Use | Meaning |
| --- | --- |
| `location.city.name:"Berlin"` | **Headquartered** in Berlin — the primary location |
| `locations.city.name:"Berlin"` | Has *an* office in Berlin, HQ anywhere |

Prefer the singular form for "companies in X". The same split applies to `name`/`allNames`, `description`/`allDescriptions`, `homepageUri`/`allUris`.

`location` is a `Location` composite: `.city.name`, `.region.name`, `.country.name`, `.subregion.name`, `.metroArea.name`, `.street`, `.postalCode`, `.latitude`, `.longitude`.

#### Field reference

| Field | Type | Notes |
| --- | --- | --- |
| `name` / `fullName` | String | Add `strict:` for exact match: `strict:name:"Apple Inc"` |
| `categories` | list | `categories.name` — OrganizationCategory taxonomy |
| `descriptors` | list of String | Free-text capability tags |
| `homepageUri` | URL | Primary domain |
| `nbEmployees` | Integer | Also `nbEmployeesMin`, `nbEmployeesMax`, `nbEmployeeRanges` |
| `revenue.value` / `.currency` | Amount | Also `yearlyRevenues`, `quarterlyRevenues` |
| `isPublic` | Boolean | |
| `ipo` | IPO composite | |
| `stock` | Stock composite | Ticker and exchange |
| `foundingDate` | DDate | `foundingDate>="2020-01-01"` |
| `ceo` | LinkedEntity (Person) | `ceo.name` |
| `founders` | list | `founders.name` |
| `investments` | list | `investments.investors.name`, `investments.series`, `investments.amount.value`, `investments.date` |
| `totalInvestment` | Amount | `totalInvestment.value>100000000` |
| `nbUniqueInvestors` | Integer | |
| `isAcquired` | Boolean | |
| `acquiredBy` | list | `acquiredBy.name` (acquirer), `acquiredBy.amount.value`, `acquiredBy.date` |
| `location` / `locations` | Location | See above |
| `nbLocations` | Integer | |

#### Matching a company by name — use `strict:`

`name:"…"` is a **contains** match, and company names are short and repetitive, so it
over-matches badly:

| Query | Hits |
| --- | --- |
| `type:Organization name:"Apple"` | 68,068 |
| `type:Organization strict:name:"Apple"` | 1,426 |
| `type:Organization strict:name:"Apple Inc."` | 1 |

When the user names a specific company, reach for `strict:` first and fall back to the
contains form only if it returns nothing. When they mean a *category* of company
("apple growers"), contains is correct — but prefer `categories.name` or `descriptors`
for that.

`strict:` still leaves duplicates: the KG holds several records for large companies
(subsidiaries, regional entities, stale dupes). Sort by `nbEmployees` or `importance`
and take the top row when you need "the" company.

#### `near` — companies within a radius of a place

Default radius 15km; override with `mi` or `km`. `near` resolves a single anchor
entity — if the inner query matches several, only the first is used.

```
type:Organization categories.name:"Semiconductor Companies" near(type:Place name:"Austin", 30mi)
type:Organization descriptors:"mexican restaurant" near(type:Organization name:"Diffbot")
```

Use this rather than `location.city.name` when the user says "near", "around", or
"within X miles" — city-name matching misses the surrounding metro.

#### `similarTo` — find companies like this one

Organization-only. Give it an anchor and it returns a ranked list of similar companies — the right tool for "competitors of X", "companies like X", or building a lookalike list.

```
type:Organization similarTo(name:"OpenAI")
type:Organization similarTo(type:Organization homepageUri:"walmart.com")
```

The anchor is a subquery: `name:"…"` is the short form, or use a fuller one like `type:Organization homepageUri:"…"` when the name is ambiguous.

**Other clauses compose and narrow within the similarity search** — they are not a post-filter on the top N, so adding a filter surfaces companies deeper in the ranking rather than just deleting rows:

```
type:Organization similarTo(name:"OpenAI") location.country.name:"United States"
type:Organization similarTo(name:"OpenAI") isPublic:true
```

**It behaves differently from a normal query in two ways:**

- It returns *exactly* `--size` results, ranked by similarity. The `hits` field mirrors the size you asked for, so there is no meaningful total — asking for more results just goes further down the ranking.
- **`db dql probe` cannot validate it.** Probe runs at `size=0`, and `similarTo` at `size=0` returns 0 — which looks like "no matches" but means nothing. Skip Step 3 for `similarTo` queries and validate with a small export (`--size 10`) instead.

#### Subqueries — co-constraining nested fields

Use `{}` when two conditions must hold on the *same* nested object:

```
type:Organization investments.{series:"Series A" date>="2026-01-01"}
```

Without `{}` those are independent — an org with *any* Series A and *any* 2026 round would match, even if they are different rounds. `{}` only works on composite-typed list fields.

#### Worked examples

```
type:Organization categories.name:"Semiconductor Companies" isPublic:true
type:Organization categories.name:"Artificial Intelligence Software" location.city.name:"San Francisco"
type:Organization investments.investors.name:"Sequoia Capital"
type:Organization nbEmployees>1000 revenue.value>1000000000
type:Organization isAcquired:true acquiredBy.name:"Microsoft"
type:Organization categories.name:"Artificial Intelligence Software" investments.{amount.value>50000000 date>="2026-01-01"}
type:Organization range:nbEmployees:10-100 location.country.name:"Germany" descriptors:"SaaS"
type:Organization similarTo(name:"OpenAI") location.country.name:"United States"
```

**Distribution questions** ("what industries dominate Berlin startups?") are facets, not row lists:

```
~/.diffbot/venv/bin/db dql export 'type:Organization location.city.name:"Berlin" facet:categories.name' \
  --out ~/.diffbot/tmp/facet.json --format json --size 25
```

Facets require `--size` ≥ 1 (`--size 0` errors), and `--size` sets the **number of buckets** returned, not rows.

### Step 3 — probe before committing

```
~/.diffbot/venv/bin/db dql probe \
  'type:Organization descriptors:"GPU" location.country.name:"United States"' \
  'type:Organization categories.name:"Semiconductor Companies" location.country.name:"United States"' \
  'type:Organization categories.name:"Semiconductor Companies" location.country.name:"United States" isPublic:true'
```

Zero hits usually means a mistyped category — re-check with `ontology taxonomy`. Note that `probe` fails the whole batch if any one variant is rejected by the API, so fix the bad clause and re-run.

**Do not probe `similarTo` queries** — probe runs at `size=0`, where `similarTo` always reports 0 regardless of how good the query is. Validate those with a small export instead.

### Step 4 — export and display

CSV for direct display:

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/orgs.csv \
  --spec "name,Company;descriptors,Description;nbEmployees,Employees;revenue.value,Revenue;location.city.name,City;location.country.name,Country;homepageUri,Website;isPublic,Public" \
  --size 50
```

JSON when results feed further analysis:

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/orgs.json --format json --size 50
```

`--spec` renders only the **primary** value of list/composite fields — one investor, one location. Export JSON if the user needs full lists.

**Display**

1. Render a markdown table sized to the question — company, one-line descriptor, headcount, HQ, website.
2. Numeric amounts come back in scientific notation (`1.0E8`); format them as `$100M` for the user.
3. Print the final DQL in a plain code block.
4. Tell the user the saved file path, and offer more rows (`--size N`, `--from K`) or a refinement.

For `similarTo` results, present them as a ranked list and say what the anchor was — the ordering is the answer, and there is no total count to report.
