# Loop Engineering HOWTO

How to adopt the portable Goal → Context → Agent → Evaluation → Stop loop in your
own system. See [`WORKFLOW.md`](WORKFLOW.md) for the full definition and
[`loop.spec.yml`](loop.spec.yml) for the machine-readable contract.

## 1. Run The Reference Driver

The driver ships with safe no-op adapters and runs with zero dependencies:

```bash
cd loop-engineering
bash scripts/run-workflow.sh
```

Then review:

```text
.runs/<timestamp>/SUMMARY.md      # verdict + stop reason + next step
.runs/<timestamp>/ledger.tsv      # per-iteration action / verdict / evidence
.runs/<timestamp>/iterations/<n>/ # context, action, eval, record logs per step
```

## 2. Define Your Goal

Copy [`loop.spec.yml`](loop.spec.yml) next to your task and edit the `goal` block:
`objective`, `success_criteria`, `constraints`, and `allowed_actions`. Keep
`allowed_actions` tight — anything not listed triggers a scope-expansion stop.

In Kujo, the goal can instead be a `spec` contract (`.spec.yml`) that `spec` can
validate and export as agent context; the loop's `success_criteria` map to that
contract's eval requirements.

## 3. Bind Adapters (optional)

The driver exposes five capabilities as overridable commands. Bind real tools by
exporting `*_CMD` variables. The evaluator's exit code is the contract: `0` = pass,
non-zero = fail.

```bash
# Example: real test gate + a context refresh step.
LOOP_OBJECTIVE="Fix failing checkout test" \
LOOP_MAX_ITERATIONS=5 \
LOOP_CONTEXT_CMD="scout map . --json > .ctx.json" \
LOOP_EVAL_CMD="bash run-tests.sh" \
bash scripts/run-workflow.sh
```

| Variable | Capability | Kujo binding | Generic |
| --- | --- | --- | --- |
| `LOOP_CONTEXT_CMD` | refresh context | `scout` / `scent` / `muzzle` | `git` + `grep` + file reads |
| `LOOP_ACT_CMD` | choose + apply one scoped action | `agents-sdk` / `dispatch` | model + tool runner |
| `LOOP_EVAL_CMD` | gate (exit 0 = pass) | `eval` / `shipcheck` / `changebucket` / `lens` | test runner / CI exit code |
| `LOOP_RECORD_CMD` | append decision | `runledger` | append-only log |

Bounds: `LOOP_MAX_ITERATIONS`, `LOOP_MAX_NO_PROGRESS`, `LOOP_MAX_CONSECUTIVE_FAILURES`.

### Wiring to local Kujo tools

```bash
KUJO_REPOS="${KUJO_REPOS:-/path/to/kujo-repos}"
KUJO_BIN="$KUJO_REPOS/kujo/target/release/kujo"

# Context: codebase map from Scout
LOOP_CONTEXT_CMD="$KUJO_BIN run --interpreter $KUJO_REPOS/scout/scout.kujo -- map ."
# Evaluate: Eval suite (or swap for shipcheck/changebucket/lens/tests)
LOOP_EVAL_CMD="$KUJO_BIN test"
# Record: RunLedger
LOOP_RECORD_CMD="$KUJO_REPOS/runledger/bin/runledger note --run loop"

export LOOP_CONTEXT_CMD LOOP_EVAL_CMD LOOP_RECORD_CMD
bash scripts/run-workflow.sh
```

Missing optional tools fall back to the generic implementation or a warning — they
never silently disable a stop condition.

## 4. Drive It With A Real Agent

The reference driver enforces the control flow but does not call a model. To run a
true autonomous loop, hand the driver's contract to your agent runtime:

1. Load `loop.spec.yml` as the goal/policy.
2. Use the agent task prompt in [`WORKFLOW.md`](WORKFLOW.md#example-invocation--task-prompt) as the driver's system instruction.
3. Implement the `act` capability with your agent + tools; keep `evaluate` independent of `act` where possible.
4. Append every decision to the ledger and honor the stop conditions verbatim.

In Kujo, `dispatch` provides the orchestration (steps, retry, approval gates,
resumable state) and `agents-sdk` provides the agent/worker/handoff primitives.

## 5. Run It Unattended

- **CI**: invoke `scripts/run-workflow.sh` as a job step; the script exits `0` on any clean stop, so gate the pipeline on the `SUMMARY.md` verdict, not just exit code.
- **Scheduled**: wrap it in a cron/routine with a hard `LOOP_MAX_ITERATIONS` and a `before_ship` approval gate so the job opens a change request but never merges itself.
- **Resume**: pass `RESUME_FROM=<timestamp>` semantics through your record adapter to continue an interrupted run (the driver writes everything needed to resume into the run dir).

## 6. Human-In-The-Loop

Approval gates pause the loop. When a risky action, scope expansion, or ship is
reached, the loop records the gate and stops with `request_changes`/`approved`/
`rejected`. A rejected gate is a **stop**, not a retry. Keep these gates in
`loop.spec.yml` so reviewers can see exactly when they will be asked.

## 7. Troubleshooting

- **Loop "fails" but exit code is 0** — by design: a clean stop (stall, budget, blocked) is a valid outcome. Read the verdict in `SUMMARY.md`.
- **Loop never stops in your runtime** — you skipped a stop condition; the contract requires at least `max_iterations` and `max_no_progress`.
- **Eval always passes/fails** — confirm your `LOOP_EVAL_CMD` returns a real exit code (0 = pass).
- **Context keeps growing** — you are dumping instead of fetching on demand; add `muzzle`/summarization and re-fetch each iteration.
