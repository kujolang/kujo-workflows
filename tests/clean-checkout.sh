#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

test_root="$(mktemp -d)"
trap 'rm -rf -- "$test_root"' EXIT

checkout="$test_root/kujo-workflows"
mkdir -p "$checkout"
git archive --format=tar "${1:-HEAD}" | tar -xf - -C "$checkout"

cd "$checkout"
make validate
python3 -m json.tool package.json >/dev/null
test ! -e .git

echo "clean-checkout validation passed"
