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

Pinned release: `v1.0.0` @ `44a20a931193596243d786ffb02959c8d75a5e8f`.
