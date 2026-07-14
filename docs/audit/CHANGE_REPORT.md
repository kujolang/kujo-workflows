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

## Intentionally not changed

- No direct Tribunal, Relay, or Workcell execution stage was added. The tool matrix documents the gap and deferral because the required shared docket, mission, workspace, receipt, and resume contracts are not present, and Relay explicitly leaves full Workcell isolation/recovery open.
- Existing dirty files in `ai-sdk`, `dispatch`, and `spec` were not touched.
- No generated `.runs`, `.work`, provider outputs, credentials, or tool evidence were committed.
