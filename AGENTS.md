# AGENTS.md — Anthropic plugin-directory criteria

For any agent editing this repository, whatever harness it runs in.

This file describes the criteria the Anthropic plugin directory has actually applied
to this plugin, as reported back to us by the Anthropic developer portal. It is a
description of the feedback we have, not a procedure — it says what the directory accepts and
refuses, and leaves how to satisfy it to whoever makes the change.

Everything here comes from two portal results: a directory check of the resubmitted
1.2.1 tree (commit `70fd1db`) and a later scheduled check of v1.2.2. Nothing below is
inferred beyond those.

## Two facts that frame all of it

**Diffbot is not a Verified organization.** Several of the directory's rules are
written as "accepted only from Verified organizations." For this plugin, that phrasing
means *not accepted*.

**The directory scans `main`, not only the release tag.** The v1.2.2 result was labeled
on commit `2f7ca3b` — the tip of `main` at scan time — while the release tag `v1.2.2`
sits on `240bc9f`. A file that the directory refuses therefore causes a refusal while it
is on `main`, regardless of whether any tagged release contains it.

## Blocking / refusal criteria

These stopped the plugin from progressing. In the v1.2.2 result, the portal's later
stages (Review → Publish → Live) were not reached because of the refusal.

### Allowed-tools beyond Read, Grep, Glob, and LS

Reported as BLOCKING on the 1.2.1 tree (`70fd1db`): `allowed-tools` / `allowedTools`
entries naming any tool beyond `Read`, `Grep`, `Glob`, and `LS` are accepted only from
Verified organizations.

1.2.1's approach — a `Bash` entry scoped to a single `db` subcommand — did not satisfy
this. This blocker was cleared in 1.2.2, and the v1.2.2 scan recorded those as fixed.

### Files outside the allowed types

New in the v1.2.2 result, and the reason that version was **refused by directory
policy**: *"Files outside the allowed types accepted only from Verified organizations."*
The directory accepts scripts, programs, and files outside its allowed types only from
Verified orgs.

Accepted: Markdown, text, JSON, YAML, and PNG, JPEG, GIF, WebP, or ICO images.

Refused, as called out in the result:

- any file that starts with `#!`
- scripts and programs generally
- package-manager configuration files (the example given: `pnpm-workspace.yaml`)
- extra `.claude/skills` or `.claude-plugin` folders
- `hooks.json`, `.mcp.json`, `.lsp.json`, and `monitors.json` files that Claude Code
  does not read, and output-styles
- files that are not UTF-8, or that contain NUL bytes

Explicitly allowed to stay: a license, a readme, `.gitignore`, and the plugin's icon —
provided each is UTF-8 text or an allowed image type and does not start with `#!`.

A CI script added to `main` was itself refused under this rule.

## Warnings

Present in both results, and *not* the reason for either the block or the refusal. The
portal states official guidance for each; it does not demand a change in our situation.

### "Image or font file that the plugin's code could run"

Anthropic's guidance: if nothing runs it, leave it as it is and the plugin stays held
for review; if something does run it, ship that code as a readable script instead.

### "Contains a download-and-run command"

Anthropic's guidance: where the plugin runs this, ship the script inside the plugin and
run that file instead. Where it only appears in documentation, nothing needs to change.

The docs-only `pip` / `npx` install lines in this repo were left in place on that basis.

## Notes (not failures)

**"Images and fonts passed without a code check."** One well-formed image
(`.claude-plugin/icon.png`) was let through without being read as code.

**The security scan passed** in the v1.2.2 result. The file-type refusal, not the
security scan, is what held that version.

## Repo-specific context worth knowing

- `claude plugin validate --strict` rejects an `icon` field in `plugin.json`. The icon is
  picked up by convention at `.claude-plugin/icon.png`, which is why no manifest field
  points at it.
- Background on the skills, manifests, permissions history, and the `cowork` branch
  lives in `docs/CLAUDE.md`.
