# Weekly Kujo Workflows Audit - 2026-08-08

Audit ID: `kujo-workflows-audit-2026-08-08`
Captured: `2026-08-08T06:03:48-04:00` (UTC `2026-08-08T10:03:48Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under `$KUJO_REPOS`, prioritizing repositories changed since the 2026-08-01 run. The unavailable named skill `$kujo-workflow-auditor` was not found on disk, so the audit followed the repository's `AGENTS.md`, `README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo-skills` | `9376808` | Updated skill compatibility baseline; Howl and Kennel routing changes inspected. |
| `howl` | `a2b80a5` | Updated Howl content factory to exercise the new branded social SVG variant. |
| `watchdog` | `7c46cd0` | Preserved Watchdog showcase boundary; updated version and August pricing note. |
| `kujo`, `agents-sdk`, `eval`, `kennel`, `lens`, `mcp`, `muzzle`, `packwrite`, `patchbrief`, `rag`, `runledger`, `scent`, `scout`, `shipcheck`, `spec`, `ssg` | current main/v1.0.0 release sweep commits | Confirmed no workflow-catalog contract drift requiring new supported integrations. |
| `ai-chat` | `87624e3` committed main; dirty checkout present | Preserved prior boundary; dirty local experiment files were not used as catalog evidence. |

## Updated Workflows And Records

- `howl-content-factory/`: added a `variant: "social"` manifest card and artifact checks for `social-launch-card.{md,html,svg}`. The workflow now validates Howl's current branded 1200x630 SVG output while preserving the no-posting/no-network boundary.
- `docs/audit/workflow-catalog.json`: advanced audit ID to 2026-08-08 and updated Howl outputs/tests/evidence for branded social SVG coverage.
- `docs/audit/skill-compatibility-matrix.json`: advanced audit ID and `kujo-skills` commit to `9376808`; preserved 36 compatible and 9 compatible-but-under-tested relationships.
- `docs/audit/tool-integration-matrix.json`: advanced audit ID; updated Watchdog to `7c46cd0` and preserved AI SDK/Watchdog showcase boundaries.
- `docs/audit/README.md`: updated the latest audit summary and file list.

## Confirmed Current

- `agency-runner`, `agency-verified-fix-loop`, `feature-card-workflow`, `ai-sdk-muzzle-benchmark`, `ai-sdk-watchdog-showcase`, `enterprise-dispatch-approval-router`, `mcp-agent-gateway-review`, `rag-enterprise-knowledge-gate`, `casefile-incident-evidence-packet`, `loop-engineering`, `docsgen-repo-contract-runner`, `tribunal-decision-gate`, `relay-lifecycle-handoff`, and `workcell-execution-gate` remain aligned with their cataloged paths, commands, skills, tools, documents, contracts, and stated acceptance boundaries.
- Tribunal remains an advisory mock decision workflow unless signed trust-policy verification is added.
- Relay remains a local persistence and pause/resume handoff workflow, not a remote exactly-once delivery claim.
- Workcell remains a bounded trusted local Docker/Podman boundary, not a hosted scheduler or microVM isolation claim.

## Compatibility Disposition

- Added/changed: Howl social-card rendering is now directly covered by `howl-content-factory`.
- Preserved: AI SDK, AI Chat, Watchdog, Dispatch, CaseFile, RunLedger, Eval, Tribunal, Relay, Workcell, and the existing skill relationships.
- Deferred: agency-runner's seven provider/consumer-heavy relationships and docsgen/RAG relationships remain compatible-but-under-tested pending provider, consumer, authenticated browser, or clean target-repo evidence.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash howl-content-factory/scripts/run-workflow.sh
bash workcell-execution-gate/scripts/run.sh
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
git diff --check
```

Sibling-tool evidence inspected:

- Howl `a2b80a5` source, tests, manifest validation, and social SVG renderer.
- Kujo Skills `9376808` Howl/Kennel routing refresh and `9812414` Kujo v1 release guidance.
- Watchdog `7c46cd0` and `a497717` August pricing refresh.
- v1.0.0 release-sweep commits for the current catalog's dependent tool repositories.

## Partial Verification Boundaries

- Live-provider, credentialed browser, and paid provider behavior was not run.
- AI Chat's dirty local checkout was not treated as authoritative beyond committed main evidence.
- Clean-checkout validation on a separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable in local skill paths; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- Howl social-card background image/font embedding if workflows start committing branded assets.
- Kennel compatibility shims until downstream root-module imports are retired.
- Kujo v1.0.0 release guidance propagation into workflow examples that still use legacy syntax.
- Watchdog pricing snapshots and named-upstream/provider credential boundaries.
- Dirty or experimental AI Chat browser/tool surfaces before promoting any new workflow support.
- Clean-machine and live-provider verification evidence for the under-tested catalog relationships.
