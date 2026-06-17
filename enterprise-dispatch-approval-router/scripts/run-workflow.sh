#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-/Users/robertdevore/2026/Kujolang/kujo-repos}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
DISPATCH_REPO="${DISPATCH_REPO:-$KUJO_REPOS/dispatch}"
TOPIC="${DISPATCH_TOPIC:-Enterprise CRM rollout approval: review migration safety, auth resilience, and error-budget risk.}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR:-$WORKFLOW_DIR/.runs/$STAMP}"
LOG_DIR="$RUN_DIR/logs"

mkdir -p "$LOG_DIR"

if [[ ! -x "$KUJO_BIN" ]]; then
  echo "Missing executable Kujo runtime: $KUJO_BIN" >&2
  exit 1
fi

if [[ ! -f "$DISPATCH_REPO/dispatch.kujo" ]]; then
  echo "Missing Dispatch repo: $DISPATCH_REPO" >&2
  exit 1
fi

{
  echo -e "stage\tstatus\tdetail"
  echo -e "preflight\tpass\t$KUJO_BIN"
} > "$RUN_DIR/status.tsv"

cd "$DISPATCH_REPO"

"$KUJO_BIN" run --interpreter dispatch.kujo templates --json \
  > "$LOG_DIR/templates.log" 2>&1
echo -e "templates\tpass\t$LOG_DIR/templates.log" >> "$RUN_DIR/status.tsv"

DISPATCH_ALLOW_ANY_OUTPUT_ROOT=true DISPATCH_OFFLINE_FIXTURE=true \
"$KUJO_BIN" run --interpreter dispatch.kujo demo "$TOPIC" \
  --workflow crud-reliability \
  --policy-profile development \
  --yes \
  --non-interactive \
  --output-root "$RUN_DIR/dispatch" \
  > "$LOG_DIR/dispatch-demo.log" 2>&1
echo -e "dispatch-demo\tpass\t$LOG_DIR/dispatch-demo.log" >> "$RUN_DIR/status.tsv"

DISPATCH_RUN_DIR="$(find "$RUN_DIR/dispatch" -mindepth 1 -maxdepth 1 -type d -name 'run-*' | sort | tail -1)"
if [[ -z "$DISPATCH_RUN_DIR" ]]; then
  echo "Dispatch completed without a run directory" >&2
  exit 1
fi

DISPATCH_RUN_ID="$(basename "$DISPATCH_RUN_DIR")"

DISPATCH_ALLOW_ANY_OUTPUT_ROOT=true \
"$KUJO_BIN" run --interpreter dispatch.kujo runs --output-root "$RUN_DIR/dispatch" --json --diagnostics \
  > "$LOG_DIR/runs-diagnostics.json" 2>&1
echo -e "runs-diagnostics\tpass\t$LOG_DIR/runs-diagnostics.json" >> "$RUN_DIR/status.tsv"

DISPATCH_ALLOW_ANY_OUTPUT_ROOT=true \
"$KUJO_BIN" run --interpreter dispatch.kujo inspect "$DISPATCH_RUN_ID" --output-root "$RUN_DIR/dispatch" --json \
  > "$LOG_DIR/inspect.json" 2>&1
echo -e "inspect\tpass\t$LOG_DIR/inspect.json" >> "$RUN_DIR/status.tsv"

for required in "$DISPATCH_RUN_DIR/state.json" "$DISPATCH_RUN_DIR/trace.json" "$DISPATCH_RUN_DIR/trace.md" "$DISPATCH_RUN_DIR/report.md"; do
  if [[ ! -f "$required" ]]; then
    echo "Missing expected Dispatch artifact: $required" >&2
    exit 1
  fi
done
echo -e "artifact-check\tpass\t$DISPATCH_RUN_DIR" >> "$RUN_DIR/status.tsv"

cat > "$RUN_DIR/SUMMARY.md" <<EOF
# Enterprise Dispatch Approval Router Summary

Run: $STAMP

## Verdict

PASS - Dispatch produced a governed offline workflow run with state, trace, report, catalog diagnostics, and inspect output.

## Content Pillar

Enterprise AI work needs orchestration evidence: what ran, under which policy profile, where approval happened, and which artifacts prove completion.

## Key Artifacts

- Dispatch run: \`$DISPATCH_RUN_DIR\`
- Report: \`$DISPATCH_RUN_DIR/report.md\`
- Trace: \`$DISPATCH_RUN_DIR/trace.md\`
- State: \`$DISPATCH_RUN_DIR/state.json\`
- Diagnostics: \`$LOG_DIR/runs-diagnostics.json\`
- Inspect JSON: \`$LOG_DIR/inspect.json\`

## Demo Topic

$TOPIC

## Buyer Relevance

- Developers: repeatable local workflow packets.
- Agency owners: client-facing proof that work followed a process.
- Enterprise: policy profile, trace, approval, and machine-readable audit artifacts.
EOF

echo "Workflow complete: $RUN_DIR"
