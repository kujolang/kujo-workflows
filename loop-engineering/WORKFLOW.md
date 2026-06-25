# Loop Engineering — Workflow Definition

> Portable "Goal → Context → Agent → Evaluation → Stop" loop for autonomous and
> semi-autonomous agents. System-agnostic and decentralized. This document is the
> canonical, agent-readable specification; [`loop.spec.yml`](loop.spec.yml) is the
> machine-readable companion.

---

## Name

`loop-engineering` (a.k.a. the self-driving task loop)

## Purpose

Let an agent or agent system repeatedly work toward a **scoped objective**: it
fetches and refreshes context, chooses the next action, makes a small reviewable
change, evaluates the result, records the decision, and either continues or stops.
The loop is **bounded by design** — it stops on success, repeated failure, scope
expansion, a required human approval, or a spent budget.

It exists to convert "let the agent run until it's done" into a controlled cycle
with explicit goals, fetchable context, mandatory evaluation, and a decision
ledger that both humans and other agents can inspect.

## When To Use It

Use Loop Engineering when:

- A task is large enough to need **multiple steps** but should still produce small, reviewable changes.
- You want an agent to **self-correct** using tests/CI/eval rather than one-shot output.
- The work may run **unattended** (CI, scheduled jobs, background runners) and must not run away.
- You want a **portable** loop that behaves the same across local CLI harnesses, repo bots, CI, and future orchestration layers.

Do **not** use it when:

- The task is a single deterministic command (use a plain script or the relevant single-tool kit).
- The objective cannot be expressed as measurable success criteria (define a Spec first).
- There is no evaluation signal available and none can be created (the loop has no stop signal — add a gate or keep a human in the loop every iteration).

## Required Inputs

| Input | Description |
| --- | --- |
| `objective` | One sentence: what "done" means. |
| `success_criteria` | Verifiable conditions that mark success (map to eval gates). |
| `constraints` | Hard limits: files/paths off-limits, APIs not to call, budgets, style rules. |
| `allowed_actions` | The action vocabulary the agent may use (e.g. edit code, run tests, open PR, query RAG). Anything not listed is disallowed. |
| `stop_conditions` | Explicit termination rules (see Stop Conditions). At minimum a `max_iterations` and a `max_no_progress` bound. |
| `repo_or_workspace` | The working location (a repo, a directory, a service workspace). |

## Optional Inputs

| Input | Description |
| --- | --- |
| `human_approval_gates` | Points where the loop must pause for human sign-off. |
| `context_sources` | Declared sources to fetch from (issues/PRs, logs, metrics, docs, RAG/MCP servers). |
| `subagent_roles` | Named roles the loop may delegate to (see Agent Roles). |
| `budget` | Caps on iterations, wall-clock, tokens, or cost. |
| `priority` / `tags` | Routing and reporting metadata. |
| `resume_from` | A prior run id to resume an interrupted loop. |

## Required Tools / Capabilities

The loop needs **five capabilities**. Each is an adapter; any implementation that
satisfies the contract works. The Kujo-native binding is listed first, followed by
the generic fallback so the loop stays portable.

| Capability | What it must do | Kujo binding | Generic fallback |
| --- | --- | --- | --- |
| **goal** | Produce/validate a task contract with success criteria and eval requirements. | `spec` (`.spec.yml`), `runledger` (open run) | A YAML/JSON contract file + any task tracker |
| **context** | Fetch & refresh only the relevant context; compress noisy output. | `scout`, `scent`, `packwrite`, `muzzle`, `casefile`, MCP/RAG | `grep`/`git`/file reads + any retrieval API |
| **act** | Choose and apply one scoped action; optionally delegate. | `agents-sdk`, `dispatch` | Any model + tool runner |
| **evaluate** | Run gates and return pass/fail/stall with evidence. | `eval`, `shipcheck`, `changebucket`, `lens`, tests/CI | Test runner + lint/type + CI exit codes |
| **record** | Append decisions, evidence, and metrics to a durable ledger. | `runledger`, `watchdog` | An append-only log file + any telemetry sink |

A bare-bones run needs only `bash` and a shell; the reference driver ships with
no-op default adapters so the control flow is demonstrable with zero dependencies.

## Agent Roles

Roles are optional; a single agent can play all of them. Delegation is encouraged
when a subtask is well-scoped and independently verifiable.

| Role | Responsibility |
| --- | --- |
| **driver** | Owns the loop: reads the goal, sequences iterations, enforces stop conditions. |
| **context-builder** | Fetches/refreshes/compresses context for the next action. |
| **worker** | Performs the scoped action (edit, generate, run). May be a delegated subagent. |
| **evaluator** | Runs gates and returns an explicit verdict with evidence. Should be independent of the worker where possible. |
| **reviewer (human or agent)** | Approves at human approval gates and risky-action gates. |

