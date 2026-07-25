# Weekly Kujo Workflows Audit - 2026-07-25

Audit ID: `kujo-workflows-audit-2026-07-25`
Captured: `2026-07-25T06:08:02-04:00` / `2026-07-25T10:08:02Z`
Automation ID: `weekly-kujo-worklflows-audit`

## Scope

This refresh audited the workflow catalog against sibling Kujo repositories under `/Users/robertdevore/2026/Kujolang/kujo-repos`, prioritizing repositories changed during the last 7-10 days and the Relay partial-verification boundary from the 2026-07-18 audit.

Recent repository evidence inspected:

| Repository | Branch | HEAD | Disposition |
| --- | --- | --- | --- |
| kujo-skills | `weekly-kujo-skills-audit-2026-07-04` | `b0233fd` | Skill source pointer updated in the compatibility matrix; 45 existing workflow-skill relationships still validate. |
| ai-sdk | `main` | `da59fa1` | Current benchmark/showcase relationships preserved; stream usage telemetry and streamed tool-call fixes remain SDK-owned contracts, not workflow-catalog drift. |
| ai-chat | `main` | `b91718d` | Current Watchdog showcase relationship preserved; long-running stream/tool-continuation fixes, browser tools, Web Search, and benchmark panes remain deferred from catalog promotion until a workflow contract exists. |
| watchdog | `main` | `c5d77ba` | Current showcase relationship preserved; token visibility, dashboard backup/history work, named upstreams, and agent insights are compatible additions. |
| relay | `main` | `66228c2` | Relay lifecycle workflow preserved, but provider-tool smoke and aggregate acceptance remain partial/unresolved in sibling Relay verification. |
| changebucket | `main` | `2ff156a` | CLI parser repair is compatible with existing ChangeBucket workflow usage. |
| eval | `main` | `0557e22` | Command-policy gate repair is compatible with existing Eval workflow usage. |
| fence | `main` | `c07df1a` | CLI parsing repair validated by sibling smoke; no current workflow record needs migration. |
| patchbrief | `main` | `8a49e9a` | CLI parsing repair is compatible with existing PatchBrief workflow usage. |
| rag | `main` | `4534e66` | Release-evaluation gate passed; `rag-enterprise-knowledge-gate` remains compatible-but-under-tested pending broader consumer evidence. |
| shipcheck | `main` | `3b098ed` | CLI helper repair validated by sibling contract test; existing workflow usage preserved. |
| spec | `main` | `b7018fd` | Runtime-banner parity verifier tolerance is compatible with Spec workflow usage. |
| kujo | `main` | `86ca4cf` | VM and stdlib release-contract stabilization supports current workflow validators; no catalog schema drift found. |
| workcell | `main` | `5ada0b6` | Docker build-context artifact ignore does not alter `workcell-execution-gate` contracts. |
| tribunal | `codex/tribunal-v0.7-enterprise-review` | `5859c6c` | Input-boundary hardening is compatible with the advisory `tribunal-decision-gate`; binding policy remains deferred. |

## Workflow Records Updated

- `docs/audit/workflow-catalog.json`: audit ID refreshed to `kujo-workflows-audit-2026-07-25`.
- `docs/audit/skill-compatibility-matrix.json`: audit ID refreshed and `kujo-skills` source commit updated to `b0233fdfba4b589429f1bd4b73d11581c0d3985c`.
- `docs/audit/tool-integration-matrix.json`: audit ID refreshed; AI SDK, AI Chat, Watchdog, and Relay current evidence/risk text updated from sibling repository proof.
- `docs/audit/README.md`, `docs/audit/VERIFICATION.md`, and `docs/audit/DEFERRED_OPPORTUNITIES.md`: latest weekly scope, validation, and Relay unresolved boundary recorded.

## Workflows Confirmed Current

- `agency-runner`
- `agency-verified-fix-loop`
- `ai-sdk-muzzle-benchmark`
- `ai-sdk-watchdog-showcase`
- `casefile-incident-evidence-packet`
- `docsgen-repo-contract-runner`
- `enterprise-dispatch-approval-router`
- `feature-card-workflow`
- `howl-content-factory`
- `loop-engineering`
- `mcp-agent-gateway-review`
- `rag-enterprise-knowledge-gate`
- `tribunal-decision-gate`
- `relay-lifecycle-handoff`
- `workcell-execution-gate`

