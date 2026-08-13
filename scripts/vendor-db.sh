#!/usr/bin/env bash
#
# Regenerate vendor/ — the self-contained Diffbot `db` CLI plus its pure-Python
# dependency tree — so the skills run with no pip install at runtime.
#
# Network is needed only here, at build time. The produced vendor/ needs none.
#
# The bundle targets Python 3.9 (the macOS system interpreter). diffbot-python's
# metadata declares >=3.10, but its code and every dependency run fine on 3.9, so
# we bypass only diffbot-python's own gate and resolve the deps against 3.9 wheels
# (--python-version 3.9). Any builder Python works; the output is 3.9-compatible.
#
# Every version below is pinned exactly, transitives included, so a regenerate
# reproduces the committed vendor/ byte-for-byte instead of drifting to whatever
# PyPI serves that day. Bumping diffbot-python means re-resolving the deps and
# updating the pins here in the same commit.
#
# Usage:
#   scripts/vendor-db.sh                       # reproduce the pinned bundle
#   scripts/vendor-db.sh diffbot-python==0.3.0 # build against a different version

set -euo pipefail

spec="${1:-diffbot-python==0.2.1}"

# Full dependency closure of diffbot-python 0.2.1, resolved against 3.9 wheels.
deps=(
  'anyio==4.12.1'
  'certifi==2026.5.20'
  'click==8.1.8'
  'h11==0.16.0'
  'httpcore==1.0.9'
  'httpx==0.28.1'
  'idna==3.18'
  'markdown-it-py==3.0.0'
  'mdurl==0.1.2'
  'pygments==2.20.0'
  'rich==15.0.0'
  'typing-extensions==4.15.0'
)
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
vendor="$root/vendor"
target_py="3.9"

py=""
for cand in python3.13 python3.12 python3.11 python3.10 python3.9 python3; do
  if command -v "$cand" >/dev/null 2>&1; then py="$(command -v "$cand")"; break; fi
done
[ -n "$py" ] || { echo "error: need a python3 on PATH to build the vendor bundle" >&2; exit 1; }

echo "Building vendor/ for '$spec' (targeting Python $target_py) with $("$py" --version)…"
rm -rf "$vendor"
# Step 1: diffbot-python itself, no deps, bypassing only its conservative >=3.10 gate.
"$py" -m pip install --target "$vendor" --quiet --no-deps --ignore-requires-python "$spec"
# Step 2: its dependency closure, pinned, resolved against 3.9 wheels.
"$py" -m pip install --target "$vendor" --quiet \
  --python-version "$target_py" --only-binary=:all: \
  "${deps[@]}"

# pip writes machine-specific console scripts into bin/; replace them with our
# portable launcher (resolves vendor/ relative to itself, guards Python version).
rm -rf "$vendor/bin"
mkdir -p "$vendor/bin"
cp "$root/scripts/db-launcher.py" "$vendor/bin/db"
chmod +x "$vendor/bin/db"

# Drop build cruft so the committed bundle stays lean and deterministic.
find "$vendor" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$vendor" -type f -name '*.pyc' -delete
# pip also marks which packages were named on the command line; that set is a
# property of this script, not of the bundle.
find "$vendor" -type f -name 'REQUESTED' -delete
# RECORD still lists the files just deleted, and names them with the *builder's*
# Python ABI tag (cpython-311 vs -312) plus a hash of pip's machine-specific
# console-script shebang. Left in, they make every regenerate on a different
# machine produce a spurious diff. Strip the dead entries.
find "$vendor" -type f -name 'RECORD' -exec perl -i -ne \
  'print unless m{__pycache__} || m{^\.\./\.\./bin/} || m{/REQUESTED,}' {} +

size="$(du -sh "$vendor" | awk '{print $1}')"
echo "Vendored '$spec' into vendor/ ($size)."