Delegation rule: only delegate a subtask that (a) fits inside the current
`allowed_actions`, (b) has its own verifiable check, and (c) reports a structured
result back to the driver. Delegated work counts against the same budget.

## Loop Steps

### Step 0 — Initialize (once)

1. Resolve the **goal** into a task contract (`spec` validate, or load `loop.spec.yml`).
2. Open a **run record** (`runledger`) and capture run id, goal hash, budget, and stop conditions.
3. Snapshot the starting state (git rev, workspace digest) for blast-radius comparison.

### Step 1 — Build / refresh context (every iteration, fetch-on-demand)

- Pull **only** what the next action needs: relevant files, prior decisions from the ledger, issue/task/PR text, recent logs/errors/test failures, metrics/analytics if available, repo rules, human notes.
- Use `scout` for codebase structure, `scent` for task-scoped context with provenance/redaction, RAG/MCP for external knowledge, `casefile` for prior failure evidence.
- **Compress** noisy command output with `muzzle`; summarize long context rather than dumping it. Re-fetch instead of trusting stale context after each change.

### Step 2 — Choose the next action

- The driver/worker picks **one** scoped action from `allowed_actions` that is the clearest justified next step toward the goal.
- If the next action requires expanding scope or touching disallowed areas → **do not act**; raise a scope-expansion stop (see Stop Conditions).
- If the action is risky (deploy, data migration, external publish, irreversible delete) → route to a **human approval gate** before acting.

### Step 3 — Make scoped progress

- Apply the smallest reviewable change that advances the goal.
- Prefer a single coherent diff per iteration; avoid bundling unrelated edits.
- Optionally delegate to a `worker` subagent under the delegation rule above.

### Step 4 — Evaluate

- Run the eval gates relevant to the change (see Evaluation Gates). Always re-read updated context (test output, diffs) through the context adapter.
- Produce an explicit verdict: **pass**, **fail**, or **stall** (no measurable progress vs. previous iteration), with evidence paths.

### Step 5 — Record

- Append to the ledger: iteration number, chosen action, diff/blast-radius summary, eval verdict, evidence links, and the justification for continuing or stopping.
- Update metrics (iterations used, budget remaining) via the record adapter / `watchdog`.

### Step 6 — Stop or continue

- Evaluate **stop conditions** (below). If any fire → stop and write the final packet.
- Otherwise continue **only when the next action is clearly justified** by the latest evaluation. Ambiguity is a stall, not a license to keep going.

## Evaluation Gates

Gates are the loop's stop signal. Configure the subset that applies; an iteration
that changes nothing verifiable is a stall.

| Gate | Tool binding | Fires when |
| --- | --- | --- |
| Tests | `eval`, project test runner | Required tests must pass for success. |
| CI | CI provider exit status (any) | CI must be green before ship. |
| Lint / type checks | project linters/type checker | No new violations introduced. |
| Visual / UI QA | `lens` | UI changed; visual flow must pass and produce proof. |
| Blast radius / diff review | `changebucket` | Change size/risk must stay within constraints. |
| Release readiness | `shipcheck` | All ship blockers cleared before a ship action. |
| LLM-as-judge | `eval` (judge mode) | **Only** for subjective criteria with no deterministic check, and never as the sole gate for shipping. |

Rule: deterministic gates (tests, types, CI, blast radius) take precedence. Use an
LLM judge to supplement, not to override, a failing deterministic gate.

## Stop Conditions

The loop **must** stop when any of these fire:

1. **Success** — all `success_criteria` satisfied and required gates pass.
2. **Repeated failure** — the same gate fails `max_consecutive_failures` times (default 3) without a changed root cause.
3. **No progress / stall** — `max_no_progress` iterations (default 2) with no measurable improvement in eval signal.
4. **Scope expansion** — the only viable next action requires going outside `allowed_actions`/`constraints`.
5. **Approval required** — a human approval gate or risky-action gate is reached.
6. **Budget exhausted** — `max_iterations`, wall-clock, token, or cost cap reached.
7. **External error** — environment/tooling failure the loop cannot recover from; capture with `casefile` and stop.

On every stop the loop writes a final packet (verdict + ledger + evidence) and, if
not successful, a clear statement of what is blocking and what a human/next run
should do.

## Human Approval Gates

Approval gates pause the loop and require explicit sign-off (human, or a designated
reviewer agent under policy). Default gates:

- **Before any risky/irreversible action**: deploy, data migration, deletion of data the loop did not create, sending external messages, spending money, or changing production config.
- **Before scope expansion**: any request to widen `allowed_actions` or touch off-limits paths.
- **Before ship**: when `shipcheck`/CI is green but policy requires a human to release.
- **Custom gates** from `human_approval_gates` (e.g. "after design doc", "before merging to default branch").