## Compatibility Disposition

- Added: no new supported workflow/tool compatibility relationship.
- Changed: `relay` tool-matrix record now records the unresolved provider-tool smoke exit and aggregate acceptance failure boundary.
- Changed: AI SDK, AI Chat, and Watchdog tool-matrix records now cite current repository heads and recently verified contract surfaces.
- Preserved: 45 workflow-to-skill relationships; validator still reports 36 compatible and 9 compatible-but-under-tested.
- Deferred: AI Chat benchmark/browser/Web Search workflow promotion remains deferred until a dedicated workflow runner, fixture set, validation contract, and live/mock boundary exist.
- Deferred: Relay external delivery and Workcell/Relay/Tribunal composition remain deferred until shared contracts and clean sibling acceptance evidence exist.
- Deferred: CMS and CMS Experience remain outside the active workflow catalog until a workflow kit references their delivery, auth, or content-publication contracts.
- Removed: none.

## Validation

Passed:

- `python3 scripts/validate_catalog.py --json`
- `python3 scripts/validate_contracts.py`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `bash tests/validate_catalog.sh`
- `python3 -m json.tool` over the audit JSON files
- `bash -n` over tracked repository shell scripts
- `KUJO_BIN=/Users/robertdevore/2026/Kujolang/kujo-repos/kujo/target/release/kujo bash tests/skill_relationship_contracts.sh`
- `git diff --check`
- Sibling AI Chat `npm test` (203 tests)
- Sibling AI SDK `bash scripts/release_quality_gates.sh` with explicit `KUJO_BIN` (104 aggregate tests; live provider smoke used documented no-key skip)
- Sibling AI SDK `bash scripts/supply_chain_policy_check.sh`
- Sibling Watchdog proxy/API/frontend focused checks with explicit `KUJO_BIN`
- Sibling Fence `bash tests/cli_smoke.sh` with explicit `KUJO_BIN` (20 checks)
- Sibling ShipCheck `tests/cli-output-contract.sh` with explicit `KUJO`
- Sibling Eval `bash scripts/supply_chain_policy_check.sh` with explicit `KUJO_BIN` (9 checks)
- Sibling Spec `bash scripts/verify_test_runtime_parity.sh` with explicit `KUJO_BIN`
- Sibling RAG `kujo run scripts/run_release_evaluation.kujo --interpreter` with explicit `KUJO_BIN` (12/12 release-eval cases)

## Partial Verification Boundaries

- AI Chat live benchmark execution was not run because it requires a running AI Chat server, API auth token, selected pane profile, and provider credentials.
- AI Chat browser and Web Search surfaces were covered by unit/integration tests and repo evidence; live Web Search remained configuration-gated.
- Watchdog live named-upstream behavior was not run against external credentials; focused local proxy/API/frontend checks passed.
- AI SDK live-provider behavior was not run because provider keys were not configured; the release gate took the documented no-key skip path.
- Relay provider-generated tools remain partial: `tests/relay_provider_tool_smoke.sh` printed `PASS relay provider tool smoke` but did not exit cleanly before interruption.
- Relay aggregate acceptance did not pass: `tests/relay_acceptance.sh` reached `relay_input_boundary_smoke.sh`, then stopped at `relay_lock_stress_smoke.sh`; focused tracing showed `examples/fixture-mission.json` references a missing `/tmp/relay-fixture-workspace`.

## Next Watch List

- Fix sibling Relay smoke fixture setup/process cleanup, then rerun `tests/relay_provider_tool_smoke.sh` and `tests/relay_acceptance.sh` before claiming full Relay acceptance.
- Promote an AI Chat benchmark/tools workflow only after adding a dedicated workflow runner, fixtures, validation contract, and live/mock boundary record.
- Watch Watchdog token-visibility, named-upstream, auth/rate-limit, and agent-insights changes for impact on `ai-sdk-watchdog-showcase`.
- Watch AI SDK stream/tool-call contract changes for benchmark and Watchdog showcase compatibility.
- Keep CMS/CMS Experience deferred until a workflow kit references their delivery, auth, or content-publication contracts.
- Keep the nine under-tested relationships under-tested until provider-backed, authenticated-browser, and consumer-level evidence is available.
