# Weekly Kujo Workflows Audit - 2026-10-10

Audit ID: `kujo-workflows-audit-2026-10-10`
Captured: `2026-10-10T06:06:05-04:00` (UTC `2026-10-10T10:06:05Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under
`$KUJO_REPOS`, prioritizing repositories changed since the 2026-10-03 run. The
named skill `$kujo-workflow-auditor` was not found in the available Codex skill
list or on disk, so the audit followed this repository's `AGENTS.md`,
`README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo` | `0c6f9f8` on `main`; Publishing House support baseline remains stable `v1.5.0` at `83fbdd4` | Preserved workflow runtime boundaries. Database-pool starvation, VM-startup, benchmark, and runtime work does not add new catalog workflows or broaden Publishing House support. |
| `kujo-skills` | `70e68ba` on `main` | Advanced skill evidence and Publishing House support-lock evidence. The refresh touched Kujo MCP/runtime guidance and indexes; Publishing House skill files remain present and versioned `0.7.0`. |
| `kujo-agents` | `be22fda` on `main` | Advanced Publishing House support-lock evidence. The October agent capability audit changed chain-of-command/deferred-opportunity documentation, not the Publishing House contract version. |
| `kujolang-mcp` | `ea10a3e` on `codex/ecosystem-catalog-refresh` | Preserved MCP Gateway workflow boundaries. Ecosystem catalog refresh evidence does not create a new workflow integration claim in this repository. |
| `dispatch` | `ac2609b` on `main` | Preserved Publishing House and approval-router boundaries. Subgraph settlement verification evidence does not change workflow completion contracts. |
| `workcell` | `a276a92` on `main` | Preserved the representative Workcell local-container boundary. Vulnerable-adapter dependency and integrity-pin updates tighten the sibling tool without promoting hosted or microVM isolation claims. |
| `ai-chat` | `d32e649` on `main` | Preserved the AI SDK/Watchdog showcase boundary. Expired-approval-loop and execution-recovery changes improve the sibling app outside the current showcase runner. |
| `watchdog` | `4ceb203` on `main` | Preserved the AI SDK/Watchdog telemetry boundary. Telemetry-ID validation work does not change fixture acceptance. |
| `eval` | `926577b` on `main` | Preserved Eval-backed workflow acceptance. Suite-inventory gate fixes remain compatible with existing owned Agent Project and VideoOps contracts. |
| `tribunal` | `e3ccd21` on `main` | Preserved the advisory mock decision boundary. README plain-language changes do not change receipt semantics. |
| `mcp`, `patchbrief`, `shipcheck`, `ability` | `e02905d`, `0e8d6bd`, `0a9f579`, `bcbecb4` | Confirmed no repository-backed workflow contract drift requiring a new catalog claim. |
| `ssg`, `intake`, `presentations`, `site-kit`, `scout`, `kennel`, `runledger`, Publishing House tool repositories, `lens`, `spec` | current Sep 22-Oct 3 commits where present | Confirmed no new supported workflow integration without a validated shared contract. |

Dirty or scratch sibling repositories were not treated as authoritative workflow
evidence. `watchdog` had a modified local `watchdog_proxy_config.json`, and
`kujo-videoops` had extensive uncommitted local work; neither was used as
support evidence.

## Updated Workflows And Records

- `docs/audit/workflow-catalog.json`: advanced the audit ID only; the 44 active workflows remain unchanged.
- `docs/audit/skill-compatibility-matrix.json`: advanced the audit ID and `kujo-skills` evidence to `70e68ba`.
- `docs/audit/tool-integration-matrix.json`: advanced the audit ID and refreshed preserved-boundary rationale for `kujo`, `dispatch`, `workcell`, `ai-chat`, `watchdog`, `eval`, and `tribunal`.
- `docs/publishing-house/install-lock.json` and `docs/publishing-house/compatibility-matrix.json`: advanced clean local `kujo-agents` and `kujo-skills` support pins to `be22fda` and `70e68ba` after the unit suite exposed stale strict checkout baselines.
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
- Changed: audit evidence advanced to current sibling commits; strict Publishing House `kujo-agents` and `kujo-skills` support evidence advanced to `be22fda` and `70e68ba`.
- Preserved: all existing catalog workflow, tool, fixture, contract, and deferred-integration boundaries.
- Deferred: live VideoOps provider execution, external asset search, authenticated Lens/browser capture, licensed-media acquisition, cloud rendering, publication, hosted runners, separate-machine clean checkout proof, and composed workflows that would combine Workcell, Relay, and Tribunal.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 -m unittest discover -s tests -p 'test_*.py'
DOCKER_HOST=unix://$HOME/.colima/default/docker.sock bash workcell-execution-gate/scripts/run.sh
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
git diff --check
```

The catalog validator passed for 44 workflows. Contract validation passed with
19 schemas, 16 examples, and 314 required-field negatives. The unit suite passed
after advancing stale strict `kujo-agents` and `kujo-skills` support pins.
Representative Tribunal, Relay, and whitespace gates passed.

Blocked or partial:

```text
bash workcell-execution-gate/scripts/run.sh
DOCKER_HOST=unix://$HOME/.colima/default/docker.sock bash workcell-execution-gate/scripts/run.sh
```

The default Docker context `desktop-linux` could not connect to
the Docker Desktop socket. After starting Colima and
rerunning the gate with the Colima socket, Workcell validation, inspection,
work-package schema validation, and completion-receipt schema validation passed,
but bounded container execution was blocked because
`kujolang/workcell-base:local` was not available locally and `--no-pull` was
requested. Workcell completion success is not claimed for this run.

## Partial Verification Boundaries

- Live-provider, paid-provider, external asset, authenticated browser, hosted-runner, cloud-render, and external publication behavior was not run.
- Workcell container execution was host-blocked before a completion artifact was produced; package and blocked completion receipts are validated, but successful bounded execution is not claimed.
- Dirty sibling checkout files were not treated as authoritative catalog evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- Kujo runtime and language release movement beyond the pinned Publishing House `v1.5.0` support baseline.
- Kujo MCP, `kujolang-mcp`, and ecosystem catalog refresh work for possible future MCP Gateway evidence changes.
- Dispatch settlement and workflow state changes that could affect Publishing House or approval-router contracts.
- Workcell dependency integrity, Docker/Podman endpoint behavior, local Git-effect validation, and Boat integration.
- Watchdog/RunLedger measurement records and AI Chat execution-boundary changes that may justify future composed observability workflows.
- MCP Gateway, PatchBrief, ShipCheck, Ability, and portable Git-process work for possible future reviewer-evidence or release-readiness workflows.
- Clean-machine, live-provider, authenticated browser, hosted-runner, and publication evidence for currently deferred relationships.
