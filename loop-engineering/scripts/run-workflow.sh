#!/usr/bin/env bash
set -euo pipefail

# Loop Engineering — portable reference driver.
#
# Implements the bounded Goal -> Context -> Agent -> Evaluation -> Stop control
# flow from WORKFLOW.md / loop.spec.yml. Ships with safe no-op default adapters so
# it runs anywhere bash is available — no Kujo runtime, model key, or network
# required. Override any adapter with a *_CMD environment variable to wire real
# tooling (see HOWTO.md). This driver demonstrates and enforces the control flow
# and stop conditions; it does not itself call a model.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR:-$WORKFLOW_DIR/.runs/$STAMP}"
ITER_DIR="$RUN_DIR/iterations"
LEDGER="$RUN_DIR/ledger.tsv"
SUMMARY="$RUN_DIR/SUMMARY.md"

# ---- Goal / bounds (override per task) ------------------------------------
LOOP_OBJECTIVE="${LOOP_OBJECTIVE:-Demonstrate the bounded loop control flow and stop conditions.}"
LOOP_MAX_ITERATIONS="${LOOP_MAX_ITERATIONS:-8}"
LOOP_MAX_NO_PROGRESS="${LOOP_MAX_NO_PROGRESS:-2}"
LOOP_MAX_CONSECUTIVE_FAILURES="${LOOP_MAX_CONSECUTIVE_FAILURES:-3}"

# ---- Adapters (override with *_CMD to bind real tools) --------------------
# context: refresh only what the next action needs (scout/scent/grep/...).
LOOP_CONTEXT_CMD="${LOOP_CONTEXT_CMD:-}"
# act: choose + apply one scoped action (agents-sdk/dispatch/model+tools/...).
LOOP_ACT_CMD="${LOOP_ACT_CMD:-}"
# evaluate: exit 0 = pass, non-zero = fail (eval/tests/ci/...).
LOOP_EVAL_CMD="${LOOP_EVAL_CMD:-}"
# record: append a decision line (runledger/append log/...).
LOOP_RECORD_CMD="${LOOP_RECORD_CMD:-}"

# Built-in demo evaluator: simulate measurable progress so the success stop is
# observable with zero dependencies. Ignored when LOOP_EVAL_CMD is set.
LOOP_DEMO_SUCCESS_AT="${LOOP_DEMO_SUCCESS_AT:-2}"

mkdir -p "$ITER_DIR"
printf 'iteration\taction\tverdict\tprogress\tevidence\tjustification\n' > "$LEDGER"

# Default adapters (no-ops that are honest about being placeholders).
default_context() { echo "fetch-on-demand context refresh (placeholder adapter)"; }
default_act()     { echo "chose scoped action: advance-toward-goal (placeholder adapter)"; }
default_record()  { :; }

# Default evaluator returns pass once demo progress reaches the threshold.
default_eval() {
  local n="$1"
  if [ "$n" -ge "$LOOP_DEMO_SUCCESS_AT" ]; then return 0; fi
  return 1
}

run_adapter() { # name cmd logfile fallback-fn [args...]
  local name="$1" cmd="$2" log="$3" fallback="$4"; shift 4
  if [ -n "$cmd" ]; then
    printf '$ %s\n' "$cmd" > "$log"
    bash -lc "$cmd" >> "$log" 2>&1
    return $?
  fi
  "$fallback" "$@" > "$log" 2>&1
  return $?
}

STOP_REASON=""
VERDICT="incomplete"
PROGRESS=0
PREV_PROGRESS=-1
NO_PROGRESS=0
CONSEC_FAIL=0
ITERS_USED=0

echo "Loop Engineering driver"
echo "  objective : $LOOP_OBJECTIVE"
echo "  bounds    : max_iter=$LOOP_MAX_ITERATIONS no_progress=$LOOP_MAX_NO_PROGRESS consec_fail=$LOOP_MAX_CONSECUTIVE_FAILURES"
echo "  run dir   : $RUN_DIR"

