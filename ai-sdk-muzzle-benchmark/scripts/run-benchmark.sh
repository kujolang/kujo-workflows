#!/usr/bin/env bash
set -u -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$ROOT/../.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
AI_SDK_DIR="${AI_SDK_DIR:-$KUJO_REPOS/ai-sdk}"
MUZZLE_BIN="${MUZZLE_BIN:-$KUJO_REPOS/muzzle/muzzle}"
RUNLEDGER_BIN="${RUNLEDGER_BIN:-$KUJO_REPOS/runledger/bin/runledger}"

PROVIDER="${PROVIDER:-openai}"
MODEL="${MODEL:-}"
MAX_TOKENS="${MAX_TOKENS:-4000}"
PORT_BASE="${PORT_BASE:-8120}"
TASK_NAME="${TASK_NAME:-Build PHP website benchmark app}"

STAMP="${STAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="${RUN_DIR:-$ROOT/.runs/$STAMP}"
PROMPT_FILE="$RUN_DIR/prompt.md"
SUMMARY="$RUN_DIR/summary.md"
COMPARE="$RUN_DIR/compare.md"
LOG_DIR="$RUN_DIR/logs"
LEDGER_DIR="$RUN_DIR/runledger"
REQUEST_SCRIPT="$ROOT/scripts/ai-sdk-app-request.kujo"

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

mkdir -p "$RUN_DIR" "$LOG_DIR" "$LEDGER_DIR"
cp "$ROOT/templates/site-prompt.md" "$PROMPT_FILE"

now_ms() {
  python3 - <<'PY'
import time
print(int(time.time() * 1000))
PY
}

json_get() {
  node -e "
const fs = require('fs');
const file = process.argv[1];
const path = process.argv[2].split('.');
let value = JSON.parse(fs.readFileSync(file, 'utf8'));
for (const key of path) value = value && value[key];
if (value === undefined || value === null) value = '';
if (typeof value === 'object') console.log(JSON.stringify(value));
else console.log(String(value));
" "$1" "$2"
}

bytes_for() {
  if [ -f "$1" ]; then
    wc -c < "$1" | tr -d ' '
  else
    printf '0'
  fi
}

estimate_tokens() {
  local bytes="$1"
  if [ -z "$bytes" ] || [ "$bytes" = "0" ]; then
    printf '0'
  else
    python3 - "$bytes" <<'PY'
import math
import sys
print(max(1, math.ceil(int(sys.argv[1]) / 4)))
PY
  fi
}

record_stage() {
  local name="$1"
  local status="$2"
  local detail="$3"
  case "$status" in
    pass) PASS_COUNT=$((PASS_COUNT + 1)) ;;
    fail) FAIL_COUNT=$((FAIL_COUNT + 1)) ;;
    warn) WARN_COUNT=$((WARN_COUNT + 1)) ;;
  esac
  printf '| `%s` | %s | %s |\n' "$name" "$status" "$detail" >> "$SUMMARY"
}

safe_runledger() {
  if [ -x "$RUNLEDGER_BIN" ]; then
    RUNLEDGER_DIR="$LEDGER_DIR" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" "$@"
    return $?
  fi
  return 127
}

start_ledger() {
  local mode="$1"
  local log="$LOG_DIR/runledger-start-$mode.log"
  local model_label="${MODEL:-provider-default}"
  safe_runledger start \
    --provider "$PROVIDER" \
    --model "$model_label" \
    --task "$TASK_NAME" \
    --prompt "$PROMPT_FILE" \
    --repo "$RUN_DIR/$mode/app" >"$log" 2>&1
  sed -n 's/^Started run: //p' "$log" | head -n 1
}

ensure_muzzle_workflows() {
  mkdir -p "$RUN_DIR/.muzzle/workflows" "$RUN_DIR/.muzzle/manifests" "$RUN_DIR/.muzzle/logs" "$RUN_DIR/.muzzle/reports" "$RUN_DIR/.muzzle/state"
  cp "$ROOT/scripts/ai-request.sh" "$RUN_DIR/.muzzle/workflows/ai-request.sh"
  cp "$ROOT/scripts/verify-app.sh" "$RUN_DIR/.muzzle/workflows/verify-app.sh"
  chmod +x "$RUN_DIR/.muzzle/workflows/ai-request.sh" "$RUN_DIR/.muzzle/workflows/verify-app.sh"
  cat > "$RUN_DIR/.muzzle/manifests/ai-request.json" <<'JSON'
{
  "name": "ai-request",
  "summary": "Send the benchmark prompt through the Kujo AI SDK and write ack.json.",
  "runner": "bash",
  "script": "workflows/ai-request.sh",
  "quiet_by_default": true,
  "safety": {
    "require_git_repo": false,
    "allow_dirty_tree": true,
    "requires_network": true,
    "human_approval_recommended": false
  }
}
JSON
  cat > "$RUN_DIR/.muzzle/manifests/verify-app.json" <<'JSON'
{
  "name": "verify-app",
  "summary": "Run PHP syntax, asset, content, and local HTTP checks for the generated app.",
  "runner": "bash",
  "script": "workflows/verify-app.sh",
  "quiet_by_default": true,
  "safety": {
    "require_git_repo": false,
    "allow_dirty_tree": true,
    "requires_network": false,
    "human_approval_recommended": false
  }
}
JSON
}

