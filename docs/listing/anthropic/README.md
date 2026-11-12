# Anthropic listing

Two Anthropic marketplaces, two different paths. **The community marketplace is
the active submission path** — the official one has no public application process.

## Community marketplace (`claude-community`) — active

The real public queue: submit via an in-app form, get reviewed + safety-screened,
and the plugin is SHA-pinned into `anthropics/claude-plugins-community`.

- **Start here → `community-submission.md`** — paste-ready name, description, and
  example use cases for the form, the form URLs (Console vs. claude.ai), the
  pre-submit `claude plugin validate` step, and the post-approval install line.

## Official marketplace (`claude-plugins-official`) — deferred

Anthropic curates this at its discretion. There is **no application process**, and
the submission form does **not** add plugins to it; listing is by Anthropic's
choice (informally, others request consideration via a GitHub issue on
`anthropics/claude-plugins-official`). The bundle below is kept ready for when a
curator / partner contact opens up:

- `handoff.md` — cover note + paste-ready marketplace entry
- `marketplace-entry.json` — the SHA-pinned entry to merge
- `positioning-brief.md` — 1-page, DQL-led positioning
- `validation-proof.md` — captured `claude plugin validate` + smoke-test logs

Pinned release: `v1.1.0` @ `466f802ebadd8126bb09dc9fe9e81b736a8814b6`.

## Directory review holds cleared in v1.2.1

v1.2.0 was held by the developer-portal scan at
[claude.ai/directory/manage](https://claude.ai/directory/manage) on three findings. What
each was and what 1.2.1 changed:

| Finding | Count | Fix in 1.2.1 |
| --- | --- | --- |
| *Pre-approves broad shell access in `allowed-tools`* | 10 (one per SKILL.md) | Every entry now names one `db` subcommand at the fixed path (`Bash(~/.diffbot/venv/bin/db dql export:*)`); `python3 -m venv`, `pip install`, and `pip uninstall` are gone from all ten. `jq:*` kept only on the four skills that pipe JSON through it. |
| *Contains a download-and-run command* | 3 | The Step 1 bootstrap — `pip install`, `pip uninstall`, `pip install --force-reinstall` — is removed from all ten skills. Each now runs `db --version` and, if the CLI is missing, stops and shows the user the install line to run or approve. Installing is documented in the README only. |
| *No icon* | 1 | `.claude-plugin/icon.png`, 1024x1024. There is **no `icon` field** in the manifest schema — adding one fails `claude plugin validate --strict`. |

Two useful notes from the portal's published rules
([pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist)):

- A wildcard after a shell, interpreter, or package manager is held whatever the path, so
  `Bash(python3:*)` and `Bash(pip install:*)` can never pass. Scoping to a specific
  command, as in the portal's own `Bash(git status:*)` example, is what clears it.
- The checklist's executable surface for a skill is a `` !`…` `` line. These skills have
  none, so what made the old bootstrap a *plugin-run* command was the `allowed-tools`
  pre-approval sitting next to it. Removing the pre-approval is what breaks the pairing —
  see **Permissions / deps** in `docs/CLAUDE.md` before changing either half.

## Directory review holds in v1.2.2

The Monday 2026-11-09 resubmission was this same tree (v1.2.1, plus the Saturday
`Read(~/.diffbot/tmp/**)` allowlist tweak). Nothing had landed on main since Saturday
2026-11-07. Diffbot is not a Verified organization. The portal check is stricter than
1.2.1's "scope each Bash entry to one subcommand" fix: `allowed-tools` entries beyond
`Read`, `Grep`, `Glob`, and `LS` are accepted only from Verified orgs. Scoping
`Bash(~/.diffbot/venv/bin/db dql export:*)` does not clear it. Do not put Bash back.

| Finding | Count | What 1.2.2 did |
| --- | --- | --- |
| *BLOCKING: `allowed-tools` beyond Read, Grep, Glob, and LS* | every skill | `Bash` and `jq` removed from all ten. Nine skills keep only `Read(~/.diffbot/tmp/**)`. `diffbot-web-search` omits the `allowed-tools` key. No `${...}` paths, no `//` or `\\` paths, no URLs. `db` and `jq` prompt the user. |
| *Pre-approves broad shell access (Bash)* | 10 | Resolved by the same Bash removal. |
| *An image or font file the plugin's code could run* | 2 | Audited, files left as-is. The only image or font in the tree is `.claude-plugin/icon.png`, which the report already marked Info/passed. No hooks, scripts, commands, or skill instructions load or execute an image or font as code. No `icon` field added — it is not in the schema and `claude plugin validate --strict` fails on it. |
| *Download-and-run commands* (`curl \| sh`, `uvx`/`npx` of a remote URL, `pip install` from a URL) | 3 | Left as documentation. The plugin itself does not run them: there is no hook, script, command, or `` !`…` `` line, and no bundled installer was added. The README install / upgrade / `npx skills add` sections stay. Each skill's Step 1 block still shows `python3 -m venv ~/.diffbot/venv && ~/.diffbot/venv/bin/pip install 'diffbot>=3.1.0'` for the user to run or approve, and still says the skill never installs, upgrades, or uninstalls the CLI. 1.2.1's note that installing was "documented in the README only" was incomplete — the line also lives in those Step 1 blocks, as documentation. |

## Directory-policy CI

`.github/workflows/directory-policy.yml` runs the check **inline** — a
`python3 - <<'PY'` heredoc in its `Check directory allowlist policy` step — on
pull requests into `main` and on pushes to `main`. It is inline rather than a
`scripts/` file because the directory scans `main` and a non-Verified org may
ship only Markdown, text, JSON, YAML, and PNG/JPEG/GIF/WebP/ICO images there;
scripts, shebang files, and package-manager configs are refused. Workflow files
are not plugin surface, so the guard is unchanged: twelve self-test cases run
first (all in temporary directories), then the live checkout. Diffbot is not a
Verified org, so the check fails if any plugin-surface `allowed-tools` /
`allowedTools` (skill frontmatter, commands, agents, `plugin.json`, `settings.json`, hooks)
names a tool other than `Read`, `Grep`, `Glob`, or `LS`, or contains a `${...}`
path, a path starting with `//` or `\\`, or a URL. `Bash` and `jq` cannot come
back without failing CI. Docs-only `pip install` / `pip uninstall` / upgrade
fences in `SKILL.md` and `README.md`, and the README
`npx skills add https://github.com/...` line, stay — they are user documentation,
not something the plugin runs. A hook command, a `` !`…` `` line, or an allowlist
that runs a download-and-run install still fails. Notes under `docs/listing/` are
not scanned as plugin surface. The workflow does not install the Claude CLI; if
`claude` is absent it skips `claude plugin validate --strict`.

The portal may still warn about those docs-only pip lines and about the required
plugin icon. The two image findings were likely a false positive on
`.claude-plugin/icon.png`, which the same report already marked Info/passed.
Those warnings are not cleared by this check. No `icon` field was added
(`claude plugin validate --strict` rejects it). Andrew's contact still has to
resubmit; this repository does not submit the plugin.
