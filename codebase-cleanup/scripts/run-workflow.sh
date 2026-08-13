#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPOS="${KUJO_REPOS:-$(cd "$WORKFLOW_DIR/../.." && pwd)}"
KUJO="${KUJO_BIN:-$REPOS/kujo/target/release/kujo}"

if [[ ! -x "$KUJO" ]]; then
  printf 'ERROR: Kujo runtime not found: %s\n' "$KUJO" >&2
  exit 2
fi

exec "$KUJO" run "$WORKFLOW_DIR/cleanup.kujo" -- "$@"
