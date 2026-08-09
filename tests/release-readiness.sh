#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

make validate
make format
python3 -m json.tool package.json >/dev/null
bash .github/scripts/check-kujo-tool-artifacts.sh

echo "release-readiness validation passed"
