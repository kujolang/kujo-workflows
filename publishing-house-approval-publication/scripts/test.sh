#!/usr/bin/env bash
set -euo pipefail
WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$WORKFLOW_DIR/.." && pwd)"
RUN_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/publishing-house-approval-publication.XXXXXX")"
trap 'rm -rf "$RUN_ROOT"' EXIT
bash "$WORKFLOW_DIR/bin/run" --request "$WORKFLOW_DIR/fixtures/request.fixture.json" --out "$RUN_ROOT/run" --json
bash "$WORKFLOW_DIR/bin/run" --request "$WORKFLOW_DIR/fixtures/request.fixture.json" --out "$RUN_ROOT/run" --resume --fixture-approval "$ROOT/fixtures/publishing-house/fixture-approval.fixture.json" --json
bash "$WORKFLOW_DIR/bin/run" --request "$WORKFLOW_DIR/fixtures/request.fixture.json" --out "$RUN_ROOT/run" --json
