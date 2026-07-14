#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPOS="${KUJO_REPOS:-$(cd "$ROOT/.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$REPOS/kujo/target/release/kujo}"
RELAY="${RELAY_ROOT:-$REPOS/relay}"
OUT="${OUT_DIR:-$ROOT/.runs/relay-lifecycle-handoff}"
TMP="$(mktemp -d /tmp/kujo-relay-handoff.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

test -x "$KUJO_BIN"
test -f "$RELAY/main.kujo"
mkdir -p "$OUT" "$TMP/work"
git -C "$TMP/work" init -q
git -C "$TMP/work" config user.email relay-workflow@example.invalid
git -C "$TMP/work" config user.name RelayWorkflow
printf 'fixture\n' > "$TMP/work/README.md"
git -C "$TMP/work" add README.md
git -C "$TMP/work" commit -qm baseline

python3 - "$RELAY/examples/worktree-mission.json" "$TMP/work" "$TMP/mission.json" <<'PY'
import json
import sys
spec = json.load(open(sys.argv[1]))
spec["repository"] = sys.argv[2]
json.dump(spec, open(sys.argv[3], "w"), indent=2)
PY

export RELAY_ROOT="$RELAY"
"$KUJO_BIN" run "$RELAY/main.kujo" -- missions run "$TMP/mission.json" --fixture --pause-after-plan --json > "$OUT/paused.json"
run_id="$(jq -r '.run.run_id' "$OUT/paused.json")"
test -n "$run_id" -a "$run_id" != "null"
jq -e '.ok == true and .run.status == "paused" and (.run.checkpoint | type) == "object"' "$OUT/paused.json" >/dev/null

"$KUJO_BIN" run "$RELAY/main.kujo" -- missions resume "$run_id" --json > "$OUT/resumed.json"
jq -e '.ok == true and .run.status == "completed" and (.run.receipts | length) > 0' "$OUT/resumed.json" >/dev/null
"$KUJO_BIN" run "$RELAY/main.kujo" -- runs export "$run_id" --output "$OUT/export.json" --json > "$OUT/export-result.json"
jq -e --arg id "$run_id" '.run_id == $id and .integrity_valid == true and .receipts_valid == true and .receipts_consistent == true' "$OUT/export.json" >/dev/null

python3 - "$OUT/export.json" "$OUT/message-envelope.json" "$OUT/delivery-receipt.json" "$run_id" <<'PY'
import json
import sys
export = json.load(open(sys.argv[1]))
run_id = sys.argv[4]
message_id = f"{run_id}:handoff"
common = {"source_tool": "relay", "source_version": "0.1.0", "artifact_refs": ["events.jsonl", "receipts.json"]}
json.dump({
    "contract": "kujo.relay.message-envelope", "contract_version": "1.0", "message_id": message_id,
    "message_type": "workflow.handoff.completed", "sender": "relay-lifecycle-handoff", "recipient": "workflow-resumer",
    "workflow_ref": {"id": "relay-lifecycle-handoff", "version": "1"}, "run_ref": {"id": run_id, "attempt": 1}, "step_ref": {"id": "resume-callback", "sequence": 1},
    "correlation_id": run_id, "causation_id": run_id, "sequence": 1, "attempt": 1,
    "idempotency_key": f"{run_id}:handoff:1", "created_at": "2026-07-14T00:00:00Z",
    "delivery": {"guarantee": "local_persisted", "ack_required": True, "max_attempts": 1},
    "payload": {"run_id": run_id, "event_count": len(export.get("events", [])), "receipt_count": len(export.get("receipts", []))},
    "provenance": common, "redaction": {"policy": "workflow-default-redaction-v1", "redacted_fields": []}
}, open(sys.argv[2], "w"), indent=2)
json.dump({
    "contract": "kujo.relay.delivery-receipt", "contract_version": "1.0", "message_id": message_id,
    "created_at": "2026-07-14T00:00:01Z", "workflow_ref": {"id": "relay-lifecycle-handoff", "version": "1"}, "run_ref": {"id": run_id, "attempt": 1}, "step_ref": {"id": "resume-callback", "sequence": 1},
    "correlation_id": run_id, "status": "acknowledged", "attempts": 1, "transport": "local_store", "acknowledgment": {"required": True, "status": "received", "received_at": "2026-07-14T00:00:01Z", "actor": "workflow-resumer"},
    "next_action": "resume_workflow", "provenance": common,
    "redaction": {"policy": "workflow-default-redaction-v1", "redacted_fields": []}
}, open(sys.argv[3], "w"), indent=2)
PY

python3 "$ROOT/scripts/validate_contract_instance.py" "$ROOT/contracts/relay/message-envelope.v1.schema.json" "$OUT/message-envelope.json"
python3 "$ROOT/scripts/validate_contract_instance.py" "$ROOT/contracts/relay/delivery-receipt.v1.schema.json" "$OUT/delivery-receipt.json"
"$KUJO_BIN" run "$RELAY/main.kujo" -- missions cleanup "$run_id" --confirm --json > "$OUT/cleanup.json"
jq -e '.ok == true' "$OUT/cleanup.json" >/dev/null
echo "PASS Relay lifecycle handoff: $OUT"
