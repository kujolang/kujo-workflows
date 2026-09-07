#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPOS="${KUJO_REPOS:-$(cd "$ROOT/.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$REPOS/kujo/target/release/kujo}"
WORKCELL="${WORKCELL_ROOT:-$REPOS/workcell}"
OUT="${OUT_DIR:-$ROOT/.runs/workcell-execution-gate}"
TMP_ROOT="${WORKCELL_TMP_ROOT:-$REPOS/.workcell-host-tmp}"
mkdir -p "$TMP_ROOT"
TMP="$(mktemp -d "$TMP_ROOT/kujo-workcell-gate.XXXXXX")"
RUN_OUTPUT="$TMP_ROOT/kujo-workcell-gate-output.$RANDOM"
trap 'rm -rf "$TMP" "$RUN_OUTPUT"' EXIT

test -x "$KUJO_BIN"
test -x "$WORKCELL/bin/workcell"
mkdir -p "$OUT"
# Observe the operator-selected context without changing Docker global configuration.
# Workcell doctor/run remain the policy authority; no profile is disabled here.
doctor_status=0
env TMPDIR="$TMP_ROOT" KUJO="$KUJO_BIN" "$WORKCELL/bin/workcell" doctor --backend docker --json > "$OUT/doctor.json" || doctor_status=$?
printf '%s\n' "$doctor_status" > "$OUT/doctor-exit-code.txt"
docker info --format '{{json .SecurityOptions}}' > "$OUT/docker-security-options.json"
python3 "$ROOT/workcell-execution-gate/scripts/configure_profile.py" "$WORKCELL/examples/hello/workcell.json" "$OUT/docker-security-options.json" "$OUT/workcell-definition.json"
DEFINITION="$OUT/workcell-definition.json"
git -C "$TMP" init -q
git -C "$TMP" config user.email workcell-workflow@example.invalid
git -C "$TMP" config user.name WorkcellWorkflow
printf 'fixture\n' > "$TMP/input.txt"
git -C "$TMP" add input.txt
git -C "$TMP" commit -qm baseline

env TMPDIR="$TMP_ROOT" KUJO="$KUJO_BIN" "$WORKCELL/bin/workcell" validate --file "$DEFINITION" --json > "$OUT/validate.json"
env TMPDIR="$TMP_ROOT" KUJO="$KUJO_BIN" "$WORKCELL/bin/workcell" inspect --file "$DEFINITION" --repo "$TMP" --json > "$OUT/inspect.json"
jq -e '.ok == true and .definition.backend == "docker"' "$OUT/validate.json" >/dev/null
jq -e '.ok == true and .effective_security_policy.network_mode == "none" and .resource_limits.timeout_ms > 0' "$OUT/inspect.json" >/dev/null

run_status=0
env TMPDIR="$TMP_ROOT" KUJO="$KUJO_BIN" "$WORKCELL/bin/workcell" run --file "$DEFINITION" --repo "$TMP" --output "$RUN_OUTPUT" --no-pull --json > "$OUT/run-result.json" || run_status=$?
test "$run_status" -eq 0 -o "$run_status" -eq 4 -o "$run_status" -eq 7 -o "$run_status" -eq 8

