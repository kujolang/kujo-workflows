# Weekly Kujo Workflows Audit - 2026-09-19

Audit ID: `kujo-workflows-audit-2026-09-19`
Captured: `2026-09-19T10:33:31-04:00` (UTC `2026-09-19T14:33:31Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under
`$KUJO_REPOS`, prioritizing repositories changed since the 2026-09-12 run. The
named skill `$kujo-workflow-auditor` was not found in the available Codex skill
list or on disk, so the audit followed the repository's `AGENTS.md`,
`README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo` | `7968d4f` | Preserved workflow runtime boundaries. Recent standard-library, PDF, PostgreSQL, datetime, HTTP, and URI component decoding work does not add a new catalog workflow claim. |
| `kujo-skills` | `3666d9e` | Advanced skill evidence and Publishing House support-lock records. Runtime-hardening, standard-library, and Workcell skill coverage changed; `kujo-publishing-house-workflows` remained present. |
| `kujo-agents` | `ba327cf` | Advanced Publishing House support-lock evidence. The September capability audit updates deferred agent opportunities and ecosystem maps without creating a new supported workflow integration. |
| `workcell` | `e2915a3` | Preserved the representative Workcell gate and local Docker/Podman trust boundary. Explicit Docker endpoint hardening does not promote hosted or microVM isolation claims. |
| `watchdog` | `df36d57` | Preserved the AI SDK/Watchdog showcase boundary. September 13 pricing catalog refreshes are dated cost evidence, not a workflow contract migration. |
| `mcp`, `rag`, `lens`, `siteprobe`, `howl`, `dispatch`, `ai-chat` | current Sep 6-13 commits where present | Confirmed no repository-backed workflow contract drift requiring catalog promotion. |

Dirty or scratch video repositories were not treated as authoritative workflow
evidence.

## Updated Workflows And Records

- `docs/audit/workflow-catalog.json`, `docs/audit/skill-compatibility-matrix.json`, `docs/audit/tool-integration-matrix.json`, `docs/audit/README.md`, and this file: advanced the audit ID and sibling evidence to the 2026-09-19 pass.
- `docs/publishing-house/install-lock.json`, `docs/publishing-house/compatibility-matrix.json`, and `docs/publishing-house/validation-report.md`: advanced `kujo-agents` support evidence to `ba327cf` and `kujo-skills` support evidence to `3666d9e`.
- `docs/audit/tool-integration-matrix.json`: refreshed Kujo, Watchdog, and Workcell current sibling commit evidence while preserving existing workflow contracts.

## Confirmed Current

- The 44 active workflow kits remain inventoried in the catalog.
- Owned Agent Project, WebOps, AI SDK/Watchdog showcase, Dispatch approval router, Relay local handoff, Workcell local container boundary, Tribunal advisory mock decision boundary, RAG, MCP, Howl, Casefile, Cleanup, Publishing House, and VideoOps relationships retain their existing fixture/live/host boundaries.
- Workcell still emits versioned package and completion receipts when host execution is blocked.
- Watchdog pricing data remains external, dated evidence; live-provider cost and credentials remain separate from fixture workflow acceptance.

## Compatibility Disposition

- Added: none.
- Changed: audit evidence advanced to current sibling commits; Publishing House `kujo-skills` support-lock evidence advanced to `3666d9e`.
- Preserved: all existing catalog workflow, skill, tool, fixture, contract, and deferred-integration boundaries.
- Deferred: live VideoOps provider execution, external asset search, authenticated Lens/browser capture, licensed-media acquisition, cloud rendering, publication, hosted runners, separate-machine clean checkout proof, and any composed workflow that would combine Workcell, Relay, and Tribunal.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 scripts/validate_docs.py
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
git diff --check
```

Blocked or partial:

```text
bash workcell-execution-gate/scripts/run.sh
```

The catalog validator passed for 44 workflows. Contract validation passed with
19 schemas, 16 examples, and 314 required-field negatives. Documentation,
Tribunal, Relay, unit, and whitespace validation passed.

The full unit suite passed with 28 tests run and 2 skipped after the Publishing
House support-lock commits were advanced to current clean sibling evidence.

`bash workcell-execution-gate/scripts/run.sh` wrote valid Workcell package and
completion receipts, then returned exit code 3 because the selected Docker
daemon did not report AppArmor for rootful execution. Container success was not
claimed.

## Partial Verification Boundaries

- Live-provider, paid-provider, external asset, authenticated browser, hosted-runner, cloud-render, and external publication behavior was not run.
- Workcell container execution was host-blocked by the selected Docker daemon's missing AppArmor signal; package and blocked completion receipts were verified.
- Dirty local sibling checkout files were not treated as authoritative catalog evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- Publishing House lock drift if `kujo`, Dispatch, Agents SDK, `kujo-agents`, `kujo-skills`, or the Publishing House skill changes after the current fixture matrix.
- Workcell Docker endpoint and AppArmor/rootful-rootless host proof behavior.
- Kujo runtime changes that affect Agent Project, DocsGen, package installation, PDF/document, database, or URI standard-library workflows.
- AI SDK, Watchdog, Dispatch, Relay, Agents SDK, and RunLedger telemetry correlation changes that may justify a future composed workflow.
- VideoOps live adapter work across `kujo-agents`, `kujo-skills`, PackWrite, Eval, Howl, RunLedger, HyperFrames, and Lens.
- Clean-machine, live-provider, authenticated browser, hosted-runner, and publication evidence for currently deferred relationships.
