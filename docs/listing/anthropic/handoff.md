/*
  Handoff bundle — what to send the Anthropic / partner curator for
  claude-plugins-official listing.
*/

# Anthropic listing handoff — diffbot-skills v1.1.0

Send to the Anthropic/partner curator contact (not the community submission form).

## Bundle contents

| Item | Where |
| --- | --- |
| Tagged release URL | https://github.com/diffbot/diffbot-skills/releases/tag/v1.1.0 |
| Pinned SHA (40-char) | `466f802ebadd8126bb09dc9fe9e81b736a8814b6` |
| Marketplace entry JSON | `marketplace-entry.json` (this folder) |
| Positioning brief (1 page) | `positioning-brief.md` |
| Validation proof | `validation-proof.md` |

## Marketplace entry (paste-ready)

Pattern matches firecrawl's entry in `anthropics/claude-plugins-official`
(`source: url` + immutable pinned `sha` + `ref`). See `marketplace-entry.json`.

```json
{
  "name": "diffbot",
  "category": "development",
  "source": {
    "source": "url",
    "url": "https://github.com/diffbot/diffbot-skills.git",
    "sha": "466f802ebadd8126bb09dc9fe9e81b736a8814b6",
    "ref": "v1.1.0"
  }
}
```

## Talking points for the curator

- **DQL is the headline** — ontology-aware KG querying, unique in the
  `development` category. Don't frame as scraping/search.
- Skills-only repo, per-tool manifests, minimal fixed-path permissions — easy audit.
- `claude plugin validate` passes; `/diffbot-dql` completes a real KG query E2E.

## Post-listing

Once live, the README Claude Code install line resolves:

```
/plugin install diffbot@claude-plugins-official
```

(README currently says "marketplace, once listed" — update to drop the caveat
when the entry is merged.)
