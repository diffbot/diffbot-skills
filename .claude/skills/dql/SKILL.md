---
name: dql
description: "Query the Diffbot Knowledge Graph using DQL (Diffbot Query Language). Use when the user wants to search for organizations, people, or articles in the Diffbot KG. Triggers on: search diffbot, query knowledge graph, dql search, find companies in diffbot, diffbot lookup, kg search."
allowed-tools: Bash(.claude/skills/dql/scripts/dql:*)
---

# Diffbot Knowledge Graph Search (DQL)

Query the Diffbot Knowledge Graph via the DQL API. Translate the user's plain-text request into a DQL query, execute it through the `dql` CLI, and display formatted results.

## The `dql` CLI

All work in this skill is driven by one tool: `.claude/skills/dql/scripts/dql`. It is a small Python CLI that owns token loading, URL encoding, HTTP, ontology lookup, and parallel probing — keeping the call site free of shell expansion (no `$`, no `~`, no `$(...)`, no pipes) so permissions stay clean and tool-call overhead stays minimal.

**Always invoke with the relative path `.claude/skills/dql/scripts/dql` from the project root.** Never use the absolute form (`/home/<user>/.../scripts/dql`) — the permission allow rule only matches the relative prefix, so absolute invocations will prompt. Throughout this document `dql` is shorthand for `.claude/skills/dql/scripts/dql`; expand it to the relative form in every actual bash command.

```
.claude/skills/dql/scripts/dql init                              # refresh ontology cache; check credentials
.claude/skills/dql/scripts/dql ontology types
.claude/skills/dql/scripts/dql ontology composites
.claude/skills/dql/scripts/dql ontology enums
.claude/skills/dql/scripts/dql ontology taxonomies
.claude/skills/dql/scripts/dql ontology fields  <Type> [regex]   # entity-type or composite fields
.claude/skills/dql/scripts/dql ontology taxonomy <Name> [regex]  # taxonomy values (recurses children)
.claude/skills/dql/scripts/dql ontology enum    <Name>           # enum values
.claude/skills/dql/scripts/dql ontology search  <regex>          # fallback: any 'name' anywhere in the ontology
.claude/skills/dql/scripts/dql probe "<Q1>" "<Q2>" ...           # parallel hit counts for variants (size=0)
.claude/skills/dql/scripts/dql export "<DQL>" <outfile> [--format csv|xls|xlsx|json] [--spec "name,Name;..."] [--size N] [--from K]
```

`export` writes the API response straight to a file; all other commands write to stdout. Errors go to stderr with non-zero exit codes.

There is deliberately no "execute query and print JSON" command. Use `probe` to validate selectivity, then `export` to commit to the full payload — and only then. Pulling full data into the conversation for exploration burns tokens for no gain.

## Workflow

### Step 1 — `dql init`

```
.claude/skills/dql/scripts/dql init
```

Refreshes `~/.diffbot/ontology.json`, resets `~/.diffbot/tmp/`, and verifies `~/.diffbot/credentials` exists. If credentials are missing the user must run:

```
echo "token=YOUR_TOKEN_HERE" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials
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
.claude/skills/dql/scripts/dql ontology fields Organization location     # entity-type fields, regex-filtered
.claude/skills/dql/scripts/dql ontology fields Location                  # composite fields
.claude/skills/dql/scripts/dql ontology taxonomy OrganizationCategory semiconductor
.claude/skills/dql/scripts/dql ontology enum Language
.claude/skills/dql/scripts/dql ontology search asset                     # fallback when you don't know where a field lives
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
 - `type:Article tags.label:"<entity name>"` refines an article query by mentioned entities. There is no exhaustive list of tag values — they are simply entity names that may or may not appear in the KG. If `tags.label` is too restrictive, fall back to `text:` matching.

**Organization**
 - `categories.name` is usually an excellent starting point for crafting organization DQL

### Step 3 — Probe variants in parallel before committing

Before running the final query, probe candidate variants for hit counts to verify the query is well-shaped (not too broad, not too narrow). Use `dql probe` — it fires all variants concurrently:

```
.claude/skills/dql/scripts/dql probe \
  'type:Organization descriptors:"GPU" location.country.name:"United States"' \
  'type:Organization descriptors:"GPU" location.country.name:"United States" categories.name:"Semiconductor Companies"' \
  'type:Organization descriptors:"GPU" location.country.name:"United States" isPublic:true'
```

Output is a sorted text table of hit counts; add `--json` for machine-readable. This is the right way to test query selectivity — far faster than running them serially.

### Step 4 — Export and display

Once `probe` confirms a query is well-shaped, commit to a CSV export. CSV is the canonical output format — it's compact, trivially turned into a markdown table, and avoids pulling the full entity payload into the conversation.

```
.claude/skills/dql/scripts/dql export "<DQL>" /home/<user>/.diffbot/tmp/<filename>.csv \
  --spec "name,Name;nbEmployees,Employees;homepageUri,Website;location.city.name,City;location.region.name,State;isPublic,Public"
```

`exportspec` notes:
- Format is `<field-path>,<Display Name>` per pair, `;`-separated
- Use lowercase field paths (`name`, not `Name`) — the first token is the actual DQL field path
- For list/composite fields, only the primary value is rendered

If a non-tabular shape is genuinely needed (e.g. inspecting one entity's full structure), use `.claude/skills/dql/scripts/dql export "<DQL>" /home/<user>/.diffbot/tmp/<filename>.json --format json --size 1` so the payload still lands in a file rather than the conversation.

**Final display**

1. Always print the final DQL string in a plain code block so the user can copy/iterate.
2. Tell the user the saved file path.
3. Read the CSV and render it as a markdown table with columns appropriate to the entity type (e.g. Organization: Name, Employees, Location, Website).
4. Offer pagination (`--size N`, `--from K`) or query refinement.

## Performance discipline

- **One ontology lookup per Bash tool call is wasteful.** When you need to inspect multiple fields/types, issue parallel Bash tool calls in the *same* Claude message — they execute concurrently.
- **Never serial-loop curls in a shell `for` loop.** Use `dql probe` (which parallelizes internally) for any N-variant hit-count check.
- **Don't re-`dql init` mid-session.** The ontology is cached on disk and in-process; init once at the start.