write_missing_ack() {
  local ack="$1"
  local mode="$2"
  local reason="$3"
  cat > "$ack" <<JSON
{
  "ack": "kujo-ai-sdk-response-ack-v1",
  "ok": false,
  "provider": "$PROVIDER",
  "requested_provider": "$PROVIDER",
  "model": "$MODEL",
  "requested_model": "$MODEL",
  "offline_fixture": false,
  "status_code": 0,
  "finish_reason": "",
  "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
  "prompt_file": "$PROMPT_FILE",
  "output_text": "",
  "error": {"code": "workflow_error", "message": "$reason"},
  "mode": "$mode"
}
JSON
}

run_trial() {
  local mode="$1"
  local port="$2"
  local trial_dir="$RUN_DIR/$mode"
  local app_dir="$trial_dir/app"
  local logs="$trial_dir/logs"
  local ack="$trial_dir/ack.json"
  local metrics="$trial_dir/metrics.json"
  local ai_stdout="$logs/ai-sdk.stdout.log"
  local ai_stderr="$logs/ai-sdk.stderr.log"
  local verify_log="$logs/verify.log"
  local render_log="$logs/render.log"

  mkdir -p "$logs"

  local run_id
  run_id="$(start_ledger "$mode" || true)"
  if [ -n "$run_id" ]; then
    safe_runledger note "$run_id" "Benchmark mode: $mode" >/dev/null 2>&1 || true
  fi

  local ai_start ai_end ai_code verify_start verify_end verify_code render_code
  ai_start="$(now_ms)"
  if [ "$mode" = "muzzle" ]; then
    (
      cd "$RUN_DIR"
      "$MUZZLE_BIN" run ai-request "$PROVIDER" "$MODEL" "$PROMPT_FILE" "$ack" "$AI_SDK_DIR" "$KUJO_BIN" "$MAX_TOKENS" "$REQUEST_SCRIPT" --json
    ) >"$ai_stdout" 2>"$ai_stderr"
    ai_code=$?
  else
    "$ROOT/scripts/ai-request.sh" "$PROVIDER" "$MODEL" "$PROMPT_FILE" "$ack" "$AI_SDK_DIR" "$KUJO_BIN" "$MAX_TOKENS" "$REQUEST_SCRIPT" >"$ai_stdout" 2>"$ai_stderr"
    ai_code=$?
  fi
  ai_end="$(now_ms)"

  if [ "$ai_code" -ne 0 ] && [ ! -f "$ack" ]; then
    write_missing_ack "$ack" "$mode" "AI SDK request exited $ai_code"
  fi

  node "$ROOT/scripts/render-app-from-ack.js" "$ack" "$app_dir" "$mode" >"$render_log" 2>&1
  render_code=$?

  verify_start="$(now_ms)"
  if [ "$mode" = "muzzle" ]; then
    (
      cd "$RUN_DIR"
      "$MUZZLE_BIN" run verify-app "$app_dir" "$port" --json
    ) >"$verify_log" 2>&1
    verify_code=$?
  else
    "$ROOT/scripts/verify-app.sh" "$app_dir" "$port" >"$verify_log" 2>&1
    verify_code=$?
  fi
  verify_end="$(now_ms)"

  local input_tokens output_tokens total_tokens app_source ai_bytes verify_bytes exposed_bytes exposed_tokens status verdict
  local ack_ok status_code error_code error_message
  input_tokens="$(json_get "$ack" "usage.input_tokens")"
  output_tokens="$(json_get "$ack" "usage.output_tokens")"
  total_tokens="$(json_get "$ack" "usage.total_tokens")"
  ack_ok="$(json_get "$ack" "ok")"
  status_code="$(json_get "$ack" "status_code")"
  error_code="$(json_get "$ack" "error.code")"
  error_message="$(json_get "$ack" "error.message")"
  app_source="$(json_get "$app_dir/generation-meta.json" "source")"
  ai_bytes="$(bytes_for "$ai_stdout")"
  verify_bytes="$(bytes_for "$verify_log")"
  exposed_bytes=$((ai_bytes + verify_bytes))
  exposed_tokens="$(estimate_tokens "$exposed_bytes")"

  status="pass"
  verdict="$mode benchmark completed; app source=$app_source; AI SDK ok=$ack_ok; AI SDK exit=$ai_code; verify exit=$verify_code."
  if [ -n "$error_code" ]; then
    verdict="$verdict Provider error: $error_code $error_message."
  fi
  if [ "$ack_ok" != "true" ] || [ "$ai_code" -ne 0 ] || [ "$render_code" -ne 0 ] || [ "$verify_code" -ne 0 ]; then
    status="partial"
  fi

  if [ -n "$run_id" ]; then
    safe_runledger usage "$run_id" --input "${input_tokens:-0}" --output "${output_tokens:-0}" >/dev/null 2>&1 || true
    safe_runledger note "$run_id" "AI SDK duration ms: $((ai_end - ai_start))" >/dev/null 2>&1 || true
    safe_runledger note "$run_id" "Verification duration ms: $((verify_end - verify_start))" >/dev/null 2>&1 || true
    safe_runledger note "$run_id" "Approx exposed local transcript tokens: $exposed_tokens" >/dev/null 2>&1 || true
    safe_runledger finish "$run_id" --status "$status" --verdict "$verdict" --repo "$app_dir" >/dev/null 2>&1 || true
  fi

  cat > "$metrics" <<JSON
{
  "mode": "$mode",
  "provider": "$PROVIDER",
  "model": "${MODEL:-provider-default}",
  "runledger_id": "$run_id",
  "ai_exit_code": $ai_code,
  "ai_ok": $ack_ok,
  "ai_status_code": ${status_code:-0},
  "ai_error_code": "$error_code",
  "ai_error_message": "$error_message",
  "render_exit_code": $render_code,
  "verify_exit_code": $verify_code,
  "ai_duration_ms": $((ai_end - ai_start)),
  "verify_duration_ms": $((verify_end - verify_start)),
  "input_tokens": ${input_tokens:-0},
  "output_tokens": ${output_tokens:-0},
  "total_tokens": ${total_tokens:-0},
  "app_source": "$app_source",
  "ai_stdout_bytes": $ai_bytes,
  "verify_stdout_bytes": $verify_bytes,
  "exposed_local_transcript_bytes": $exposed_bytes,
  "estimated_exposed_local_transcript_tokens": $exposed_tokens,
  "ack_path": "$ack",
  "app_dir": "$app_dir"
}
JSON

  if [ "$status" = "pass" ]; then
    record_stage "$mode" pass "$verdict"
  else
    record_stage "$mode" warn "$verdict"
  fi
}

