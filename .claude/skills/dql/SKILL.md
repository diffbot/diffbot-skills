---
name: dql
description: "Query the Diffbot Knowledge Graph using DQL (Diffbot Query Language). Use when the user wants to search for organizations, people, or articles in the Diffbot KG. Triggers on: search diffbot, query knowledge graph, dql search, find companies, find news articles, find people, latest news"
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*)
---

# Diffbot Knowledge Graph Search (DQL)

Query the Diffbot Knowledge Graph via the DQL API. Translate the user's plain-text request into a DQL query, execute it through the `db dql` CLI, and display formatted results.

## The `db dql` CLI

All work in this skill is driven by the `db` CLI from the [`diffbot-python`](file://~/Diffbot/diffbot-python) library. It owns token loading, URL encoding, HTTP, ontology lookup, and parallel probing.

**The skill runs the CLI from a dedicated virtualenv it owns at `~/.diffbot/venv`** — it does not assume `db` is on `PATH` or that any other venv exists. The Step 1 bootstrap creates the venv and installs the library if missing. **Always invoke with the fixed path `~/.diffbot/venv/bin/db`** — never bare `db` and never another venv's `db`, so the permission allow rule matches and no `PATH` assumption is made. Throughout this document `db` is shorthand for `~/.diffbot/venv/bin/db`; expand it to the full path in every actual bash command.

```
~/.diffbot/venv/bin/db dql init                              # refresh ontology cache; check credentials
~/.diffbot/venv/bin/db dql ontology types
~/.diffbot/venv/bin/db dql ontology composites
~/.diffbot/venv/bin/db dql ontology enums
~/.diffbot/venv/bin/db dql ontology taxonomies
~/.diffbot/venv/bin/db dql ontology fields  <Type> [regex]   # entity-type or composite fields
~/.diffbot/venv/bin/db dql ontology taxonomy <Name> [regex]  # taxonomy values (recurses children)
~/.diffbot/venv/bin/db dql ontology enum    <Name>           # enum values
~/.diffbot/venv/bin/db dql ontology search  <regex>          # fallback: any 'name' anywhere in the ontology
~/.diffbot/venv/bin/db dql probe "<Q1>" "<Q2>" ...           # parallel hit counts for variants (size=0)
~/.diffbot/venv/bin/db dql export "<DQL>" --out <outfile> [--format csv|xls|xlsx|json] [--spec "name,Name;..."] [--size N] [--from K]
```

`export --out <file>` writes the API response straight to a file; without `--out` it prints a formatted table to stdout. All other commands write to stdout. Errors go to stderr with non-zero exit codes.

Prefer `--out <file>` over stdout for anything but tiny result sets: use `probe` to validate selectivity, then `export --out` to commit the full payload to disk — and only then. Pulling full data into the conversation for exploration burns tokens for no gain.

## Workflow

### Step 1 — bootstrap + `db dql init`

First ensure the venv exists and the library is installed, then run `init`. Guard the venv creation so it only runs when the venv is missing — re-running `python3 -m venv` on an existing venv overwrites activation scripts and fails if any are read-only:

```
[ -d ~/.diffbot/venv ] || python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install -q -e ~/Diffbot/diffbot-python
~/.diffbot/venv/bin/db dql init
```

`init` refreshes `~/.diffbot/ontology.json`, resets `~/.diffbot/tmp/`, and verifies a token is available. The token is read from the `DIFFBOT_API_TOKEN` environment variable if set, otherwise from `~/.diffbot/credentials`. If neither is present the user must run:

```
echo "DIFFBOT_API_TOKEN=YOUR_TOKEN_HERE" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials
```

Tokens are available at https://app.diffbot.com/get-started/. The CLI loads the token itself — never echo it.

### Step 2 — Construct and validate the DQL query

Translate the natural-language request into a DQL string. Examples:

```
type:Organization name:"Diffbot"
type:Product site:"ikea.com"
type:Organization location.city.name:"San Francisco" investments.investors.name:"Andreessen Horowitz"
type:Article categories.name:"War and Conflicts" tags.label:"Ethiopia" date>="2020-11-01" date<="2022-11-30" sortBy:date
type:Article quotes.speaker:"Donald Trump" sortBy:date
```

Every DQL string starts with `type:`. Start with common types (`Organization`, `Person`, `Article`, `Product`) and reach for a more specific entity type via `dql ontology types` if those don't fit.

**Look up fields before using them.** Independent ontology lookups should be issued as parallel Bash tool calls in a single Claude message so they don't queue.

```
~/.diffbot/venv/bin/db dql ontology fields Organization location     # entity-type fields, regex-filtered
~/.diffbot/venv/bin/db dql ontology fields Location                  # composite fields
~/.diffbot/venv/bin/db dql ontology taxonomy OrganizationCategory semiconductor
~/.diffbot/venv/bin/db dql ontology enum Language
~/.diffbot/venv/bin/db dql ontology search asset                     # fallback when you don't know where a field lives
```

`dql ontology fields` accepts both entity-type names (e.g. `Organization`) and composite names (e.g. `Location`, `Employment`) — it auto-routes. Output format: `<name>: [<type>] [isList] [isComposite] [isEnum]`.

**Operators**

| Operator             | Syntax                 | Example                                                                  |
| -------------------- | ---------------------- | ------------------------------------------------------------------------ |
| Contains (string)    | `field:"value"`        | `name:"Diffbot"`                                                         |
| Regex                | `re:field:"pattern"`   | `re:name:"^Apple"`                                                       |
| Exact match          | `strict:field:"value"` | `strict:name:"Apple Inc"`                                                |
| Greater than         | `field>N`              | `nbEmployees>500`                                                        |
| Less than            | `field<N`              | `nbEmployees<10000`                                                      |
| Not equals           | `field!=value`         | `gender!="MALE"`                                                         |
| Max                  | `max:field:N`          | `max:capitalization.value:1000000`                                       |
| Min                  | `min:field:N`          | `min:capitalization.value:1000000`                                       |
| Range                | `range:field:N-M`      | `range:nbEmployees:10-100`                                               |
| AND (implicit)       | space-separated        | `type:Organization isPublic:true`                                        |
| OR                   | `or(v1,v2)`            | `categories.name:or("Software companies","Hardware companies")`          |
| NOT                  | `not(condition)`       | `not(isPublic:true)`, `not(has:parentCompany)`                           |
| Near (proximity)     | `near(name:"Place")`   | `near(name:"San Francisco", 10mi)`                                       |
| Similar to           | `similarTo(…)`         | `similarTo(type:Organization homepageUri:"walmart.com")`                 |
| Has (field exists)   | `has:field`            | `has:sicClassification`                                                  |
| Get (include fields) | `get:field`            | `has:subsidiaries get:subsidiaries`                                      |
| Get (exclude fields) | `get:!field`           | `get:!nbEmployeesMax,!phoneNumbers`                                      |
| Facet (aggregate)    | `facet:field`          | `facet:locations.city.name`                                              |
| Facet with ranges    | `facet[a:b,b:c]:field` | `facet[100:500,500:1000]:nbEmployees`                                    |
| Facet with values    | `facet["a","b"]:field` | `facet["Austin","Seattle"]:locations.city.name`                          |
| Sort ascending       | `sortBy:field`         | `sortBy:nbEmployees`                                                     |
| Sort descending      | `revSortBy:field`      | `revSortBy:nbEmployees`                                                  |

**Subquery syntax for nested fields**

Use `{}` to co-constrain multiple conditions on the same nested object:

```
type:Person employments.{employer.name:"Diffbot" isCurrent:true}
```

Without `{}` the two conditions are independent (matches a person with *any* Diffbot employment AND *any* current employment — possibly different ones). Subqueries only work on composite-typed list fields; check the ontology to confirm. Attempting `{}` on a non-nested field returns: `Nested expression over non-nested list field [...] is not allowed`.

**Singular vs plural fields (primary vs all/historical)**

Many entity types expose both a singular and plural form of the same composite field. The singular form is the primary/current value; the plural is the full list including historical entries.

| Singular (primary) | Plural (all/historical) |
| ------------------ | ----------------------- |
| `location`         | `locations`             |
| `name`             | `allNames`              |
| `description`      | `allDescriptions`       |
| `homepageUri`      | `allUris`               |

Prefer the singular form when you want to filter on the org's *primary* fact. Example: to find companies headquartered in the US, use `location.country.name:"United States"` — not `locations.country.name:"United States"`, which matches any org with a US office (even foreign-headquartered companies with a US branch). Using the singular field is also cleaner than a `locations.{country.name:"United States" isPrimary:true}` subquery.

**regex operator**
Regex is slow and compute heavy. Avoid if possible. If to be used, stick to short, simple, and speedy regex matches.

**similarTo operator** _(Organization only)_

```
type:Organization similarTo(name:"OpenAI")
```

**near operator**

Finds entities within a given distance of a Place (default 15km; specify with `mi` or `km`). `near` operates on a single entity — if the subquery returns multiple, only the first is used.

```
type:Organization near(type:Place name:"San Francisco")
type:Organization descriptors:"mexican restaurant" near(type:Organization name:"Diffbot")
```

**get operator**

`get:<field,field2>` restricts response payload to specified fields (and descendants). Mostly relevant inside an exported payload — for testing query shape, use `dql probe` (hits only, no entity data).

**Facet queries**

Use facets for aggregation/distribution questions ("what industries are common among Berlin startups?", "how are employees distributed across company sizes?"). A facet response has `value`, `count`, and `callbackQuery` per bucket — *not* `entity` records. Not appropriate when the user wants individual entity rows.

- Numeric/date fields are auto-bucketed; override with `facet[a:b,b:c]:field`
- Date fields accept `day`, `week`, or `month` interval specifiers
- Restrict to specific values with `facet["v1","v2"]:field`

See [Facet Queries](https://docs.diffbot.com/docs/facet-queries.md) for full syntax.

#### Entity-Specific Tips

**Article**
 - `type:Article categories.name"<category name>"` is a great way to narrow down articles by topic. Use ontology taxonomy to look up the category names.
 - `type:Article tags.label:"<entity name>"` refines an article query by mentioned entities. There is no exhaustive list of tag values — they are simply entity names that may or may not appear in the KG. If `tags.label` is too restrictive, fall back to `text:` matching.
 - Unless otherwise stated, always end article queries with `sortBy:date`, which sorts the articles from newest to oldest.

**Organization**
 - `categories.name` is usually an excellent starting point for crafting organization DQL

### Step 3 — Probe variants in parallel before committing

Before running the final query, probe candidate variants for hit counts to verify the query is well-shaped (not too broad, not too narrow). Use `dql probe` — it fires all variants concurrently:

```
~/.diffbot/venv/bin/db dql probe \
  'type:Organization descriptors:"GPU" location.country.name:"United States"' \
  'type:Organization descriptors:"GPU" location.country.name:"United States" categories.name:"Semiconductor Companies"' \
  'type:Organization descriptors:"GPU" location.country.name:"United States" isPublic:true'
```

Output is a sorted text table of hit counts; add `--json` for machine-readable. This is the right way to test query selectivity — far faster than running them serially.

### Step 4 — Export and display

**Choose format based on intent:**

- **Further analysis** (piping to `jq`, passing text to the entities skill, feeding another tool): export as **JSON**.
- **Final display to user** (markdown table, no downstream processing): export as **CSV**.

**JSON export** (use when results will be piped or analyzed further):

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/<filename>.json --format json --size N
```

JSON payloads are easy to slice with `jq` before passing to other tools:

```bash
# To get all the keys available to you in the DQL export
  jq '[.data[0].entity | path(..)] | map(join(".")) | unique' ~/.diffbot/tmp/<filename>.json
```

Refrain from reading `text` or `content` from type:Article DQL exports directly. `summary` may be more appropriate.

**CSV export** (use when presenting a table directly to the user):

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/<filename>.csv \
  --spec "name,Name;nbEmployees,Employees;homepageUri,Website;location.city.name,City;location.region.name,State;isPublic,Public"
```

`--spec` notes:
- Format is `<field-path>,<Display Name>` per pair, `;`-separated
- Use lowercase field paths (`name`, not `Name`) — the first token is the actual DQL field path
- For list/composite fields, only the primary value is rendered

**Final display**

1. Always print the final DQL string in a plain code block so the user can copy/iterate.
2. Tell the user the saved file path.
3. For CSV: read and render as a markdown table with columns appropriate to the entity type.
4. Offer pagination (`--size N`, `--from K`) or query refinement.

## Performance discipline

- **One ontology lookup per Bash tool call is wasteful.** When you need to inspect multiple fields/types, issue parallel Bash tool calls in the *same* Claude message — they execute concurrently.
- **Never serial-loop curls in a shell `for` loop.** Use `dql probe` (which parallelizes internally) for any N-variant hit-count check.
- **Don't re-`dql init` mid-session.** The ontology is cached on disk and in-process; init once at the start.
