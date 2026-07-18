# Verification

Phase 2 evidence captured on 2026-07-14 local time.

Weekly refresh evidence captured on 2026-07-18 local time.

## Passed automatically

- `python3 scripts/validate_catalog.py --json` — PASS; 15 workflows, no errors.
- `python3 scripts/validate_contracts.py` — PASS; 5 schemas, 5 examples, 157 top-level/nested required-field negatives, additive-field checks.
- `python3 tests/test_contracts.py` — PASS; 1 test.
- `python3 -m unittest discover -s tests -p 'test_*.py'` — PASS; 5 tests.
- `bash tests/validate_catalog.sh` — PASS.
- `python3 -m json.tool docs/audit/*.json` — PASS for all audit JSON files.
- `bash -n` over every tracked `*.sh` in this repository — PASS.
- `git diff --check` — PASS.
- Six catalog workflow runners — PASS: enterprise Dispatch approval router, MCP gateway review, RAG knowledge gate, CaseFile evidence packet, Howl content factory, and DocsGen contract runner. Each wrote a timestamped `.runs/<timestamp>/` packet and completed with exit code 0.
- Workcell `KUJO=<checkout>/kujo/target/release/kujo ./tests/run.sh --check-only` — PASS; all listed Kujo source and contract files checked.
- Tribunal doctor, docket validation, mock review, and unsigned integrity verification — PASS. Mock run `2026-07-14-product-decision-md-8737` verified 21 artifacts with no mismatches; signature was absent as expected for the unsigned fixture.
- Relay contract suite — PASS when run directly with the pinned Kujo runtime; the suite emitted its contract PASS cases and returned 0.
- bash tests/skill_relationship_contracts.sh — PASS; nine relationships each exercised with a positive boundary and a malformed or missing-input failure assertion.
- python3 tests/test_skill_relationships.py — PASS; 1 integration test.
- 2026-07-18: `python3 scripts/validate_catalog.py --json` — PASS; 15 workflows, no errors.
- 2026-07-18: `python3 scripts/validate_contracts.py` — PASS; 5 schemas, 5 examples, 157 required-field negatives, additive-field checks.
- 2026-07-18: `python3 -m unittest discover -s tests -p 'test_*.py'` — PASS; 5 tests.
- 2026-07-18: `bash tests/validate_catalog.sh` — PASS.
- 2026-07-18: JSON validation over tracked `*.json` files — PASS.
- 2026-07-18: `bash -n` over repository `*.sh` files — PASS.
- 2026-07-18: `git diff --check` — PASS.
- 2026-07-18 sibling AI Chat: `npm test` — PASS; 107 tests.
- 2026-07-18 sibling Watchdog: `KUJO_BIN=/Users/robertdevore/2026/Kujolang/kujo-repos/kujo/target/release/kujo node tests/proxy_integration_stub_suite.js && .../api_query_support_static_check.js && .../frontend_contract_suite.js` — PASS.

## Partially verified or blocked

- Relay aggregate `KUJO=../kujo/target/release/kujo bash tests/relay_acceptance.sh` — PASS after Relay commit `7ead89a`; 25 smoke scripts passed. The original root cause and repair are recorded in `PHASE2_EVIDENCE.md`.
- `PORT=0 STRICT=1 bash agency-verified-fix-loop/scripts/run-loop.sh` — PARTIAL but browser-complete: 27 passed, 1 expected failure, 1 warning, 7 explicit external-tool failures. The Lens pre-fix failure and post-fix proof passed; PatchBrief/ChangeBucket/ShipCheck are blocked by the current Kujo `cli` module-resolution issue.
- `python3 agency-runner/bin/agency-loop demo-verified-loop --strict` — PARTIAL; corrected sibling-repository discovery completed the delegated run in `.runs/20260714T122849Z/summary.md` with 27 passes, 1 expected failure, 1 warning, and 7 explicit external-tool failures. Strict mode returned non-zero and the composite runner preserved the failed stage results.
- `bash tribunal-decision-gate/scripts/run.sh` — PASS; Tribunal mock review, verify, export, and decision receipt validation.
- `bash relay-lifecycle-handoff/scripts/run.sh` — PASS; Relay worktree pause/resume, export integrity, receipt validation, and cleanup.
- `bash workcell-execution-gate/scripts/run.sh` — PASS; Workcell validate, inspect, Docker execution, and package/completion receipt validation.
- `bash docsgen-repo-contract-runner/scripts/run-workflow.sh` — PASS; packet `.runs/20260714T023826Z`.
- `bash rag-enterprise-knowledge-gate/scripts/run-workflow.sh` — PASS; packet `.runs/20260714T023826Z`.
- Live provider paths for AI SDK, Watchdog, Relay, PackWrite, and Tribunal — NOT RUN; credentials and provider cost were intentionally not used.
- 2026-07-18: AI Chat `npm run benchmark:run`, `npm run smoke:browser`, and live Web Search were not run; they require a running app, explicit app token, Chromium/browser configuration, SearXNG or Ollama Web Search credentials, and selected pane profiles.
- 2026-07-18: Watchdog live named-upstream and agent-insights dashboard behavior was repository- and test-contract reviewed only; no live upstream credentials were used.
- 2026-07-18: Relay provider-generated tool behavior was checked against repository docs, skill evidence, and `KUJO_BIN=/Users/robertdevore/2026/Kujolang/kujo-repos/kujo/target/release/kujo bash tests/relay_provider_tool_smoke.sh`; the smoke printed `PASS relay provider tool smoke`, but the process did not exit cleanly and was interrupted after 90 seconds, so this remains partial verification. The local workflow catalog did not rerun the sibling Relay aggregate acceptance suite.
