/*
  Handoff bundle — Snowflake Cortex Code official marketplace listing.
  Send to Snowflake partner / Cortex Code contact (no public submission form).
*/

# Cortex Code listing handoff — diffbot-skills v1.1.0

## Bundle contents

| Item | Where |
| --- | --- |
| Tagged release URL | https://github.com/diffbot/diffbot-skills/releases/tag/v1.1.0 |
| Pinned SHA (40-char) | `466f802ebadd8126bb09dc9fe9e81b736a8814b6` |
| Manifest | `.cortex-plugin/plugin.json` at repo root |
| Positioning brief | [`anthropic/positioning-brief.md`](anthropic/positioning-brief.md) (same product story; Cortex framing below) |
| Validation proof | [`anthropic/validation-proof.md`](anthropic/validation-proof.md) (Claude validate + E2E; add Cortex logs when available) |

## Git install (already works)

Users can install without marketplace curation:

```bash
cortex plugin install diffbot/diffbot-skills
cortex plugin install github:diffbot/diffbot-skills@v1.1.0
```

We are asking for **discoverability** in the official marketplace (`cortex plugin install diffbot`), not basic installability.

## Cortex-specific framing

- **Complement to Snowflake-native skills.** Most community Cortex skills assume an active Snowflake connection and warehouse context. Diffbot provides **external web-scale structured knowledge** — organizations, people, articles — via DQL, without requiring Snowflake SQL for the KG query itself.
- **DQL leads.** Ontology-aware Knowledge Graph querying is the headline; web-search, extract, entities, and crawl are supporting skills in one plugin.
- **No Snowflake connection required** for Diffbot API calls (token at `~/.diffbot/credentials`). Useful alongside Snowflake work: enrichment, competitive landscape, news research, entity resolution for pipelines.
- **Collision-safe naming.** Skills are prefixed `diffbot-` (`/diffbot-dql`, not `/dql`) because plugin skills share a flat namespace.

## Talking points (shared with Anthropic handoff)

- Skills-only repo, per-tool manifests, minimal fixed-path `allowed-tools` — easy audit.
- Dependencies: PyPI `diffbot-python` into `~/.diffbot/venv`; no vendored code, no secrets in repo.
- Never market as "web scraping" or generic "web search" — **structured web knowledge for developers**.

## Post-listing

Once a marketplace entry exists, the README marketplace row resolves to:

```bash
cortex plugin install diffbot
```

(Exact marketplace name to be confirmed with Snowflake.)
