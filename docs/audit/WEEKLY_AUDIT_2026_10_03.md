# Weekly Kujo Workflows Audit - 2026-10-03

Audit ID: `kujo-workflows-audit-2026-10-03`
Captured: `2026-10-03T06:05:47-04:00` (UTC `2026-10-03T10:05:47Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under
`$KUJO_REPOS`, prioritizing repositories changed since the 2026-09-26 run. The
named skill `$kujo-workflow-auditor` was not found in the available Codex skill
list or on disk, so the audit followed this repository's `AGENTS.md`,
`README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo` | `531cc22` on `main`; Publishing House support baseline remains stable `v1.5.0` at `83fbdd4` | Preserved workflow runtime boundaries. Current VM-startup, benchmark, and reverted native-AOT work does not add new catalog workflows or broaden Publishing House support. |
| `kujo-skills` | `da0aa8c` on `main` | Advanced skill evidence and Publishing House support-lock evidence. The refresh only touched Workcell and VersionSeal skill guidance plus indexes; Publishing House skill files remain present. |
| `dispatch` | `e1bbc21` on `main` | Preserved Publishing House and approval-router boundaries. Operator readiness, bounded batch graph controls, and allocated-state accounting do not change workflow completion contracts. |
| `workcell` | `0f9595b` on `main` | Preserved the representative Workcell local-container boundary. Workcell 1.2, retained-workspace ownership observations, final-validation Git-effect gates, and Boat handoff documentation do not promote hosted or microVM isolation claims. |
| `ai-chat` | `27174aa` on `main` | Preserved the AI SDK/Watchdog showcase boundary. Completion-exhaustion, output-limit recovery, and shell-boundary work improves the sibling app outside the current showcase runner. |
| `watchdog` | `fafea3a` (`v1.2.0`) on `main` | Preserved the AI SDK/Watchdog telemetry boundary. RunLedger measurement-release, pricing-catalog, timing, and Kujo-runtime-summary work does not change fixture acceptance. |
| `mcp`, `patchbrief`, `shipcheck`, `ability` | `e02905d`, `0e8d6bd`, `0a9f579`, `bcbecb4` | Confirmed no repository-backed workflow contract drift requiring a new catalog claim. MCP Gateway, reviewer evidence, and Ability process work remain separate tool boundaries. |
| `assetworks` | `4fea053` on `main` | Advanced Publishing House support-lock evidence after the fixture exposed the stale strict checkout baseline; AssetWorks still reports tool `0.3.0` and contract `1.0.0`. |
| `ssg`, `intake`, `presentations`, `cms`, `leash`, `redact`, `eval`, `lens`, `site-kit`, `scout`, `kennel`, `readersignal`, `tribunal`, `runledger` | current Sep 23-Oct 3 commits where present | Confirmed no new supported workflow integration without a validated shared contract. |

Dirty or scratch sibling repositories were not treated as authoritative workflow
evidence. `watchdog` had a modified local `watchdog_proxy_config.json`, and
`agents-sdk` had untracked maintenance-agent files; neither was used as support
evidence.

## Updated Workflows And Records

- `docs/audit/workflow-catalog.json`: advanced the audit ID only; the 44 active workflows remain unchanged.
- `docs/audit/skill-compatibility-matrix.json`: advanced the audit ID and `kujo-skills` evidence to `da0aa8c`.
- `docs/audit/tool-integration-matrix.json`: advanced the audit ID and refreshed preserved-boundary rationale for `kujo`, `kujo-skills`-adjacent skills, `dispatch`, `workcell`, `ai-chat`, and `watchdog`.
- `docs/publishing-house/install-lock.json` and `docs/publishing-house/compatibility-matrix.json`: advanced clean local `kujo-skills` and AssetWorks support pins to `da0aa8c` and `4fea053` after the unit suite exposed stale strict checkout baselines.
- `docs/audit/README.md` and this file: advanced the latest audit summary and pointer.

No workflow implementation, fixture, or catalog relationship was changed.

## Confirmed Current

- The 44 active workflow kits remain inventoried in the catalog.
- Owned Agent Project, WebOps, AI SDK/Watchdog showcase, Dispatch approval router, Relay local handoff, Workcell local container boundary, Tribunal advisory mock decision boundary, RAG, MCP, Howl, Casefile, Cleanup, Publishing House, and VideoOps relationships retain their existing fixture/live/host boundaries.
- Publishing House AssetWorks and ReaderSignal skill links still describe tool-owned records already referenced by the workflows; they do not promote live media adapters, publication, analytics, or measurement support.
- Workcell still requires the local host runtime for container execution and does not imply hosted or microVM isolation.
- Watchdog pricing, live-provider cost, provider credentials, and telemetry posture remain dated external evidence outside fixture acceptance.

## Compatibility Disposition

- Added: none.
- Changed: audit evidence advanced to current sibling commits; strict Publishing House `kujo-skills` and AssetWorks support evidence advanced to `da0aa8c` and `4fea053`.
- Preserved: all existing catalog workflow, tool, fixture, contract, and deferred-integration boundaries.
- Deferred: live VideoOps provider execution, external asset search, authenticated Lens/browser capture, licensed-media acquisition, cloud rendering, publication, hosted runners, separate-machine clean checkout proof, and composed workflows that would combine Workcell, Relay, and Tribunal.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
git diff --check
```

Blocked or partial:

```text
bash workcell-execution-gate/scripts/run.sh
```

The catalog validator passed for 44 workflows. Contract validation passed with
19 schemas, 16 examples, and 314 required-field negatives. The unit suite passed
after advancing strict `kujo-skills` and AssetWorks Publishing House support pins
exposed by fixture runs. Representative Tribunal, Relay, and whitespace gates
passed.

The Workcell gate did not produce a completion receipt in this run. The script
was still waiting after 90 seconds under the local Docker/host runtime boundary,
so container execution success is not claimed.

## Partial Verification Boundaries

- Live-provider, paid-provider, external asset, authenticated browser, hosted-runner, cloud-render, and external publication behavior was not run.
- Workcell container execution was host-blocked before a completion receipt was produced; package execution and container receipts are not claimed for this run.
- Dirty sibling checkout files were not treated as authoritative catalog evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- Kujo runtime and language release movement beyond the pinned Publishing House `v1.5.0` support baseline.
- Dispatch operator-readiness and workflow state changes that could affect Publishing House or approval-router contracts.
- Workcell local Git-effect final validation, retained-workspace ownership evidence, Docker/Podman endpoint behavior, and Boat integration.
- Watchdog/RunLedger measurement records and AI Chat execution-boundary changes that may justify future composed observability workflows.
- MCP Gateway, PatchBrief, ShipCheck, Ability, and portable Git-process work for possible future reviewer-evidence or release-readiness workflows.
- Clean-machine, live-provider, authenticated browser, hosted-runner, and publication evidence for currently deferred relationships.
