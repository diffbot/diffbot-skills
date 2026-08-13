---
name: diffbot-places
description: "Search geographic entities in the Diffbot Knowledge Graph — cities, counties, subregions, states, provinces, countries, and points of interest — by population, prominence, containing place, or proximity. MUST USE skill when the answer is a list of places, or a sourced fact about one such as population; prefer it over recalling geographic figures. Triggers on: list cities, list countries, largest cities, biggest city in, population of, how many people live in, places in, cities near, states in, provinces, counties, regions, points of interest, landmarks."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*), Bash(jq:*)
---

# Diffbot Place Search

Find geographic entities in the Diffbot Knowledge Graph: cities, counties/subregions, states/provinces/regions, countries, and points of interest. This is `type:Place` DQL with the place hierarchy, the right sort keys, and the known gaps already mapped.

Sibling note: `/diffbot-people` for people, `/diffbot-organizations` for companies located somewhere.

Sibling skills: `/diffbot-organizations` (companies, including those *located* somewhere), `/diffbot-news`, `/diffbot-deals`. Use `/diffbot-dql` for anything outside these shapes.

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

### Step 2 — pick the right type

**Query the narrowest type that fits.** `type:Place` matches everything including 12M points of interest; the subtypes are far more selective.

| Type | Approx. count | Covers |
| --- | --- | --- |
| `type:Country` | 634 | Countries |
| `type:Region` | 1,671 | States, provinces, top-level subdivisions |
| `type:Subregion` | 28,160 | Counties, districts, second-level subdivisions |
| `type:City` | 3.7M | Cities, towns, municipalities |
| `type:AdministrativeArea` | 6.5M | Superset of the four above |
| `type:Place` | 18.5M | Everything, including POIs |

Points of interest — parks, landmarks, venues — are `Place` records that are *not* administrative areas. There is no `Landmark` type in practice (`type:Landmark` returns zero):

```
type:Place not(types:"AdministrativeArea") descriptors:"national park"
```

`placeType` is an equivalent filter to the type name (`placeType:"Country"` ≡ `type:Country`); POIs carry `placeType:"other"`.

### Step 3 — pick the levers

#### Containment — `location` or `isPartOf`

Two fields do this, and they are near-equivalent as filters:

```
type:City location.country.name:"Japan"
type:City isPartOf.name:"France"
type:Subregion location.region.name:"California"
type:Region location.country.name:"United States"
```

`location` fields: `.city.name`, `.subregion.name`, `.region.name`, `.country.name`, `.metroArea.name`, `.latitude`, `.longitude`, `.postalCode`.

`isPartOf` is the full containment chain — for Lyon it reads *Metropolitan Lyon <
Rhône < France < Metropolis of Lyon < Arrondissement of Lyon*. Measured against
`location`, they agree closely: French cities are 28,361 via `isPartOf` and 28,353 via
`location.country.name`, and both return exactly 46 once `population>100000` is added.

Prefer `location.*` when you want a specific administrative level (country vs region vs
city), and `isPartOf` when you want "contained by X at any level" or need the chain
itself. **`isPartOf` is absent from the default JSON payload** — request it with `get:`
or `--spec`, or it will look empty. See the payload note in Step 5.

#### Ranking

| Field | Type | Use |
| --- | --- | --- |
| `population` | Integer | `population>1000000`, `revSortBy:population` |
| `importance` | Float (0–100) | Prominence score. Already reflected in the default ranking — sort by it only to override a different sort |
| `wikipediaPageviews` | Integer | Attention proxy; also `wikipediaPageviewsLastQuarter`, `…LastYear`, and `…Growth` variants |
| `area` | Integer | |
| `nbIncomingEdges` | Integer | How connected the entity is in the KG |

**Leave the sort off unless the user asked for an ordering.** The default ranking
already bakes in relevance and prominence, and an explicit sort overrides it — usually
for the worse. Measured: `homepageUri:"openai.com"` unsorted returns **OpenAI**, while
`revSortBy:nbEmployees` returns *"OpenAI for Developers"*; `anthropic.com` unsorted
returns **Anthropic**, sorted returns *"Claude Builder Club"*.

Add a sort only when the ordering *is* the question — "largest cities by population",
"most recent rounds", "biggest acquisitions". (Articles are the exception: see
`/diffbot-news`, where `sortBy:date` is the default.)

