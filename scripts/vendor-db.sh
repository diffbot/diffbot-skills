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
# Usage:
#   scripts/vendor-db.sh                       # vendor latest diffbot-python
#   scripts/vendor-db.sh diffbot-python==0.2.1 # pin a specific version

set -euo pipefail

spec="${1:-diffbot-python}"
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
# Step 2: its declared deps, resolved against 3.9 wheels (honors each dep's own floor).
"$py" -m pip install --target "$vendor" --quiet \
  --python-version "$target_py" --only-binary=:all: \
  'click>=8.1.0' 'httpx>=0.27.0' 'rich>=13.0.0'

# pip writes machine-specific console scripts into bin/; replace them with our
# portable launcher (resolves vendor/ relative to itself, guards Python version).
rm -rf "$vendor/bin"
mkdir -p "$vendor/bin"
cp "$root/scripts/db-launcher.py" "$vendor/bin/db"
chmod +x "$vendor/bin/db"

# Drop build cruft so the committed bundle stays lean and deterministic.
find "$vendor" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$vendor" -type f -name '*.pyc' -delete

size="$(du -sh "$vendor" | awk '{print $1}')"
echo "Vendored '$spec' into vendor/ ($size)."