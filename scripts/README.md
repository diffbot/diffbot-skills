# Cowork bundling tooling — `cowork` branch only

This directory and `vendor/` live on the **`cowork` branch**, not on `main`.

`main` is the skills repo: every install path there (`npx skills`, plugin
marketplaces, git clone) bootstraps `~/.diffbot/venv` from PyPI on first run and
never reads `vendor/`. Carrying ~9.6 MB of vendored Python on `main` would tax
every one of those installs for a payload only this branch uses.

Cowork's sandbox blocks PyPI, so its bundle has to ship the `db` CLI inside the
zip — that's what this tooling builds.

| File | Purpose |
| --- | --- |
| `vendor-db.sh` | Regenerates `vendor/` — the `db` CLI plus its full dependency closure, all pinned, targeting Python 3.9 (the macOS system floor) |
| `db-launcher.py` | Portable launcher written to `vendor/bin/db`; resolves `vendor/` relative to itself and guards the Python version |
| `build-bundle.sh` | Packages `dist/diffbot.zip` for upload via Cowork → Customize → Plugins |

## Keeping this branch current

Skills are authored on `main`. Rebase this branch onto it before building so the
bundle ships the current skills:

```bash
git fetch origin
git rebase origin/main
scripts/build-bundle.sh --version
```

## Bumping the vendored CLI

The pins in `vendor-db.sh` are the reproducibility record — an unpinned resolve
would silently drift with PyPI. To move to a new `diffbot-python`, re-resolve its
dependency closure and update the `deps` array **in the same commit** as the
regenerated `vendor/`:

```bash
scripts/vendor-db.sh diffbot-python==<new-version>
ls vendor | grep dist-info   # read off the resolved versions, update the pins
```
