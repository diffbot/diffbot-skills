/*
  Validation proof — captured during pre-release, v1.1.0.
  Tag: v1.1.0, pinned commit 466f802ebadd8126bb09dc9fe9e81b736a8814b6
*/

# Validation proof — diffbot-skills v1.1.0

Captured on 2026-08-12 against PyPI `diffbot-python` **0.2.1**, with a valid token
at `~/.diffbot/credentials`.

v1.1.0 adds five use-case Knowledge Graph skills — `/diffbot-news`,
`/diffbot-organizations`, `/diffbot-people`, `/diffbot-places`, `/diffbot-deals` —
layered over the existing `/diffbot-dql`, which keeps its DQL reference material but
gives up its news and people routing claims to the new skills. Ten skills total.

## Manifest / structure

```
$ claude plugin validate .
Validating plugin manifest: .../.claude-plugin/plugin.json
Validating plugin: .../CLAUDE.md
⚠ Found 1 warning:
  ❯ root: CLAUDE.md at the plugin root is not loaded as project context.
    To ship context with your plugin, use a skill (skills/<name>/SKILL.md) instead.
✔ Validation passed with warnings
```

The single warning is expected and unchanged from v1.0.0: `CLAUDE.md` is
maintainer documentation, not user-facing plugin context.

All four manifests verified in sync at `1.1.0` — `name`, `version`, `license`,
`repository`, `homepage`, `keywords`, `author`, and `description` are byte-identical
across `.claude-plugin/`, `.cortex-plugin/`, `.github/plugin/`, and `.factory-plugin/`.

All ten skill directories verified: `SKILL.md` present, frontmatter parses, and
`name:` matches the directory name in every case (the collision-safety invariant).

## CLI smoke tests (PyPI diffbot-python 0.2.1)

All eight subcommands the skills rely on are present:
`ask, crawl, crawl-delete-job, crawl-list-jobs, dql, entities, extract, web-search`.

| Skill | Command | Result |
| --- | --- | --- |
| dql | `db dql init` | ontology refreshed, token found |
| dql | `db dql probe 'type:Organization name:"Diffbot"'` | `4` hits |
| news | `db dql probe 'type:Article tags.label:"Anthropic" sortBy:date'` | `310` hits |
| news | `db dql export … --spec date.str,title,siteName,sentiment,pageUrl` | 826 bytes, dated headlines w/ sentiment |
| organizations | `db dql probe 'type:Organization categories.name:"Semiconductor Companies" location.country.name:"United States"'` | `2592` → `159` with `isPublic:true` |
| organizations | `db dql export … revSortBy:nbEmployees` | Intel, Micron, Qualcomm, Nvidia — correct headcounts |
| organizations | `db dql export 'similarTo(name:"OpenAI") location.country.name:"United States"'` | Hugging Face, Anthropic, Moveworks, Perplexity, Scale AI |
| people | `db dql probe` on both subquery forms | `3457` loose vs `399` co-constrained — the documented ~9x trap, reproduced |
| people | `db dql export … revSortBy:importance` | Jensen Huang / Nvidia, Lip-Bu Tan / Intel, C.C. Wei / TSMC |
| places | `db dql probe 'type:City location.country.name:"Japan" population>1000000'` | `13` hits; `type:Country` → `634` |
| places | `db dql export … revSortBy:population` | Tokyo, Yokohama, Osaka, Nagoya w/ populations |
| deals | `db dql probe 'type:Investment investment.series:"Series A" investment.date>="2026-01-01"'` | `2061` hits |
| deals | `db dql export … investee/series/amount/date/investors` | Etched Series C $300M, Cathedral Series A $160M |
| deals | `db dql export 'isAcquired:true acquiredBy.name:"Microsoft"'` | LinkedIn $26.2B, Nuance $19.7B, Skype $8.5B — figures correct |
| web-search | `db web-search "Diffbot knowledge graph" -n 2 -f text` | 2 results honouring `-n`, top score 0.966 |
| extract | `db extract https://example.com` | markdown content |
| entities | `db entities "Apple CEO Tim Cook…"` | Apple Inc. + Tim Cook resolved w/ Diffbot IDs, sentiment +0.73 |
| crawl | `db crawl-list-jobs` | read-only: returned live job list |

## Live DQL E2E

Each of the five new skills was exercised over its full documented path —
`probe` for selectivity, then `export --spec` to CSV — confirming
ontology cache → parallel probe → export to `~/.diffbot/tmp/` → formatted output,
with no repeated permission prompts.

Every DQL string shipped in the five new SKILL.md files was executed against the
live Knowledge Graph before being written. Documented traps were verified by
observation, not assumption:

- `investee.categories` does not exist on `LinkedEntity` — returns 0, so deal
  queries filtered by industry route through `Organization.investments` instead
  (verified: 0 → 121 hits).
- Unrecognized field paths are **silently ignored** and return the unfiltered
  count (`countryGroup.name:"Europe"` → 18,517,102 = all of `type:Place`).
- `type:Acquisition` records are name-only stubs; M&A routes through
  `Organization.acquiredBy`.
- The default JSON export payload is **not** the full entity — `Organization.ceo`,
  `Organization.founders`, `Place.population`, and `Place.isPartOf` are all absent
  unless requested with `get:`. `--spec` requests its CSV columns automatically.
  Verified both ways: `has:founders` matches while the field is missing from the
  payload, and `get:name,ceo,founders` returns `ceo=Elon Musk` plus five founders.
- `Person.employments` conditions written outside a `{}` co-constraint match across
  *different* jobs and inflate results ~9x (3,457 vs 399 for current semiconductor
  CEOs). `Person.descriptors` is unpopulated, unlike Organization's.
- For non-Article types the **default ranking already encodes relevance**; adding an
  explicit sort overrides it, often wrongly. `homepageUri:"openai.com"` unsorted returns
  OpenAI, `revSortBy:nbEmployees` returns "OpenAI for Developers"; `anthropic.com`
  returns Anthropic vs "Claude Builder Club". Place and Person unsorted results match
  their `revSortBy:population` / `revSortBy:importance` order already.
- `similarTo` returns exactly `--size` ranked results with `hits` mirroring the
  request, so `dql probe` (which runs `size=0`) always reports `0` for it. Both
  `/diffbot-dql` and `/diffbot-organizations` document this exception and direct
  validation to a small `export` instead.

## Dependency floor

The Step 1 bootstrap in every skill pins `diffbot-python>=0.2.1` rather than the bare
package name. This is deliberate: `pip install <pkg>` with no constraint is a no-op
when *any* version is already present, so a venv created against 0.1.0 would never
upgrade. 0.1.0 sent the wrong query parameter for web-search `-n`, silently returning
10 results regardless — the version floor is what guarantees the documented flag
behaves as described.

## Permissions summary

Each SKILL.md pre-authorizes only a fixed-path Bash allowlist:

```
Bash(~/.diffbot/venv/bin/db:*)
Bash(python3 -m venv ~/.diffbot/venv:*)
Bash(~/.diffbot/venv/bin/pip install:*)
Bash(jq:*)              # Knowledge Graph skills only: diffbot-dql, -news,
                        # -organizations, -people, -places, -deals
```

No broad `Bash(*)`. No plugin `settings.json`. Credentials are user-managed at
`~/.diffbot/credentials` and never stored in this repo.
