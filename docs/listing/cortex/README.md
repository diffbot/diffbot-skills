# Snowflake Cortex Code listing

Cortex Code can install this plugin **from Git today** — no marketplace approval required. Official catalog listing is a separate, partner-dependent step.

## Git install (works now)

Documented in the repo README. Quick reference:

```bash
cortex plugin install diffbot/diffbot-skills
cortex plugin install github:diffbot/diffbot-skills@v1.1.0   # pin release
```

Cortex Code Desktop: Agent Settings → Plugins → Add from GitHub → `diffbot/diffbot-skills` (optionally `#v1.1.0`).

Manifest: `.cortex-plugin/plugin.json` (preferred over `.claude-plugin/` when both exist).

Validate before release:

```bash
cortex plugin validate .
```

## Official Cortex marketplace

Cortex docs describe `cortex plugin install <name>` resolving through an **official plugin marketplace** (e.g. `python-repl`). There is **no public submission form or marketplace PR** documented the way GitHub Copilot (`awesome-copilot`) or Factory (`factory-plugins`) publish theirs.

**Path:** Snowflake partner / Cortex Code contact — same class of curation as Anthropic's `claude-plugins-official`. Use **`handoff.md`** as the cover note.

**Do not** default to `Snowflake-Labs/cortex-code-skills` for this plugin. That repo accepts **individual skills** with Cortex-specific frontmatter (`title`, `summary`, `tools`, `type`, etc.), not full multi-skill plugins. Our value is the bundled plugin (one install, five `diffbot-*` skills). Only pursue a skills-repo PR if Snowflake explicitly asks.

## What to do

1. Confirm Git install and capture `cortex plugin validate` + E2E logs (extend [`anthropic/validation-proof.md`](anthropic/validation-proof.md) or add `validation-proof.md` here once Cortex CLI is available).
2. Send **`handoff.md`** plus reused assets from [`anthropic/`](anthropic/) to the Snowflake partner contact.
3. Once a marketplace name is assigned (target: `diffbot`), update the README marketplace table and this folder.

Pinned release: `v1.1.0` @ _SHA recorded post-tag_.
