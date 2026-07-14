#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPOS="${KUJO_REPOS:-$(cd "$ROOT/.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$REPOS/kujo/target/release/kujo}"
TRIBUNAL="${TRIBUNAL_ROOT:-$REPOS/tribunal}"
OUT="${OUT_DIR:-$ROOT/.runs/tribunal-decision-gate}"
TMP="$(mktemp -d "$(python3 -c 'import tempfile; print(tempfile.gettempdir())')/kujo-tribunal-gate.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

test -x "$KUJO_BIN"
test -x "$TRIBUNAL/bin/tribunal"
mkdir -p "$OUT"
python3 - "$TMP/config.json" "$TMP/storage" <<'PY'
import json
import sys
json.dump({"tribunal": {"storage_dir": sys.argv[2]}}, open(sys.argv[1], "w"))
PY

review_output="$(KUJO_BIN="$KUJO_BIN" "$TRIBUNAL/bin/tribunal" review "$TRIBUNAL/examples/product-decision.md" --panel fast-two-model --mock --config "$TMP/config.json")"
run_id="$(printf '%s\n' "$review_output" | sed -n '1p')"
test -n "$run_id"
printf '%s\n' "$review_output" > "$OUT/review.txt"
KUJO_BIN="$KUJO_BIN" "$TRIBUNAL/bin/tribunal" verify "$run_id" --config "$TMP/config.json" > "$OUT/verify.json"
KUJO_BIN="$KUJO_BIN" "$TRIBUNAL/bin/tribunal" export "$run_id" --format json --config "$TMP/config.json" > "$OUT/export.json"
jq -e --arg id "$run_id" '.ok == true and .runId == $id and .artifactsChecked > 0' "$OUT/verify.json" >/dev/null
jq -e --arg id "$run_id" '.runId == $id and (.artifactPaths | length) > 0' "$OUT/export.json" >/dev/null

python3 - "$OUT/export.json" "$OUT/decision-receipt.json" "$run_id" <<'PY'
import json
import sys
export = json.load(open(sys.argv[1]))
run_id = sys.argv[3]
json.dump({
    "contract": "kujo.tribunal.decision-receipt", "contract_version": "1.0", "decision_id": f"{run_id}:decision",
    "workflow_ref": {"id": "tribunal-decision-gate", "version": "1"}, "run_ref": {"id": run_id, "attempt": 1}, "step_ref": {"id": "mock-review", "sequence": 1},
    "decision": {"status": "approved", "binding": False, "confidence": 0.5, "rationale": "Tribunal mock review completed; caller must apply its own binding policy.", "quorum": {"required": 1, "achieved": 1}, "dissent": [], "escalation": {"required": False}},
    "participants": [{"id": "tribunal-mock-panel", "role": "mock-panel", "outcome": "agree"}],
    "evidence": [{"id": path, "kind": "tribunal-artifact", "uri": path} for path in export["artifactPaths"]],
    "tool_receipt": {"tool": "tribunal", "run_id": run_id, "integrity_status": "verified", "signature_status": "absent"},
    "provenance": {"source_tool": "tribunal", "source_version": "0.7.0", "artifact_refs": export["artifactPaths"]},
    "redaction": {"policy": "workflow-default-redaction-v1", "redacted_fields": []}, "idempotency_key": f"{run_id}:mock-review:1"
}, open(sys.argv[2], "w"), indent=2)
PY

python3 "$ROOT/scripts/validate_contract_instance.py" "$ROOT/contracts/tribunal/decision-receipt.v1.schema.json" "$OUT/decision-receipt.json"
echo "PASS Tribunal decision gate: $OUT"
