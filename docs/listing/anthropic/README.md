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
