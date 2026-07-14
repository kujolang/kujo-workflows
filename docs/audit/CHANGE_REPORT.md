# Change Report

## Implemented

1. Added a canonical workflow catalog and validator.
   - Files: `docs/audit/workflow-catalog.json`, `scripts/validate_catalog.py`, `tests/validate_catalog.sh`, `tests/test_catalog_validator.py`.
   - Before: workflow-to-skill and workflow-to-tool dependencies were only implied by prose and shell commands.
   - After: 12 active workflows declare canonical skill names/paths, tool repositories, inputs, outputs, approval boundaries, state/recovery, evidence, tests, documentation, and readiness posture. The validator fails closed when dependencies disappear or drift.
   - Evidence: `python3 scripts/validate_catalog.py --json`; validator contract tests cover missing skills and unknown tools.

2. Added durable audit matrices and baseline.
   - Files: `docs/audit/skill-compatibility-matrix.json`, `docs/audit/tool-integration-matrix.json`, `docs/audit/REPOSITORY_BASELINE.md`, `docs/audit/README.md`.
   - Before: no repository-level machine-readable compatibility or Tribunal/Relay/Workcell opportunity record existed in this checkout.
   - After: current relationships, exact skill checkout, tool maturity/dispositions, cross-tool deferrals, rollback notes, and the initial multi-repository Git state are recorded.

3. Removed machine-specific sibling-repository defaults from reusable runners.
   - Files: `agency-verified-fix-loop/scripts/run-loop.sh`, `casefile-incident-evidence-packet/scripts/run-workflow.sh`, `docsgen-repo-contract-runner/scripts/run-workflow.sh`, `enterprise-dispatch-approval-router/scripts/run-workflow.sh`, `howl-content-factory/scripts/run-workflow.sh`, `mcp-agent-gateway-review/scripts/run-workflow.sh`, `rag-enterprise-knowledge-gate/scripts/run-workflow.sh`, `feature-card-workflow/muzzle-template/workflows/feature-card-full.sh`.
   - Before: several runners defaulted to `/Users/robertdevore/2026/Kujolang/kujo-repos`, and the verified-fix loop resolved one directory too shallow.
   - After: defaults resolve the sibling repository root from the workflow location while preserving explicit `KUJO_REPOS` overrides.

4. Added versioned Tribunal, Relay, and Workcell contract boundaries and three dedicated integrations.
   - Files: `contracts/`, `tribunal-decision-gate/`, `relay-lifecycle-handoff/`, `workcell-execution-gate/`, `scripts/validate_contracts.py`, `scripts/validate_contract_instance.py`, `tests/test_contracts.py`.
   - Before: the audit only documented opportunities; no workflow-facing package, message, decision, or completion receipt was validated in this repository.
   - After: Tribunal mock review, Relay pause/resume/export/cleanup, and Workcell validate/inspect/run each produce a schema-validated artifact packet with explicit advisory, local-delivery, bounded-runtime, redaction, provenance, and idempotency semantics.
   - Evidence: `python3 scripts/validate_contracts.py`, the three gate scripts, and `docs/audit/PHASE2_EVIDENCE.md`.

5. Fixed agency browser-loop reproducibility and resolved Relay aggregate acceptance.
   - Files: `agency-verified-fix-loop/scripts/run-loop.sh`; Relay commit `7ead89a` in `tests/relay_agents_tool_smoke.sh`.
   - Before: port reuse could serve a stale fixed fixture, and Relay's absolute-runtime agent smoke failed because `KUJO_BIN` was not exported.
   - After: the browser loop selects a free port, stops on an unexpected pre-fix result, and records a real expected failure. Relay's full 25-script aggregate passes with an explicit absolute runtime.
   - Evidence: agency packet `.runs/20260714T023325Z`; Relay acceptance log and pushed commit `7ead89a`.

6. Added positive and negative boundary fixtures for the nine previously under-tested skill relationships.
   - Files: `tests/skill_relationship_contracts.sh`, `tests/test_skill_relationships.py`, `docs/audit/skill-compatibility-matrix.json`, `docs/audit/PHASE2_EVIDENCE.md`.
   - Before: relationships were only supported by source inspection and composite documentation.
   - After: Spec, Scout, Scent, Lens, CaseFile, PackWrite, RunLedger, DocsGen, and RAG each have a real positive invocation plus a malformed or missing-input failure assertion. Relationships remain under-tested because this boundary suite does not establish live providers, browser execution for the Agency Runner phases, or production consumers.
   - Evidence: `bash tests/skill_relationship_contracts.sh` and `python3 tests/test_skill_relationships.py`.

7. Hardened Agency Runner tool-root, safe-write, output-exclusion, timeout, and fail-closed context behavior.
   - Files: `agency-runner/bin/agency-loop`.
   - Before: the embedded runner resolved sibling tools one directory too shallow, Spec validation rejected temp-project paths, Scent could scan its own `.kujo` output, and context commands could fail silently.
   - After: roots auto-detect from `KUJO_REPOS` or repository layout, Spec runs in the target project, `.kujo` is excluded from Scent, tool timeouts are bounded, and missing or failed Scout or Scent invocations stop the context phase.

## Intentionally not changed

- No existing production workflow was made dependent on the new Tribunal, Relay, or Workcell stages. The integrations are optional dedicated gates with rollback-safe receipts; the matrix documents where binding composition remains deferred.
- Existing dirty files in `ai-sdk`, `dispatch`, and `spec` were not touched.
- No generated `.runs`, `.work`, provider outputs, credentials, or tool evidence were committed.
