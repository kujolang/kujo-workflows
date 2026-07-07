# Loop Engineering HOWTO

How to adopt the portable Goal → Context → Agent → Evaluation → Stop loop in your
own system. See [`WORKFLOW.md`](WORKFLOW.md) for the full definition and
[`loop.spec.yml`](loop.spec.yml) for the machine-readable contract.

## 1. Initialize A Target Repo

From any repo:

```bash
/path/to/loop-engineering/scripts/init-repo-loop.sh
```

This creates:

```text
.loop-engineering/
  loop.yml
  ledger.tsv
  SUMMARY.md
  iterations/
  blockers.md
  evidence/
```

The generated `loop.yml` includes the task objective, optional checklist file,
stop bounds, allowed/blocked actions, eval gates, commit policy, and optional
Strata memory hook.

## 2. Run A Real Config

Edit `.loop-engineering/loop.yml`, then run:

```bash
/path/to/loop-engineering/scripts/run-workflow.sh --config .loop-engineering/loop.yml
```

Running `scripts/run-workflow.sh` without `--config`, `--checklist`, or `--demo`
fails with usage. The demo evaluator no longer runs by default.

## 3. Checklist Mode

Classify Markdown task lists before acting:

```bash
/path/to/loop-engineering/scripts/run-workflow.sh --checklist docs/some-checklist.md
```

Items are written to `.loop-engineering/checklist.tsv` as one of:
`local-fixable`, `already-done`, `external-blocked`, `policy-blocked`,
`requires-human-approval`, `out-of-repo`, `needs-contract-first`, or
`needs-release-pipeline`. The summary keeps non-local items in `Remaining` and
records external blockers with evidence in `blockers.md`.

## 4. Bind Adapters (optional)

The driver can run an action command before gates:

```bash
LOOP_ACT_CMD="your-agent-or-script-here" \
/path/to/loop-engineering/scripts/run-workflow.sh --config .loop-engineering/loop.yml
```

Eval gates come from `loop.yml`. Each gate has an `id`, `command`, `required`,
and optional `when_files_match` globs. Required failures stop the loop; known
registry, SSH, network, approval, and release-pipeline failures are normalized
into structured blocker records.

## 5. Commit And Push Policy

Commits are opt-in:

```yaml
commit:
  enabled: true
  strategy: small_meaningful
  push: false
```

When `push: true`, a push failure is recorded as an external blocker instead of
being reported as a workflow success.

## 6. Optional Strata Hook

The config can request a final Strata handoff:

```yaml
memory:
  enabled: true
  provider: strata
  project: "Agent Notes"
  mode: consolidate
  retrieval_tests: true
```

If `LOOP_MEMORY_CMD` is set, the driver invokes it with the generated memory
request file. Otherwise it writes `.loop-engineering/evidence/strata-memory-request.md`
for the agent or host runtime to fulfill.

## 7. Drive It With A Real Agent

The reference driver enforces the control flow but does not call a model. To run a
true autonomous loop, hand the driver's contract to your agent runtime:

1. Load `loop.spec.yml` as the goal/policy.
2. Use the agent task prompt in [`WORKFLOW.md`](WORKFLOW.md#example-invocation--task-prompt) as the driver's system instruction.
3. Implement the `act` capability with your agent + tools; keep `evaluate` independent of `act` where possible.
4. Append every decision to the ledger and honor the stop conditions verbatim.

In Kujo, `dispatch` provides orchestration and `agents-sdk` provides worker and
handoff primitives. Muzzle remains optional; missing Muzzle is not a blocker for
repo-local initialization or evidence capture.

## 8. Run It Unattended

- **CI**: invoke `scripts/run-workflow.sh` as a job step; the script exits `0` on any clean stop, so gate the pipeline on the `SUMMARY.md` verdict, not just exit code.
- **Scheduled**: wrap it in a cron/routine with a hard `LOOP_MAX_ITERATIONS` and a `before_ship` approval gate so the job opens a change request but never merges itself.
- **Resume**: pass `RESUME_FROM=<timestamp>` semantics through your record adapter to continue an interrupted run (the driver writes everything needed to resume into the run dir).

## 9. Human-In-The-Loop

Approval gates pause the loop. When a risky action, scope expansion, or ship is
reached, the loop records the gate and stops with `request_changes`/`approved`/
`rejected`. A rejected gate is a **stop**, not a retry. Keep these gates in
`loop.spec.yml` so reviewers can see exactly when they will be asked.

## 10. Troubleshooting

- **Loop "fails" but exit code is 0** — by design: a clean stop (stall, budget, blocked) is a valid outcome. Read the verdict in `SUMMARY.md`.
- **The driver only prints usage** — pass `--config`, `--checklist`, or `--demo`; there is no implicit placeholder run.
- **Loop never stops in your runtime** — you skipped a stop condition; the contract requires at least `max_iterations` and `max_no_progress`.
- **Eval always passes/fails** — confirm each `eval_gates.command` returns a real exit code (`0` = pass).
- **Context keeps growing** — you are dumping instead of fetching on demand; add `muzzle`/summarization and re-fetch each iteration.
