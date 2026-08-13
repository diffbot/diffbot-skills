# Factory (Droid) listing — `factory-plugins`

Factory's official catalog is the public repo [Factory-AI/factory-plugins](https://github.com/Factory-AI/factory-plugins). Submission is a **pull request** that vendors the plugin under `plugins/` and adds an entry to `.factory-plugin/marketplace.json`.

Git install from this repo works today without that PR — see the README Install section.

## Git install (works now)

```bash
droid plugin install https://github.com/diffbot/diffbot-skills.git
```

Manifest: `.factory-plugin/plugin.json` (Factory does **not** read `.claude-plugin/` as a fallback — this file is required).

Factory tracks plugin versions by **Git commit** on marketplace update, not semver in `plugin.json`. Document semver for humans; expect users on `factory-plugins` to pull latest marketplace commit unless the marketplace source is pinned.

## Marketplace PR (submission path)

1. Fork [Factory-AI/factory-plugins](https://github.com/Factory-AI/factory-plugins).
2. Copy the plugin into `plugins/diffbot/`:
   - `plugins/diffbot/.factory-plugin/plugin.json`
   - `plugins/diffbot/skills/` — all five `diffbot-*` skill folders
3. Add the marketplace entry from **`marketplace-entry.json`** (this folder) to `.factory-plugin/marketplace.json`.
4. Open a PR using **`factory-pr.md`** as the description template.
5. Test locally from your fork:
   ```bash
   droid plugin marketplace add /path/to/your/factory-plugins-fork
   droid plugin install diffbot@factory-plugins
   ```
6. After merge, update the README marketplace row to the `diffbot@factory-plugins` install line.

**Maintenance:** Factory vendoring creates a second copy of `skills/`. On each `diffbot-skills` release, sync `plugins/diffbot/skills/` in `factory-plugins` and open a follow-up PR. Upstream: `diffbot/diffbot-skills` tagged releases.

**Category:** `research` (KG querying, entity enrichment, competitive landscape). Alternatives: `productivity` if Factory prefers breadth.

Pinned release to sync from: `v1.1.0` @ `466f802ebadd8126bb09dc9fe9e81b736a8814b6`.
