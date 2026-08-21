# diffbot-skills

A multi-tool agent plugin that ships ten Diffbot skills (DQL-led structured web
knowledge). Skills-only — no commands/, no .mcp.json.

Distributed two ways from the same `skills/` tree:

1. **`npx skills`** — harness-agnostic install into each agent's skills directory
2. **Plugin manifests** — marketplace / native plugin install on Claude Code, Copilot,
   Cortex Code, and Factory (Droid)

## Skill layering

`diffbot-dql` is the general-purpose escape hatch — powerful but too broad for
most agents to route to correctly. Five use-case skills sit on top of it, each
pinning an entity type and pre-selecting the levers for that shape:

| Skill | Type | Baked-in defaults |
| --- | --- | --- |
| `diffbot-news` | `Article` | `sortBy:date` unless the user gives a sort or a date condition |
| `diffbot-organizations` | `Organization` | `categories.name` first; singular `location` = HQ |
| `diffbot-people` | `Person` | `employments.{…}` co-constraint is mandatory; `revSortBy:importance` |
| `diffbot-places` | `Place` + `City`/`Subregion`/`Region`/`Country` | narrowest subtype; explicit sort always |
| `diffbot-deals` | `Investment` / `Transaction` | routes to `Organization.investments` / `.acquiredBy` when the filter is industry or M&A |

**organizations vs deals is settled by row shape**, not by subject matter: rows of
companies → `diffbot-organizations`; rows of transactions/investments/deals →
`diffbot-deals`. Both query the same `acquiredBy` and `investments` fields, so the
overlap is real and the descriptions of both skills state the rule explicitly. Don't
"fix" the apparent duplication by giving M&A wholly to one of them.

The row-shape rule stays in every description; what was removed is the **cross-pointer
naming the other skill** ("…use `diffbot-deals`"). Each now states only its own shape —
"Rows are companies, not deals." Reason: a Haiku run picked `diffbot-organizations` first
for "Who are the VPs of Engineering at Stripe?" on 2 of 2 attempts, and each description
was planting the competitor's name inside itself for a smaller model to keyword-match on.
Saves ~216 chars (~54 tokens) of always-on context. Don't re-add the pointers — state the
skill's own row shape and let the reader route.

Keep `diffbot-dql` as-is: the layered skills reference it for anything outside
their shape (products, patents, job posts, facets beyond the documented cases).
Its description deliberately makes the weakest claim of the ten — no `MUST USE` —
so it loses every routing contest against a specific skill.

`diffbot-people` owns `type:Person`; `diffbot-dql` no longer mentions people in its
description or triggers. Don't add them back.

`diffbot-people` states in its description, its intro, and a closing section that
coverage is **public online professional presence only** — the KG is built from the
public web and does not surface people who haven't published themselves. Keep all three:
the skill must not read as a people-finder, absence of a person must never be reported
as a factual negative, and person counts are a floor, not a census. This is a scope and
privacy boundary, not filler — don't trim it for length.

Their DQL guidance is verified against the live KG — including the traps
(`investee.categories` doesn't exist, unknown field paths are silently ignored and
return the unfiltered count, `type:Acquisition` records are name-only stubs,
`Person.employments` conditions inflate ~9x without a `{}` co-constraint,
`Person.descriptors` is unpopulated).

**Don't add a sort unless the ordering is the question.** For non-Article types the
default ranking already encodes relevance/prominence, and an explicit sort overrides it
— measurably for the worse (`homepageUri:"openai.com"` unsorted → OpenAI; with
`revSortBy:nbEmployees` → "OpenAI for Developers"). Articles are the deliberate
exception: `diffbot-news` defaults to `sortBy:date`. An earlier revision told three
skills to "always add an explicit sort"; that was wrong and is corrected.

**The default JSON export payload is not the full entity.** Many filterable fields —
`Organization.ceo`/`.founders`, `Place.population`/`.isPartOf` — are simply absent
unless requested with `get:` (`--spec` requests its CSV columns automatically). A null
in a JSON export usually means it wasn't requested. Confirm with `has:<field>` before
writing "unpopulated" into a skill: an earlier revision wrongly documented
`Place.isPartOf` as unpopulated on exactly this mistake — it is richly populated. Re-verify with
`db dql probe` before editing those claims.

## URL lookups: index before the harness's built-in fetch