python3 - "$OUT/inspect.json" "$OUT/run-result.json" "$OUT/work-package.json" "$OUT/completion-receipt.json" "$(tr -d '[:space:]' < "$WORKCELL/VERSION")" <<'PY'
import json
import sys
inspect_result, result = [json.load(open(path)) for path in sys.argv[1:3]]
source_version = sys.argv[5]
run_id = result.get("run_id", "workcell-run-unknown")
ok = result.get("ok") is True
error = result.get("error", "")
status = "succeeded" if ok else ("blocked" if "permission" in error.lower() or result.get("stage") in {"preparing", "starting"} else "failed")
receipt = result.get("receipt", {})
package_id = f"{run_id}:package"
package = {
    "contract": "kujo.workcell.work-package", "contract_version": "1.0", "package_id": package_id,
    "created_at": "2026-07-14T00:00:00Z",
    "workflow_ref": {"id": "workcell-execution-gate", "version": "1"}, "run_ref": {"id": run_id, "attempt": 1},
    "step_ref": {"id": "bounded-docker-execution", "sequence": 1},
    "source": {"repository": receipt.get("source_repository", "fixture"), "commit": receipt.get("source_commit", "unknown"), "dirty_allowed": False},
    "execution": {"runtime_backend": inspect_result["runtime_backend"], "workspace_strategy": inspect_result["definition"]["workspace"]["strategy"], "command": inspect_result["definition"]["command"], "resource_limits": {"timeout_ms": inspect_result["resource_limits"]["timeout_ms"], "max_output_bytes": inspect_result["resource_limits"]["max_output_bytes"]}, "network_mode": inspect_result["network_mode"]},
    "artifacts": [{"path": "hello.txt", "required": True}], "verification": {"required": True, "commands": [["test", "-f", "hello.txt"]]},
    "provenance": {"source_tool": "workcell", "source_version": source_version, "artifact_refs": ["receipt.json", "manifest.json"]},
    "redaction": {"policy": "workflow-default-redaction-v1", "redacted_fields": []}, "idempotency_key": f"{run_id}:bounded-docker-execution:1"
}
completion = {
    "contract": "kujo.workcell.completion-receipt", "contract_version": "1.0", "package_id": package_id, "created_at": "2026-07-14T00:00:01Z",
    "workflow_ref": {"id": "workcell-execution-gate", "version": "1"}, "run_ref": {"id": run_id, "attempt": 1}, "step_ref": {"id": "bounded-docker-execution", "sequence": 1}, "run_id": run_id,
    "status": status, "lifecycle": receipt.get("lifecycle", ["created", "failed"]),
    "execution": {"runtime_backend": result.get("runtime_backend", inspect_result["runtime_backend"]), "cleanup_status": receipt.get("cleanup_status", "not_run"), "receipt_path": result.get("receipt_path", "receipt.json"), "manifest_path": receipt.get("manifest_path", "manifest.json"), "source_commit": receipt.get("source_commit", ""), "definition_hash": receipt.get("workcell_definition_hash", "")},
    "artifacts": [{"path": "hello.txt", "status": "exported" if ok else "missing"}],
    "errors": [] if ok else [{"code": "WORKCELL_EXECUTION_BLOCKED" if status == "blocked" else "WORKCELL_EXECUTION_FAILED", "message": error or "Workcell returned a non-success result.", "retryable": status != "blocked"}],
    "provenance": {"source_tool": "workcell", "source_version": source_version, "artifact_refs": ["receipt.json", "manifest.json", "stderr.log"]},
    "redaction": {"policy": "workflow-default-redaction-v1", "redacted_fields": []}
}
json.dump(package, open(sys.argv[3], "w"), indent=2)
json.dump(completion, open(sys.argv[4], "w"), indent=2)
PY

python3 "$ROOT/scripts/validate_contract_instance.py" "$ROOT/contracts/workcell/work-package.v1.schema.json" "$OUT/work-package.json"
python3 "$ROOT/scripts/validate_contract_instance.py" "$ROOT/contracts/workcell/completion-receipt.v1.schema.json" "$OUT/completion-receipt.json"
if jq -e '.status == "blocked"' "$OUT/completion-receipt.json" >/dev/null; then
  echo "BLOCKED Workcell execution gate: bounded runtime did not produce a completion artifact; $OUT" >&2
  exit 3
fi
if ! jq -e '.status == "succeeded"' "$OUT/completion-receipt.json" >/dev/null; then
  echo "FAILED Workcell execution gate: completion receipt is not successful; $OUT" >&2
  exit 1
fi
echo "PASS Workcell execution gate: $OUT"