write_compare() {
  local raw="$RUN_DIR/raw/metrics.json"
  local muzzle="$RUN_DIR/muzzle/metrics.json"
  node - "$raw" "$muzzle" "$COMPARE" <<'NODE'
const fs = require("fs");
const [rawPath, muzzlePath, outPath] = process.argv.slice(2);
const raw = JSON.parse(fs.readFileSync(rawPath, "utf8"));
const muzzle = JSON.parse(fs.readFileSync(muzzlePath, "utf8"));
const pct = (before, after) => {
  if (!before) return "n/a";
  return `${(((before - after) / before) * 100).toFixed(1)}%`;
};
const md = `# AI SDK + Muzzle Benchmark Compare

| Metric | Raw | Muzzle | Delta |
|---|---:|---:|---:|
| AI SDK ok | ${raw.ai_ok} | ${muzzle.ai_ok} | - |
| AI status code | ${raw.ai_status_code} | ${muzzle.ai_status_code} | ${muzzle.ai_status_code - raw.ai_status_code} |
| AI error | ${raw.ai_error_code || "-"} ${raw.ai_error_message || ""} | ${muzzle.ai_error_code || "-"} ${muzzle.ai_error_message || ""} | - |
| AI input tokens | ${raw.input_tokens} | ${muzzle.input_tokens} | ${muzzle.input_tokens - raw.input_tokens} |
| AI output tokens | ${raw.output_tokens} | ${muzzle.output_tokens} | ${muzzle.output_tokens - raw.output_tokens} |
| AI total tokens | ${raw.total_tokens} | ${muzzle.total_tokens} | ${muzzle.total_tokens - raw.total_tokens} |
| AI duration ms | ${raw.ai_duration_ms} | ${muzzle.ai_duration_ms} | ${muzzle.ai_duration_ms - raw.ai_duration_ms} |
| Verify duration ms | ${raw.verify_duration_ms} | ${muzzle.verify_duration_ms} | ${muzzle.verify_duration_ms - raw.verify_duration_ms} |
| Local transcript bytes exposed | ${raw.exposed_local_transcript_bytes} | ${muzzle.exposed_local_transcript_bytes} | ${pct(raw.exposed_local_transcript_bytes, muzzle.exposed_local_transcript_bytes)} smaller |
| Estimated local transcript tokens | ${raw.estimated_exposed_local_transcript_tokens} | ${muzzle.estimated_exposed_local_transcript_tokens} | ${pct(raw.estimated_exposed_local_transcript_tokens, muzzle.estimated_exposed_local_transcript_tokens)} smaller |

Raw app source: ${raw.app_source}

Muzzle app source: ${muzzle.app_source}

RunLedger raw id: \`${raw.runledger_id || "not-created"}\`

RunLedger muzzle id: \`${muzzle.runledger_id || "not-created"}\`
`;
fs.writeFileSync(outPath, md);
NODE
}