Approval is recorded in the ledger with who/what approved and the decision
(`approved` / `rejected` / `request_changes`). A rejected gate is a stop, not a retry.

## Expected Outputs

Every run produces a reviewable packet:

- `SUMMARY.md` — verdict, goal, iterations used, gates run, stop reason, next steps.
- `ledger.tsv` (and/or `runledger` record) — per-iteration action, verdict, evidence, justification.
- `iterations/<n>/` — per-iteration artifacts: chosen action, diff/blast-radius, eval output, context snapshot.
- Evidence artifacts from the bound tools (eval reports, `lens` proof, `changebucket` report, `casefile` bundles on failure).
- An explicit **stop reason** and, on non-success, a blocking statement and recommended next action.

## Failure Modes

| Failure mode | Mitigation in this workflow |
| --- | --- |
| Runaway loop (never stops) | Mandatory `max_iterations` + budget; stall detection. |
| Silent scope creep | Allowed-actions vocabulary; scope-expansion stop + approval gate. |
| Shipping unverified work | Evaluation is mandatory before continue/ship; deterministic gates precede judges. |
| Context bloat / token blowup | Fetch-on-demand context; `muzzle`/summarization; re-fetch instead of accumulating. |
| Thrashing on the same failure | `max_consecutive_failures` stop; require a changed root cause to retry. |
| Irreversible mistakes | Risky-action approval gates; snapshot for blast-radius diffing. |
| Lost reasoning / unauditable run | Decision ledger + per-iteration evidence + `runledger`/`watchdog`. |
| Tool/provider outage | External-error stop with `casefile` capture; resumable via `resume_from`. |

## Example Use Cases

- **Verified bug fix**: loop until the failing test/visual flow passes and blast radius stays small, then pause for ship approval.
- **Flaky test stabilization**: iterate on a test, re-running it N times per iteration as the eval gate, stop when stable or budget hit.
- **Dependency/version bump**: apply a bump, run tests + `changebucket`, stop on green or first incompatibility.
- **Docs/content generation from real examples**: generate, validate against source, stop when all sections cite verified sources.
- **Scheduled maintenance agent**: nightly loop with a hard budget that opens a PR and stops at the merge-approval gate.

## Example Invocation / Task Prompt

Reference driver (portable, no dependencies):

```bash
LOOP_OBJECTIVE="Make the checkout promo-code apply on first tap on mobile" \
LOOP_MAX_ITERATIONS=5 \
LOOP_EVAL_CMD="bash run-tests.sh" \
bash scripts/run-workflow.sh
```

Agent task prompt (drop into any harness):

```text
You are the DRIVER of a bounded Loop Engineering run. Load the goal from
loop.spec.yml. Each iteration: (1) refresh only the context the next action needs,
(2) choose ONE allowed action that is clearly justified, (3) make the smallest
reviewable change, (4) run the evaluation gates and record an explicit verdict with
evidence, (5) check stop conditions. STOP immediately on success, on the same gate
failing 3× without a new root cause, on a stall of 2 iterations, on any need to go
outside allowed_actions, on reaching a human approval gate, or on budget exhaustion.
Never expand scope silently. Never continue without a justified next action. Write a
final SUMMARY with the verdict, stop reason, and recommended next step.
```

Kujo-wired example (bind real tools via env, see HOWTO):

```bash
KUJO_REPOS=/path/to/kujo-repos \
LOOP_CONTEXT_ADAPTER="scout" \
LOOP_EVAL_ADAPTER="eval" \
LOOP_RECORD_ADAPTER="runledger" \
bash scripts/run-workflow.sh
```

## Notes On Portability

This workflow is decentralized by construction:

- **No platform lock-in.** It assumes neither GitHub nor GitLab; "open a PR" / "CI is green" are adapter actions, not built-ins. Any host, runner, model provider, CI, or hosting target plugs in behind the five capabilities.
- **Adapters, not assumptions.** Goal / context / act / evaluate / record are contracts. Kujo bindings (`spec`, `scout`, `agents-sdk`, `dispatch`, `eval`, `runledger`, …) are the recommended implementation, but a pure-shell or third-party implementation is valid.
- **Runs anywhere.** Local CLI harnesses, repo-based agent systems, CI-driven automation, scheduled jobs, future Kujo/BZBY orchestration layers, and human-in-the-loop review systems all consume the same `loop.spec.yml` contract.
- **Graceful degradation.** Missing optional tools downgrade a gate to a warning or fall back to the generic implementation; they never silently disable a stop condition. The bounded control flow and the decision ledger are always present.
- **Human-and-agent readable.** The contract is plain YAML/Markdown so a person can audit it and an agent can execute it without bespoke parsing.