The competitor for a `url:` lookup is **the agent's own fetch tool** (`WebFetch`, `curl`,
a browser tool), not `diffbot-extract`. `diffbot-web-search` is written that way on
purpose — an earlier revision framed it as web-search vs. extract, which compares two
Diffbot skills to each other and never reaches the decision the agent is actually making.
Keep the built-in fetch as the named alternative in the description, the section heading,
and the tips. `diffbot-extract` is the secondary note, not the headline.

Querying with a `url:<URL>` prefix is an index lookup, not a retrieval. Verified live:

- Exactly **one** `search_results` element for an indexed URL, **zero** for a miss.
  Server `timeMs` 2–6; wall 300–376 ms across every URL tested.
- URL matching normalizes scheme, missing scheme, and trailing slash to one record.
- `score` on a `url:` hit reflects the *term* match, not the URL match — a single record
  at 0.368 is a clean hit. Don't teach agents to threshold it.

**The routing rule is prose vs. current state**, and it is load-bearing — not a hedge to
trim. Verified failure cases on the "state" side:

- `techcrunch.com` is cached as a **June 2025** snapshot; its "Latest News" is over a year old.
- `status.anthropic.com` is cached as "All Systems Operational" **with no date field**.
- The cached `docs.anthropic.com/…/prompt-caching` page still describes Claude 4 models.
- `npmjs.com/package/react` returns the package prose, no version number.

And on the "index wins" side, measured against this harness's `WebFetch`:

- `reddit.com` → *"Claude Code is unable to fetch"*; `x.com` → *HTTP 402*. Both return an
  index record (X gives the profile shell, not the timeline — don't oversell it).
- `docs.anthropic.com/…/prompt-caching` → `WebFetch` returned a 301 to `platform.claude.com`
  and demanded a second call; `url:` on the original URL returned 4.3 KB first try. Note the
  new `platform.claude.com` URL **misses** the index — migrations cut both ways.

**Non-page URLs are not in the index**: `api.github.com/repos/…`, `raw.githubusercontent.com`
`.md`, `robots.txt`, and an arXiv `/pdf/` URL all missed, while the `/abs/` page hit. The
built-in fetch is correct for those; say so rather than sending agents to retry the index.

**`date` is not a freshness signal — never document it as one.** arXiv `/abs/` returns 2017
(publication), the prompt-caching page returns Jun 2023, Reddit and the status page return
nothing. The response carries no "cached at" value, which is why the rule keys on page kind.

**`content` is chunks, never the full document.** `url:<URL>` alone ≈ 1.1 KB (the page
opening); `url:<URL> <terms>` ≈ 4–6 KB of matching chunks. Extract returned 25.5 KB for the
docs page against 4.3 KB from the index. The API marks a cut chunk with a literal `...`,
which is the escalation signal the skills point at. Neither `maxTokens` (tested to 200000)
nor `numChunks`/`chunks`/`fullContent`/`full` moves that ceiling — they are silently
ignored, so don't add them as a "get the whole page" flag.

Extract timings for context: 1.3 s–9 s typical, 24 s cold on the docs page and 0.8 s on a
repeat. An earlier revision of this file recorded a 30 s timeout returning nothing on that
URL — that was a single non-reproducible run and the claim has been removed.

## Small-model behavior (measured on Haiku)

Verified with headless runs (`claude --plugin-dir . --model haiku -p …`), Opus on the same
prompts as control. `claude plugin eval` would be the right harness but is gated on early access.

- **Discovery and matching are fine.** Haiku lists all ten skills, and asked to route without
  acting it maps population→`places`, executives→`people`, URL→`web-search`, all correct.
- **Invocation is gated on the model's own confidence, not on the skill's claim.** "How many
  people live in Reykjavik?" → Haiku answered from memory with no tool call, despite an exact
  trigger-phrase match. The same prompt plus "use one of your available skills" → fired
  `places`, returned 138,772, matching Opus. An obscure place (Kópavogur) fired the skill
  unprompted. **`diffbot-places` already says "prefer it over recalling geographic figures"
  and that was read and ignored — do not spend description tokens restating it.**
- **Haiku's successful runs take 21–40 turns** where Opus takes 16. Verbose, not wrong.

The practical read: description text cannot close the confidence gate. Model choice for KG
work is the lever, not more words in the frontmatter.

## Multi-tool manifests

The same `skills/` tree is activated by per-tool manifests. Each tool looks in a
different place; keep all four plugin manifests in sync (name, version, description, license):

| File | Tool | Notes |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | Claude Code | Also the fallback Cortex and Copilot CLI read |
| `.claude-plugin/marketplace.json` | Claude Code | Not a plugin manifest — it makes the repo its own single-plugin **marketplace** so `/plugin marketplace add diffbot/diffbot-skills` resolves. Coexists with `plugin.json` in the same directory |
| `.cortex-plugin/plugin.json` | Snowflake Cortex Code | Preferred over `.claude-plugin/`; "if both present, `.cortex-plugin` wins" |
| `.github/plugin/plugin.json` | GitHub Copilot CLI + VS Code | Note the `plugin/` subdir. The one path VS Code reads that `.claude-plugin/` does **not** cover |
| `.factory-plugin/plugin.json` | Factory.ai (Droid) | No `.claude-plugin/` fallback — needs its own manifest. Components must stay at repo root, never inside `.factory-plugin/` |

- `license` is **required** by Copilot/GitHub — all four manifests carry it (MIT). Factory only requires name/description/version; extra fields are ignored.
- Skills auto-discover from `skills/`; no `skills` path field needed in any manifest.
- **Copilot/VS Code manifest path = `.github/plugin/plugin.json` (with the `plugin/` subdir).**
  Some third-party guides say bare `.github/plugin.json` or repo-root `plugin.json` — those are
  wrong/outdated. Verified against the live `github/awesome-copilot` reference marketplace, whose
  every plugin uses `<plugin>/.github/plugin/plugin.json` (skills/agents sit at the plugin root,
  sibling to `.github/`), and against VS Code's documented auto-detect order
  (`.plugin/plugin.json` → root `plugin.json` → `.github/plugin/plugin.json` → `.claude-plugin/plugin.json`).
- Copilot installs plugins from a marketplace (`marketplace.json` in `.github/plugin/` or
  `.claude-plugin/`) or locally via `copilot plugin install <path>`. The Claude Code
  `marketplace.json` this repo ships is read by Claude Code only; Copilot still needs either its
  own catalog entry or a local path install.

### Claude Code specifics

- `.claude-plugin/marketplace.json` uses `"source": "./"` — the repo is its own single-plugin
  marketplace, the same shape `mvanhorn/last30days-skill` uses. Without this file
  `/plugin marketplace add` has nothing to read and the only install path is a Git clone.
- **The marketplace plugin entry deliberately omits `version`.** It is optional (14 of 287
  entries in `anthropics/claude-plugins-official` carry it) and `plugin.json` is the single
  source of truth. Don't add it back — it would become a fifth manifest to keep in sync.
- **Both Claude Code install paths work; keep both in the README.** A clone into
  `~/.claude/skills/diffbot-skills` loads as the `diffbot@skills-dir` plugin *because* the repo
  ships `.claude-plugin/plugin.json` — the nested `skills/` tree is then discovered normally.
  Verified: `claude plugin list` reports `diffbot@skills-dir` at the manifest version, ten skills. Adding
  `marketplace.json` does not affect this path.
  - The bare-directory rule is what trips people up: a directory in `~/.claude/skills/` with
    **no** `plugin.json` is only discovered when `SKILL.md` is at its top level. `<dir>/skills/<name>/SKILL.md`
    with no manifest is silently ignored. That is why the README says to clone the repo root.
  - Skills-directory plugins load at **session start**, so a clone never appears in an
    already-running session. The README says to restart; keep that note.
- Validate before release: `claude plugin validate .` checks `marketplace.json` when present, and
  `claude plugin validate .claude-plugin/plugin.json` checks the plugin manifest. `--strict` turns
  warnings into a non-zero exit for CI.
- **This file lives at `docs/CLAUDE.md`, not the repo root — keep it there.** At the root it
  tripped the only `--strict` warning (*"CLAUDE.md at the plugin root is not loaded as project
  context"*), which blocked a green CI run. Moving it clears that.
  - The tradeoff, so nobody "restores" it by accident: a root `CLAUDE.md` is auto-loaded as
    project context when someone opens this repo to work on it; `docs/CLAUDE.md` is not — it
    loads only when the agent is working inside `docs/`. Read it explicitly before editing
    skills or manifests, and point agents at it in any task that touches them.

### Harnesses with NO addable manifest

- **ForgeCode** (`forgecode.dev`, the `.forge/` folder) has **no installable-plugin/manifest
  concept** — no `.forge-plugin/plugin.json`, no marketplace, no install command. It consumes
  skills only from `.forge/skills/<name>/SKILL.md` (project), `~/forge/skills/` (global), or the
  cross-tool `~/.agents/skills/` convention. Nothing to add to this repo; a Forge user copies/symlinks
  the SKILL.md files into `.forge/skills/`. (Don't confuse with Atlassian Forge or claude-forge — unrelated.)
- **Cowork** is served by a **separate branch** — `cowork`, which carries `scripts/`
  (bundling tooling) and `vendor/` (the `db` CLI plus its pinned dependency closure) on top
  of `main`. Cowork's sandbox blocks PyPI, so its zip must ship the CLI inside it; every
  install path on `main` bootstraps `~/.diffbot/venv` from PyPI instead and never reads
  `vendor/`. Keeping those ~9.6 MB off `main` matters because `npx skills`, the plugin
  marketplaces, and the Git clone path all download the repo. `vendor/` is in `.gitignore`
  here so a rebase can't quietly reintroduce it — **don't "fix" that by untracking it on
  `cowork`, where it must stay committed.** To ship a Cowork build, rebase `cowork` on
  `main` and run `scripts/build-bundle.sh`; see `scripts/README.md` on that branch.
- **pi.dev** is served by a **separate repository** — [`diffbot/diffbot-pi`](https://github.com/diffbot/diffbot-pi),
  a pi-wrapped TS library installed with `pi install git:github.com/diffbot/diffbot-pi`. Nothing to add
  to this repo and no fifth manifest to keep in sync: pi.dev never reads this `skills/` tree. The README
  lists pi.dev under compatible harnesses, so keep the two repos' capability claims aligned when either
  ships new surface area.

## `npx skills` install

```bash
npx skills add diffbot/diffbot-skills
```

Pulls this GitHub repo (skills are not published to npm). The CLI discovers
`skills/*/SKILL.md` and installs into Claude Code, Cursor, Copilot, Pi, Droid,
Cortex, ForgeCode, Codex, and [many more](https://github.com/vercel-labs/skills#supported-agents).
Browse: [skills.sh](https://skills.sh).

- This path reads nothing but `skills/*/SKILL.md` — no manifest is involved, so it works
  on harnesses that have no addable manifest at all (ForgeCode) and needs no catalog listing.
- **It depends on `name:` being present in every SKILL.md** — the CLI/agentskills.io use it
  for discovery. See the naming section below; the two requirements happen to agree.
- The CLI strips `name:` and `allowed-tools:` when it writes the universal `agent/skills/`
  copies. That normalization is the CLI's, not a defect in this repo — don't "fix" it here.

## Skill naming — do NOT shorten to bare names

Every skill is named with a `diffbot-` prefix (dir + `name:` frontmatter):
`diffbot-dql`, `diffbot-news`, `diffbot-organizations`, `diffbot-people`,
`diffbot-places`, `diffbot-deals`, `diffbot-web-search`, `diffbot-extract`,
`diffbot-entities`, `diffbot-crawl`. Invoked as `/diffbot-dql`, etc. This is
deliberate — do not "clean up" to `/dql`, `/extract`, `/news`, `/people`, etc.

Why: plugin skills share a **flat namespace** with every other installed plugin.
Two compounding facts make bare names dangerous:

1. Declaring `name:` in SKILL.md frontmatter **strips the `diffbot:` plugin
   prefix** entirely — the skill registers only as its bare name
   (claude-code#22063, closed as not planned). All our skills declare `name:`.
2. There is no way to require namespace-qualified invocation (claude-code#43695,
   also closed not planned).

So generic names like `extract`/`crawl`/`entities`/`web-search` would collide with
other plugins — notably **firecrawl** (same `development` category) ships
crawl/extract-style skills. Prefixing the skill `name` itself is the only fix that
is collision-proof across all three tools regardless of their namespacing behavior.

`name:` is also **required** by the `npx skills` CLI / agentskills.io for discovery, so
dropping it to regain the `diffbot:` auto-prefix would break that install path outright.

If you add a skill, prefix it `diffbot-` and keep the dir name == `name:` field.

## Permissions / deps

- No plugin `settings.json` — permissions live in each SKILL.md's `allowed-tools`
  (fixed-path Bash allowlist only: `db`, `venv`, `pip install`, plus `jq` where used).
- Deps live in `~/.diffbot/venv` (stable path so the allowlist rule matches), not
  `${CLAUDE_PLUGIN_DATA}` (which `allowed-tools` can't variable-substitute).