cat > "$SUMMARY" <<EOF
# AI SDK + Muzzle Benchmark Run

- Timestamp: $STAMP
- Provider: $PROVIDER
- Model: ${MODEL:-provider default}
- Run dir: \`$RUN_DIR\`
- Prompt: \`$PROMPT_FILE\`

## Stage Results

| Stage | Status | Detail |
|---|---:|---|
EOF

echo "AI SDK + Muzzle benchmark"
echo "Run dir: $RUN_DIR"
echo "Provider: $PROVIDER"
echo "Model: ${MODEL:-provider default}"
echo

if [ ! -x "$KUJO_BIN" ]; then
  record_stage "preflight-kujo" fail "Kujo runtime not executable: $KUJO_BIN"
else
  record_stage "preflight-kujo" pass "$KUJO_BIN"
fi

if [ ! -d "$AI_SDK_DIR" ]; then
  record_stage "preflight-ai-sdk" fail "AI SDK directory not found: $AI_SDK_DIR"
else
  record_stage "preflight-ai-sdk" pass "$AI_SDK_DIR"
fi

if [ ! -x "$MUZZLE_BIN" ]; then
  record_stage "preflight-muzzle" fail "Muzzle binary not executable: $MUZZLE_BIN"
else
  record_stage "preflight-muzzle" pass "$MUZZLE_BIN"
fi

if [ ! -x "$RUNLEDGER_BIN" ]; then
  record_stage "preflight-runledger" warn "RunLedger binary not executable: $RUNLEDGER_BIN"
else
  record_stage "preflight-runledger" pass "$RUNLEDGER_BIN"
fi

ensure_muzzle_workflows
record_stage "prepare-muzzle-workflows" pass "$RUN_DIR/.muzzle"

run_trial "raw" "$PORT_BASE"
run_trial "muzzle" "$((PORT_BASE + 1))"

write_compare
record_stage "compare" pass "$COMPARE"

if [ -x "$RUNLEDGER_BIN" ]; then
  RUNLEDGER_DIR="$LEDGER_DIR" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" compare --task "$TASK_NAME" > "$RUN_DIR/runledger-compare.txt" 2>&1 || true
  RUNLEDGER_DIR="$LEDGER_DIR" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" report --task "$TASK_NAME" --output "$RUN_DIR/runledger-report.md" > "$LOG_DIR/runledger-report.log" 2>&1 || true
fi

REVIEW_HTML="$(node "$ROOT/scripts/generate-review-html.js" "$RUN_DIR")"
record_stage "review-html" pass "$REVIEW_HTML"

cat >> "$SUMMARY" <<EOF

## Totals

- Passed stages: $PASS_COUNT
- Warning stages: $WARN_COUNT
- Failed stages: $FAIL_COUNT

## Key Artifacts

- Compare: \`$COMPARE\`
- Raw metrics: \`$RUN_DIR/raw/metrics.json\`
- Muzzle metrics: \`$RUN_DIR/muzzle/metrics.json\`
- RunLedger report: \`$RUN_DIR/runledger-report.md\`
- Review dashboard: \`$REVIEW_HTML\`
- Muzzle logs: \`$RUN_DIR/.muzzle/logs\`

EOF

cat "$COMPARE"
echo
echo "Review dashboard: $REVIEW_HTML"
echo "Summary: $SUMMARY"

if [ "$FAIL_COUNT" -gt 0 ]; then
  exit 1
fi

exit 0
