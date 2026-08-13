---
name: diffbot-people
description: "Search people in the Diffbot Knowledge Graph by job title, employer, employer industry, skills, education, location, or nationality. Covers people with a public online professional presence only — not a people-finder for private individuals. MUST USE skill when the answer is a list of people: executives at a company, alumni of a school, who holds a role, or who has a skill. Returns people as rows; for the companies themselves use diffbot-organizations. Triggers on: find people, who works at, executives at, employees of, CEO of, CTO of, leadership team, alumni of, people who studied, people with skill, board members, who founded."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*), Bash(jq:*)
---

# Diffbot People Search

Find people in the Diffbot Knowledge Graph. This is `type:Person` DQL with the
people-research levers pre-selected: employment history, employer industry,
education, skills, and location.

**Coverage is limited to people with a public online presence** — see the note at the
end before reporting an empty or partial result.

**Row shape decides the skill.** If the rows are people, this skill owns it —
including "who runs Nvidia". If the rows are companies ("companies whose CEO is
a woman"), use `/diffbot-organizations`. Sibling skills: `/diffbot-news`,
`/diffbot-places`, `/diffbot-deals`. Use `/diffbot-dql` for anything outside
these shapes.

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

### Step 2 — the subquery rule comes first

`employments` is a **list** of jobs. Conditions written separately are matched
against *different* jobs, which silently inflates results. Co-constrain them
with `{}`:

```
✗ type:Person employments.{title:"Chief Executive Officer" isCurrent:true} employments.employer.categories.name:"Semiconductor Companies"
✓ type:Person employments.{title:"Chief Executive Officer" isCurrent:true employer.categories.name:"Semiconductor Companies"}
```

Measured: **3,457 hits vs 399**. The loose form matches anyone who was ever a CEO
*somewhere* and also worked at *some* semiconductor company — a different job.
Nearly 9 out of 10 of those rows are wrong.

**Put every condition about one job inside one `{}`.** The same applies to
`educations`, `colleagues`, and `locations`.

Add `isCurrent:true` whenever the user means the present ("who runs X", "current
CTO"); omit it for history ("everyone who has worked at X").

### Step 3 — the levers

#### Employer industry resolves — this is the headline capability

`employments.employer` is a full `Organization` link, so you can filter people by
their employer's industry, size, or location:

```
type:Person employments.{title:"Chief Technology Officer" isCurrent:true employer.categories.name:"Biotechnology Companies"}
type:Person employments.{isCurrent:true employer.location.country.name:"Germany" employer.nbEmployees>1000}
```

Look up category strings first — they are title-cased and usually plural:
`~/.diffbot/venv/bin/db dql ontology taxonomy OrganizationCategory <regex>`

(Contrast with `/diffbot-deals`, where `investee` is a bare `LinkedEntity` with no
categories. The employer link is richer — the deals trap does not apply here.)

#### Field reference

| Field | Type | Notes |
| --- | --- | --- |
| `name` / `allNames` | String | `nameDetail.firstName`, `.lastName`, `.nicknames` |
| `employments` | list | `.title`, `.employer.name`, `.isCurrent`, `.from`, `.to`, `.description`, `.location`, `.categories.name` (EmploymentCategory taxonomy), `.technologies.name` |
| `educations` | list | `.institution.name`, `.major.name`, `.degree.name`, `.isCurrent`, `.hasDroppedOut`, `.from`, `.to` |
| `skills` | list | `skills.name` — free-form skill entities |
| `location` / `locations` | Location | Singular is primary residence; same HQ-vs-offices split as Organization |
| `nationalities` | list | `nationalities.name` |
| `gender` | enum | `gender:"Female"` works; `gender.normalizedValue:"Female"` is equivalent. Values: Male, Female, Transgender_male, Transgender_female, Bigender, Agender, Trigender, Other |
| `age`, `birthDate`, `deathDate` | | `birthPlace`, `deathPlace` are Location composites |
| `netWorth.value` | Amount | See the caveat below |
| `awards` | list | `awards.title`, `awards.date` |
| `colleagues` | list | `.colleague.name`, `.relationship`, `.isCurrent` |
| `parents`, `children`, `siblings`, `unions` | list | Family graph |
| `politicalAffiliation` | list | Linked Organization |
| `importance` | Float | Prominence — the best general "most notable first" sort |
| `wikipediaPageviews` | Integer | Attention proxy, with quarter/year and growth variants |
| `linkedInUri`, `twitterUri`, `githubUri`, `crunchbaseUri`, `homepageUri` | URL | |
| `emailAddresses`, `phoneNumbers` | list | Sparse |

`type:PersonInvestor` (~57k) is a narrower type for angels and individual investors.

**Leave the sort off unless the user asked for an ordering.** The default ranking
already bakes in relevance and prominence, and an explicit sort overrides it — usually
for the worse. Measured: `homepageUri:"openai.com"` unsorted returns **OpenAI**, while
`revSortBy:nbEmployees` returns *"OpenAI for Developers"*; `anthropic.com` unsorted
returns **Anthropic**, sorted returns *"Claude Builder Club"*.

Add a sort only when the ordering *is* the question — "largest cities by population",
"most recent rounds", "biggest acquisitions". (Articles are the exception: see
`/diffbot-news`, where `sortBy:date` is the default.)

For people specifically: `strict:name:"Jensen Huang"` unsorted returns the records in
descending `importance` order already (97.2, then 13.6, then 10.1) — the Nvidia CEO
first, without asking for it.

#### Worked examples

```
type:Person employments.{employer.name:"Nvidia" isCurrent:true}
type:Person employments.{title:"Chief Executive Officer" isCurrent:true employer.categories.name:"Semiconductor Companies"}
type:Person educations.{institution.name:"Stanford University" major.name:"Computer Science"}
type:Person skills.name:"Machine Learning" location.city.name:"San Francisco"
type:Person gender:"Female" employments.{title:"Chief Executive Officer" isCurrent:true}
type:Person nationalities.name:"France" netWorth.value>1000000000 revSortBy:netWorth.value
```

### Step 4 — probe before committing

```
~/.diffbot/venv/bin/db dql probe \
  'type:Person employments.{employer.name:"Anthropic" isCurrent:true}' \
  'type:Person employments.{employer.name:"Anthropic" isCurrent:true title:"Engineer"}'
```

**Compare the `{}` and non-`{}` forms when a query has two or more employment
conditions.** A large gap means the loose form is matching across different jobs
and the subquery is required. `probe` fails the whole batch if any variant is
rejected, so fix the bad clause and re-run.

### Step 5 — export and display

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/people.csv \
  --spec "name,Name;employments.title,Title;employments.employer.name,Employer;location.city.name,City;linkedInUri,LinkedIn" \
  --size 50
```

**Display**

1. Render a markdown table — name, title, employer, location.
2. Print the final DQL in a plain code block, give the saved file path, and offer
   more rows (`--size N`, `--from K`) or a refinement.

## Traps

- **`--spec` renders the primary employment, not the matched one.** This is the trap
  most likely to make you report something false. Querying Tesla's founders returns the
  right *people* but the CSV shows their current jobs:

  | Name | Employer (as rendered) |
  | --- | --- |
  | Elon Musk | Neuralink |
  | Martin Eberhard | INEVIT |
  | JB Straubel | QuantumScape |

  All three genuinely co-founded Tesla; none of those employers is Tesla. Don't present
  the rendered employer as the matched one. Export JSON and pick the right entry:
  ```bash
  jq -r '.data[].entity | .name as $n | .employments[] | select(.employer.name|test("Tesla")) | "\($n)\t\(.title)\t\(.employer.name)"' ~/.diffbot/tmp/people.json
  ```
- **`descriptors` is effectively unpopulated on Person** (`descriptors:"venture
  capitalist"` → 0 hits), unlike Organization where it is a good fallback. Use
  `employments.title`, `skills.name`, or `summary` instead.
- **`netWorth` has extreme outliers** — the top of `revSortBy:netWorth.value`
  includes obviously bad values (a $96T record) and historical figures like Mansa
  Musa. Sanity-check the top rows before presenting, and prefer a bounded range.
- **Titles are free text, and the abbreviation is not a substring of the long form.**
  `title:"Chief Executive Officer"` → 521,798 current holders; adding the
  abbreviation, `title:or("Chief Executive Officer","CEO")` → **2,620,747**. Five
  times as many, and dropping them is a silent under-count, not an error. Always
  `or()` the abbreviation with the spelled-out form for C-suite roles (CEO, CTO, CFO,
  COO, CIO), and probe both. Note this is the opposite of a field like
  `investment.series`, where `"Series A"` already contains `"Series A-1"` and `or()`
  changes nothing — `or()` earns its keep only when the spellings genuinely differ.
- **Board membership is titled "Director", not "Board Member".** At Nvidia,
  `title:"Board Member"` finds **5** people; `title:or("Board Member","Board of
  Directors","Director")` finds **904**. Never answer a board question with the naive
  string — it under-counts by two orders of magnitude. ("Founder" is the happy
  opposite: it is a substring of "Co-Founder", so it catches both without `or()`.)
- **For the CEO or founders of one specific named company, don't scan Person — read the
  Organization.** It is a curated field and far cleaner than title matching, which drags
  in same-named companies (a Person scan for Tesla founders surfaced the *band* Tesla's
  guitarist). Note `get:` is required — these fields are absent from the default payload:
  ```
  ~/.diffbot/venv/bin/db dql export 'type:Organization homepageUri:"tesla.com" get:name,ceo,founders' --out ~/.diffbot/tmp/f.json --format json --size 1
  ```
  Returns `ceo=Elon Musk`, `founders=JB Straubel, Martin Eberhard, Ian Wright, Marc
  Tarpenning, Elon Musk`.

  **Match on `homepageUri`, not `name`, and do not sort.** Both alternatives fail:
  `strict:name:"Apple"` never matches the real company (its canonical name is
  "Apple Inc."), and adding `revSortBy:nbEmployees` returns *"OpenAI for Developers"*
  for openai.com and *"Claude Builder Club"* for anthropic.com. The domain plus the
  default relevance ranking is correct for all of apple.com, tesla.com, openai.com,
  anthropic.com, airbnb.com, nvidia.com, and stripe.com.

  Use `/diffbot-people` when the rows are people matching a *pattern*; use this when you
  want one company's known leadership.
- **Matching a specific person by name — use `strict:`.** `name:"…"` is a contains
  match, so a common name pulls in every partial hit. `strict:name:"Jensen Huang"`
  pins it. Person records also duplicate, so expect several rows for one individual.
- **Person records duplicate.** Same-name rows with different employers may be
  distinct people or the same person twice — say which when it matters.

## Coverage — public presence only

The Knowledge Graph is built from the public web, so this skill sees people who have a
public professional footprint: company pages, bylines, filings, conference listings,
profiles they chose to publish. It does not surface people who have not put themselves
online, and it is not a people-finder.

Two things follow, and both change how you report results:

- **Absence is not evidence.** Zero hits means "not publicly published", not that the
  person doesn't exist, doesn't hold the role, or isn't employed there. Say which one
  you actually know. Never present an empty result as a factual negative about someone.
- **Coverage is uneven, so counts are a floor and never a census.** Executives,
  founders, academics, authors, and public figures are dense; individual contributors,
  private-company staff, and people outside English-language sources are sparse.
  "15,227 people at Nvidia" is who is publicly documented, not the headcount — use
  `/diffbot-organizations` and `nbEmployees` for that.

If a request is really about locating, profiling, or compiling a dossier on a private
individual, this skill is the wrong tool and name matching is not a substitute. Say the
KG covers public professional presence and stop there.
