# diffbot-skills

A multi-tool agent plugin that ships five Diffbot skills (DQL-led structured web
knowledge). Skills-only — no commands/, no .mcp.json.

## Multi-tool manifests

The same `skills/` tree is activated by per-tool manifests. Each tool looks in a
different place; keep all three in sync (name, version, description, license):

| File | Tool | Notes |
| --- | --- | --- |
| `.claude-plugin/plugin.json` | Claude Code | Also the fallback Cortex and Copilot CLI read |
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
  `.claude-plugin/`) or locally via `copilot plugin install <path>`. This repo ships the plugin
  manifest only; a marketplace entry points its `source` at the repo.

### Harnesses with NO addable manifest

- **ForgeCode** (`forgecode.dev`, the `.forge/` folder) has **no installable-plugin/manifest
  concept** — no `.forge-plugin/plugin.json`, no marketplace, no install command. It consumes
  skills only from `.forge/skills/<name>/SKILL.md` (project), `~/forge/skills/` (global), or the
  cross-tool `~/.agents/skills/` convention. Nothing to add to this repo; a Forge user copies/symlinks
  the SKILL.md files into `.forge/skills/`. (Don't confuse with Atlassian Forge or claude-forge — unrelated.)

## Skill naming — do NOT shorten to bare names

Every skill is named with a `diffbot-` prefix (dir + `name:` frontmatter):
`diffbot-dql`, `diffbot-web-search`, `diffbot-extract`, `diffbot-entities`,
`diffbot-crawl`. Invoked as `/diffbot-dql`, etc. This is deliberate — do not
"clean up" to `/dql`, `/extract`, etc.

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

If you add a skill, prefix it `diffbot-` and keep the dir name == `name:` field.

## Permissions / deps

- No plugin `settings.json` — permissions live in each SKILL.md's `allowed-tools`
  (fixed-path Bash allowlist only: `db`, `venv`, `pip install`, plus `jq` where used).
- Deps live in `~/.diffbot/venv` (stable path so the allowlist rule matches), not
  `${CLAUDE_PLUGIN_DATA}` (which `allowed-tools` can't variable-substitute).
