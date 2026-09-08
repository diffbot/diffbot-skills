# Grok Build (xAI) listing — `xai-official`

xAI's official catalog is the public repo [xai-org/plugin-marketplace](https://github.com/xai-org/plugin-marketplace). Submission is a **pull request** that appends one entry to `.grok-plugin/marketplace.json`. Third-party plugins use a **remote source**: nothing is vendored — the entry points at this repo and pins a full 40-character commit SHA, and Grok Build clones that commit at install time.

Manifest: `.grok-plugin/plugin.json` (Grok Build reads it first and falls back to `.claude-plugin/plugin.json`; we ship both so the Grok listing is not coupled to the Claude manifest).

## Install (after listing)

Inside Grok Build run `/marketplace`, find **diffbot**, and press `i` to install. Setup is the same as every other harness: a Diffbot API token at `~/.diffbot/credentials` (see the README Setup section) and Python 3.10+.

## Marketplace PR (submission path)

1. Fork [xai-org/plugin-marketplace](https://github.com/xai-org/plugin-marketplace) and branch from `main`.
2. Pin the commit to ship — the current `main` HEAD of this repo:
   ```bash
   git ls-remote https://github.com/diffbot/diffbot-skills.git HEAD
   ```
3. Append the entry from **`marketplace-entry.json`** (this folder) to `.grok-plugin/marketplace.json`, replacing the `sha` placeholder with that commit.
4. Regenerate the component index and validate — this is exactly what their CI runs:
   ```bash
   python3 scripts/generate-plugin-index.py
   python3 scripts/validate-catalog.py
   python3 scripts/generate-plugin-index.py --check
   ```
   Index generation shallow-fetches the pinned commit, so the commit must be public and reachable (never pin a branch commit that may be rebased away).
5. Open the PR using **`xai-pr.md`** as the description, filling in the pinned SHA. CI plus code-owner review is required.
6. After merge, update the README marketplace row and record the pinned SHA below.

**Maintenance:** a remote source means no second copy of `skills/` anywhere — but the catalog is frozen at the pinned commit. To ship a release to Grok Build users, open a PR that bumps the `sha` in `.grok-plugin/marketplace.json` and regenerates the index. xAI also runs a daily `bump-plugin-shas` workflow that advances pins when the manifest `version` changes, so bump `version` in all five manifests on every release.

**Review expectations** (from their CONTRIBUTING): source under the official org (`diffbot/`, not a personal account); `keywords`/`domains` must be brand-scoped because they drive the plugin CTA — generic terms like `search`, `crawl`, `api` get pushed back; static security audit of skills, hooks, and MCP configs. This plugin is skills-only with a fixed-path Bash allowlist and no hooks or MCP servers, which keeps that audit short.

**Category:** `development` — the same category as the other web-data plugins in the catalog (firecrawl, exa, tavily). Their catalog has no `research` category.

Pinned release: see the PR — `.grok-plugin/marketplace.json` in `xai-org/plugin-marketplace` is the source of truth for what Grok Build users receive.
