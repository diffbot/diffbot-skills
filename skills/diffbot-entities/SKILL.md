---
name: diffbot-entities
description: "Identify and resolve named entities in text using the Diffbot NLP API. Links mentions to Diffbot Knowledge Graph entities with confidence scores and sentiment. Use when the user wants to extract entities from text, do NER (named entity recognition), identify companies or people mentioned, or get Diffbot IDs for entities. Triggers on: identify entities, entity recognition, NER, find entities in text, extract entities, entity linking, diffbot NLP, named entity."
allowed-tools: Bash(~/.diffbot/venv/bin/db:*), Bash(python3 -m venv ~/.diffbot/venv:*), Bash(~/.diffbot/venv/bin/pip install:*)
---

# Diffbot Entities (NLP)

Identify and resolve named entities in text using the Diffbot NLP API. Each entity is linked to a Diffbot Knowledge Graph record with confidence, salience, and sentiment scores.

## The `db entities` CLI

**Always invoke with the fixed path `~/.diffbot/venv/bin/db`.**

```
~/.diffbot/venv/bin/db entities "<text>" [-f table|json|dql] [--lang <code>]
echo "<text>" | ~/.diffbot/venv/bin/db entities
```

| Flag | Default | Description |
|------|---------|-------------|
| `-f`, `--format` | `table` | Output: `table` (rich), `json` (raw API), `dql` (ID filter for `db dql`) |
| `--lang` | `auto` | Language code (e.g. `en`, `es`, `fr`). Default auto-detects. |

Text can be passed as a CLI argument or piped via stdin.

## Workflow

### Step 1 — bootstrap

```
[ -d ~/.diffbot/venv ] || python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install -q 'diffbot-python>=0.2.1'
```

The token is read from `DIFFBOT_API_TOKEN` env var or `~/.diffbot/credentials`. If missing:

```
echo "DIFFBOT_API_TOKEN=YOUR_TOKEN_HERE" > ~/.diffbot/credentials && chmod 600 ~/.diffbot/credentials
```

### Step 2 — identify entities

From a string argument:

```
~/.diffbot/venv/bin/db entities "Apple CEO Tim Cook announced record quarterly earnings."
```

From a file via stdin:

```
cat article.txt | ~/.diffbot/venv/bin/db entities
```

Full JSON (inspect raw API fields):

```
~/.diffbot/venv/bin/db entities "Elon Musk founded Tesla and SpaceX." -f json
```

### Step 3 — use entity IDs in DQL

The `-f dql` format emits an `id:or(...)` filter string that can be piped directly into `db dql export`:

```
~/.diffbot/venv/bin/db entities "Apple, Microsoft, and Google dominate cloud AI." -f dql
# → id:or("EiqAqBMJHMT","EL7WL3J","EiCxSaRJP") 

~/.diffbot/venv/bin/db entities "Apple, Microsoft, and Google dominate cloud AI." -f dql \
  | xargs -I{} ~/.diffbot/venv/bin/db dql export "{}" \
      --spec "name,Name;nbEmployees,Employees;homepageUri,Website" \
      --out ~/.diffbot/tmp/entities.csv
```

This is a fast path for turning free text into structured KG lookups — much faster than a name-based DQL query because ID lookups bypass full-text search.

## Output fields

The `table` format shows one row per entity:

| Column | Description |
|--------|-------------|
| **Entity** | Mention text as it appears in the source |
| **Type** | Entity type (`Organization`, `Person`, `Place`, `Product`, etc.) |
| **Confidence** | 0–1 score for entity resolution accuracy |
| **Salience** | 0–1 prominence in the text (higher = more central) |
| **Sentiment** | Per-entity sentiment: `+0.xx` (positive), `-0.xx` (negative), `~0.00` (neutral) |
| **Diffbot ID** | KG entity ID (usable in DQL `id:` lookups) |

The document-level sentiment is printed above the table when present.

## Tips

- **Confidence vs salience**: confidence is about resolution accuracy (is this the right KG record?); salience is about topic importance (how central is this entity to the text?).
- The `dql` format is the killer feature — use it to bridge free text and structured KG data without manually copying IDs.
- For multilingual text, pass `--lang <code>` explicitly for better accuracy.
- Entities without a Diffbot ID were recognized but not linked to the KG (proper noun detection without record match).
