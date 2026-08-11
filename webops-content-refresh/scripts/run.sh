#!/usr/bin/env bash
set -euo pipefail
WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$WORKFLOW_DIR/.." && pwd)"
exec python3 "$ROOT/scripts/webops_workflow.py" --workflow "$(basename "$WORKFLOW_DIR")" "$@"
