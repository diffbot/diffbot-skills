#!/usr/bin/env bash
#
# Build a Cowork-installable zip of the diffbot plugin.
#
# Produces dist/<name>.zip containing a single top-level <name>/ folder with
# only the files the plugin needs: the per-tool manifests, the skills/ tree,
# and README/LICENSE. Internal dev files (docs/, PLAN.md, CLAUDE.md, .git) are
# left out so the bundle stays lean.
#
# Re-run after editing a skill, then re-upload the same dist/<name>.zip in
# Cowork via Customize > Plugins.
#
# Usage:
#   scripts/build-bundle.sh            # -> dist/diffbot.zip
#   scripts/build-bundle.sh --version  # -> dist/diffbot-<version>.zip as well

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

manifest=".claude-plugin/plugin.json"
[ -f "$manifest" ] || { echo "error: $manifest not found" >&2; exit 1; }

name="$(jq -r '.name' "$manifest")"
version="$(jq -r '.version' "$manifest")"
[ -n "$name" ] && [ "$name" != "null" ] || { echo "error: could not read .name from $manifest" >&2; exit 1; }

# Files/dirs to include in the bundle (everything the host tools read).
include=(
  ".claude-plugin"
  ".cortex-plugin"
  ".factory-plugin"
  ".github"
  "skills"
  "vendor"
  "README.md"
  "LICENSE"
)

dist="$repo_root/dist"
mkdir -p "$dist"

# Stage into a temp dir under the plugin name so the zip wraps everything in a
# single <name>/ folder (the layout Cowork's zip upload expects).
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
pkg="$stage/$name"
mkdir -p "$pkg"

for item in "${include[@]}"; do
  if [ -e "$item" ]; then
    # --no-D and excludes keep cruft out of the copy.
    rsync -a --exclude='.DS_Store' --exclude='__pycache__' --exclude='*.pyc' \
      "$item" "$pkg/"
  else
    echo "warning: skipping missing path '$item'" >&2
  fi
done

out="$dist/$name.zip"
rm -f "$out"
# Zip from the stage root so paths are <name>/...
( cd "$stage" && zip -rq "$out" "$name" -x '*.DS_Store' )

echo "Built $out  (plugin '$name' v$version)"

if [ "${1:-}" = "--version" ]; then
  versioned="$dist/$name-$version.zip"
  cp "$out" "$versioned"
  echo "Built $versioned"
fi