for ((n=1; n<=LOOP_MAX_ITERATIONS; n++)); do
  ITERS_USED="$n"
  step="$ITER_DIR/$n"
  mkdir -p "$step"

  # Step 1 — context (fetch/refresh on demand)
  run_adapter context "$LOOP_CONTEXT_CMD" "$step/context.log" default_context || true

  # Step 2/3 — choose + make scoped progress
  run_adapter act "$LOOP_ACT_CMD" "$step/action.log" default_act || true
  action="advance-toward-goal"

  # Step 4 — evaluate (pass/fail/stall)
  if [ -n "$LOOP_EVAL_CMD" ]; then
    if run_adapter evaluate "$LOOP_EVAL_CMD" "$step/eval.log" true; then
      eval_ok=0
    else
      eval_ok=1
    fi
    # External evaluators don't emit a progress scalar; derive a coarse one.
    [ "$eval_ok" -eq 0 ] && PROGRESS=$((PROGRESS + 1))
  else
    PROGRESS="$n"
    if default_eval "$n"; then eval_ok=0; else eval_ok=1; fi
    printf 'demo evaluator: progress=%s success_at=%s -> %s\n' \
      "$n" "$LOOP_DEMO_SUCCESS_AT" "$([ "$eval_ok" -eq 0 ] && echo pass || echo fail)" \
      > "$step/eval.log"
  fi

  # Stall detection: no measurable improvement vs previous iteration.
  if [ "$PROGRESS" -le "$PREV_PROGRESS" ]; then
    NO_PROGRESS=$((NO_PROGRESS + 1))
  else
    NO_PROGRESS=0
  fi
  PREV_PROGRESS="$PROGRESS"

  if [ "$eval_ok" -eq 0 ]; then
    verdict="pass"; CONSEC_FAIL=0
  else
    verdict="fail"; CONSEC_FAIL=$((CONSEC_FAIL + 1))
  fi

  # Step 5 — record decision + evidence
  justification="continue: next action justified by eval signal"
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$n" "$action" "$verdict" "$PROGRESS" "iterations/$n/eval.log" "$justification" >> "$LEDGER"
  run_adapter record "$LOOP_RECORD_CMD" "$step/record.log" default_record || true
  echo "  iter $n: action=$action verdict=$verdict progress=$PROGRESS"

  # Step 6 — stop conditions
  if [ "$verdict" = "pass" ] && [ "$eval_ok" -eq 0 ]; then
    STOP_REASON="success: success criteria satisfied and required gates passed"
    VERDICT="success"; break
  fi
  if [ "$CONSEC_FAIL" -ge "$LOOP_MAX_CONSECUTIVE_FAILURES" ]; then
    STOP_REASON="repeated-failure: same gate failed ${CONSEC_FAIL}x without a new root cause"
    VERDICT="blocked"; break
  fi
  if [ "$NO_PROGRESS" -ge "$LOOP_MAX_NO_PROGRESS" ]; then
    STOP_REASON="stall: no measurable progress for ${NO_PROGRESS} iterations"
    VERDICT="blocked"; break
  fi
done

if [ -z "$STOP_REASON" ]; then
  STOP_REASON="budget-exhausted: reached max_iterations ($LOOP_MAX_ITERATIONS)"
  VERDICT="blocked"
fi

# Final packet
NEXT_STEP="None — loop succeeded."
if [ "$VERDICT" != "success" ]; then
  NEXT_STEP="Review ledger.tsv, address the blocking gate, then resume (RESUME_FROM=$STAMP) or hand to a human."
fi

cat > "$SUMMARY" <<EOF
# Loop Engineering Run Summary

Run: $STAMP

## Verdict

$( [ "$VERDICT" = "success" ] && echo "SUCCESS" || echo "STOPPED (not successful)" ) — the bounded loop terminated on an explicit stop condition.

## Goal

$LOOP_OBJECTIVE

## Stop Reason

$STOP_REASON

## Loop Stats

| Metric | Value |
|---|---|
| Iterations used | $ITERS_USED / $LOOP_MAX_ITERATIONS |
| Final verdict | $VERDICT |
| Consecutive failures at stop | $CONSEC_FAIL |
| No-progress streak at stop | $NO_PROGRESS |

## Stop Conditions Enforced

- success, repeated-failure (>= $LOOP_MAX_CONSECUTIVE_FAILURES), stall (>= $LOOP_MAX_NO_PROGRESS), budget (max_iterations $LOOP_MAX_ITERATIONS)
- scope-expansion and human-approval gates are enforced by the action adapter when bound to real tools (see WORKFLOW.md)

## Key Artifacts

- Decision ledger: \`ledger.tsv\`
- Per-iteration evidence: \`iterations/<n>/\`
- This summary: \`SUMMARY.md\`

## Recommended Next Step

$NEXT_STEP

## Notes

This run used $( [ -n "$LOOP_EVAL_CMD" ] && echo "the supplied LOOP_EVAL_CMD evaluator" || echo "the built-in demo evaluator" )
and $( { [ -n "$LOOP_CONTEXT_CMD$LOOP_ACT_CMD$LOOP_RECORD_CMD" ] && echo "one or more bound adapters"; } || echo "default placeholder adapters" ).
Bind Kujo tooling via *_CMD env vars to turn this into a real autonomous loop.
EOF

echo "Workflow complete: $RUN_DIR"
echo "Verdict: $VERDICT — $STOP_REASON"
[ "$VERDICT" = "success" ] || exit 0  # a clean stop is a valid, expected outcome
