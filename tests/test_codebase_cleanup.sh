#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repos="${KUJO_REPOS:-$(cd "$repo_root/.." && pwd)}"
kujo="${KUJO_BIN:-$repos/kujo/target/release/kujo}"

if [[ ! -x "$kujo" ]]; then
  echo "SKIP Codebase Cleanup Kujo tests: runtime not found at $kujo"
  exit 0
fi

cd "$repo_root/codebase-cleanup"
KUJO_BIN="$kujo" KUJO_REPOS="$repos" "$kujo" run tests/cleanup_tests.kujo