For places specifically: `strict:name:"Springfield"` unsorted and with
`revSortBy:population` return an identical top three (Missouri 169k, Massachusetts
156k, Illinois 114k) — the default already surfaces the prominent one.

#### Proximity

`near(...)` resolves a single anchor entity (the first match) and filters by distance; default radius 15km, override with `mi` or `km`:

```
type:City near(type:Place name:"Paris", 50km)
type:Place not(types:"AdministrativeArea") near(type:Place name:"Yosemite", 20mi)
```

#### Other fields

`name`, `allNames`, `description`, `allDescriptions`, `descriptors`, `summary`, `postalCodes`, `areaCodes`, `headOfPlace` (mayors, governors, heads of state), `image`.

#### Worked examples

```
type:City location.country.name:"Japan" population>1000000 revSortBy:population
type:City location.country.name:"Germany" revSortBy:population
type:Subregion location.region.name:"California" revSortBy:population
type:Region location.country.name:"United States"
type:City near(type:Place name:"Paris", 50km) revSortBy:population
type:Place not(types:"AdministrativeArea") descriptors:"national park"
```

### Known gap — continents are not a field

There is no continent field. `countryGroup` exists but is populated on ~49 records, and an unrecognized path like `countryGroup.name:"Europe"` is **silently ignored** — it returns the unfiltered count, which looks like a working query. Watch for a hit count equal to the bare `type:` count; that is the tell.

For "all countries in Europe", match the prose description and verify:

```
type:Country description:"in Europe"
```

This returns ~89 hits for Europe: over-inclusive (countries merely *mentioning* Europe leak in) and it double-counts duplicate records. Export it, then filter the list yourself before presenting, and tell the user the list was text-matched rather than pulled from a continent field. With only 634 countries total, exporting all of `type:Country` and filtering against your own knowledge is also a legitimate approach.

### Step 4 — probe before committing

```
~/.diffbot/venv/bin/db dql probe \
  'type:City location.country.name:"France" population>100000' \
  'type:City location.country.name:"France"' \
  'type:Place name:"Europe"'
```

Two failure signatures to watch for:
- **Hit count == the bare `type:` count** → your filter path is wrong and was ignored.
- **Zero hits** → the value is wrong for this field, or the concept isn't modelled at all
  (continents: `isPartOf.name:"Europe"` on countries returns 0).

`probe` fails the whole batch if any single variant is rejected by the API — fix the
offending clause and re-run rather than assuming the others were checked.

Place names are matched with **contains**, so `name:"Springfield"` pulls in every
Springfield on earth. Add `strict:` plus a `location.country.name` or
`location.region.name` filter to pin one, and `facet:placeType` to see what mix of
cities, subregions, and POIs a name spans.

### Step 5 — export and display

```
~/.diffbot/venv/bin/db dql export "<DQL>" --out ~/.diffbot/tmp/places.csv \
  --spec "name,Place;population,Population;location.region.name,Region;location.country.name,Country;importance,Importance" \
  --size 50
```

**The default JSON payload is not the full entity.** A plain `--format json` export of a
Place returns only `name`, `description`, `placeType`, `importance`, `types`, and
provenance — `population`, `location`, and `isPartOf` are all **absent**, even though you
can filter on them. Ask for them explicitly:

```
~/.diffbot/venv/bin/db dql export '<DQL> get:name,population,location,isPartOf' --out ~/.diffbot/tmp/places.json --format json --size 50
```

`--spec` already does this for you, which is why the CSV above shows populations. Only
raw JSON exports need `get:`. A `null` field in a JSON export usually means you didn't
request it, not that the data is missing.

**Display**

1. Render a markdown table with columns matched to the question — name, population, containing region/country.
2. **Deduplicate.** The KG holds multiple records for the same place (e.g. two `Tokyo` rows with different populations — city proper vs. metro). Collapse same-name rows in the same parent and say which figure you kept, or show both labelled.
3. Format populations with thousands separators; `importance` is a 0–100 prominence score, not a rank — only show it if it's relevant.
4. Print the final DQL in a plain code block.
5. Tell the user the saved file path, and offer more rows (`--size N`, `--from K`) or a refinement.
