#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$ROOT/.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf -- "$TEST_ROOT"' EXIT

"$ROOT/scripts/install-publishing-house.sh" \
  --prefix "$TEST_ROOT/install" \
  --source-repos "$KUJO_REPOS" \
  --kujo-bin "$KUJO_BIN" \
  --demo

"$TEST_ROOT/install/bin/publishing-house-doctor" >/dev/null
test -f "$TEST_ROOT/install/first-run/integration-proof.json"
python3 -c 'import json,sys; p=json.load(open(sys.argv[1])); assert p["workflow_count"] == 8 and p["offline"] is True and p["network_calls"] == 0' "$TEST_ROOT/install/first-run/integration-proof.json"
test ! -e "$TEST_ROOT/install/kujo-workflows/.git"
echo "Publishing House clean installation passed"
