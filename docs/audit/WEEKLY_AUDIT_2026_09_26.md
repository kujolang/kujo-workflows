# Weekly Kujo Workflows Audit - 2026-09-26

Audit ID: `kujo-workflows-audit-2026-09-26`
Captured: `2026-09-26T06:06:17-04:00` (UTC `2026-09-26T10:06:17Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under
`$KUJO_REPOS`, prioritizing repositories changed since the 2026-09-19 run. The
named skill `$kujo-workflow-auditor` was not found in the available Codex skill
list or on disk, so the audit followed the repository's `AGENTS.md`,
`README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo` | `3efa60c` on `runtime/generator-async-spawn-completion`; stable `v1.5.0` tag `83fbdd4` | Preserved workflow runtime boundaries. Kujo 1.5 and follow-on runtime, concurrency, PDF, and fixture-provider work support current sibling gates but do not add new catalog workflows. |
| `kujo-skills` | `ab77f5c` | Advanced skill evidence. New AssetWorks and ReaderSignal workflow skills are now linked to the Publishing House workflows that directly use those tool-owned records. |
| `dispatch` | `a01a365` | Advanced Publishing House support-lock evidence. Durable control, DAG barrier, clean retry, and provider-control work preserves existing orchestration contracts. |
| `storydesk`, `galleypack`, `bluepencil`, `versionseal`, `presswire`, `readersignal`, `assetworks`, `dossier` | current Sep 22-26 commits where present | Advanced Publishing House support-lock evidence where tool-owned version preflights passed against clean checkouts. |
| `watchdog` | `4e07223` | Preserved the AI SDK/Watchdog showcase boundary. Redaction-fixture and regression-isolation work does not change the fixture telemetry contract. |
| `workcell` | `3f019ab` | Preserved the representative Workcell gate and local Docker/Podman trust boundary. Portable execution evidence and failure preservation tighten receipts without promoting hosted or microVM isolation claims. |
| `tribunal`, `relay`, `eval`, `lens`, `siteprobe`, `howl`, `runledger`, `ai-chat`, `scout`, `kennel`, `muzzle`, `ssg` | current Sep 22-26 commits where present | Confirmed no repository-backed workflow contract drift requiring a new workflow claim. |

Dirty or scratch sibling repositories were not treated as authoritative workflow
evidence.

## Updated Workflows And Records

- `docs/audit/workflow-catalog.json`: advanced the audit ID and added canonical `kujo-assetworks-workflows` skill links to Publishing House adaptation, asset production, and format production plus `kujo-readersignal-workflows` to post-publication.
- `docs/audit/skill-compatibility-matrix.json`: advanced `kujo-skills` evidence to `ab77f5c` and recorded the Publishing House skill relationship for AssetWorks and ReaderSignal without expanding live support.
- `docs/audit/tool-integration-matrix.json`: refreshed current sibling commit evidence and preserved existing fixture/live boundaries for Tribunal, Relay, Watchdog, Workcell, Dispatch, AI Chat, RunLedger, Scout, Eval, Kujo, and Howl.
- `docs/publishing-house/install-lock.json` and `docs/publishing-house/compatibility-matrix.json`: advanced the locked Publishing House support matrix to clean current local checkouts where contract preflights passed, including Kujo `v1.5.0`, Dispatch `a01a365`, `kujo-skills` `ab77f5c`, ReaderSignal `0.3.0`, AssetWorks `0.3.0`, BluePencil `0.3.0`, VersionSeal `0.3.0`, and StoryDesk `0.3.0`.
- `lib/publishing_house/runtime.kujo` and `scripts/publishing_house_fixture.kujo`: moved Publishing House tool-state and tool-input paths under repository `.runs/` so AssetWorks `0.3.0` no longer rejects symlinked `/tmp` output paths in fixture tests.
- `docs/audit/README.md` and this file: advanced the audit summary and latest audit pointer.

## Confirmed Current

- The 44 active workflow kits remain inventoried in the catalog.
- Owned Agent Project, WebOps, AI SDK/Watchdog showcase, Dispatch approval router, Relay local handoff, Workcell local container boundary, Tribunal advisory mock decision boundary, RAG, MCP, Howl, Casefile, Cleanup, Publishing House, and VideoOps relationships retain their existing fixture/live/host boundaries.
- Publishing House AssetWorks and ReaderSignal skill links describe existing tool-owned records already referenced by the workflows; they do not promote live media adapters, publication, analytics, or measurement to supported behavior.
- Workcell still emits versioned package and completion receipts when host execution is blocked.
- Watchdog pricing data and provider telemetry remain external, dated evidence; live-provider cost and credentials remain separate from fixture workflow acceptance.

## Compatibility Disposition

- Added: canonical skill relationships for AssetWorks-backed Publishing House workflows and ReaderSignal-backed post-publication workflow.
- Changed: audit evidence advanced to current sibling commits; Publishing House support-lock and compatibility evidence advanced to clean current local commits after unit tests exposed stale lock baselines.
- Preserved: all existing catalog workflow, tool, fixture, contract, and deferred-integration boundaries.
- Deferred: live VideoOps provider execution, external asset search, authenticated Lens/browser capture, licensed-media acquisition, cloud rendering, publication, hosted runners, separate-machine clean checkout proof, and composed workflows that would combine Workcell, Relay, and Tribunal.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 scripts/validate_docs.py
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
python3 scripts/validate_static.py
git diff --check
```

Blocked or partial:

```text
python3 -m unittest discover -s tests -p 'test_*.py'
bash workcell-execution-gate/scripts/run.sh
```

The catalog validator passed for 44 workflows. Contract validation passed with
19 schemas, 16 examples, and 314 required-field negatives. Documentation,
static syntax, Tribunal, Relay, and whitespace validation passed.

The full unit suite first failed because the Publishing House support-lock
baseline still pointed at older tool commits. After advancing to clean current
support evidence and adapting fixture paths for AssetWorks `0.3.0`, the original audit remained
blocked at the all-eleven Publishing House fixture because PressWire `0.2.0`
rejects VersionSeal `0.3.0` approval records with `approval contract mismatch`.
The rest of that audit suite completed with 1 failure and 2 skips. The same-day
compatibility follow-up below supersedes this Publishing House blocker.

`bash workcell-execution-gate/scripts/run.sh` returned before package execution
because the configured user Docker socket was unavailable. Container success
was not claimed.

## Partial Verification Boundaries

- Live-provider, paid-provider, external asset, authenticated browser, hosted-runner, cloud-render, and external publication behavior was not run.
- Publishing House all-eleven fixture execution now passes after the same-day compatibility follow-up below; live publication support was not inferred.
- Workcell container execution was host-blocked before Docker API connection; package execution and container receipts were not claimed for this run.
- Dirty local sibling checkout files were not treated as authoritative catalog evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- Publishing House lock drift as Kujo 1.5 adoption continues across StoryDesk, Dossier, GalleyPack, BluePencil, VersionSeal, PressWire, ReaderSignal, AssetWorks, Dispatch, Agents SDK, `kujo-agents`, and `kujo-skills`.
- Workcell Docker endpoint, AppArmor, rootful/rootless, portable execution evidence, and failure-preservation behavior.
- Kujo runtime changes that affect Agent Project, DocsGen, package installation, PDF/document, database, async, generator, or URI standard-library workflows.
- AI SDK, Watchdog, Dispatch, Relay, Agents SDK, RunLedger, Eval, and Scout telemetry or portable-result changes that may justify a future composed workflow.
- VideoOps live adapter work across `kujo-agents`, `kujo-skills`, PackWrite, Eval, Howl, RunLedger, HyperFrames, Lens, and AssetWorks.
- Clean-machine, live-provider, authenticated browser, hosted-runner, and publication evidence for currently deferred relationships.

## Same-day VersionSeal / PressWire Compatibility Follow-up

PressWire commit `14fb28b1ae5b3475370cea0585c584fd022bcf60` accepts
VersionSeal `0.3.0` approval records under unchanged schema/contract `1.0.0`.
Its producer allowlist retains `0.1.0` and `0.2.0`; identity, checksum,
destination, action, actor, timestamp, and optional exact output-path checks
remain enforced. Native PressWire record versions remain separate from the
advertised VersionSeal approval versions. The PressWire validation gate passed,
including 68 compatibility assertions across all three approval versions.

The support lock and compatibility matrix now pin that PressWire commit and
`kujo-agents` commit `e74545cfb3677257f9f3d88ed5840a36555ed566`. The latter
changes only two chain-of-command audit documents, with no Publishing House
agent changes. The older pin failed the clean-checkout preflight.

After approval compatibility was restored, the final fixture check exposed a
stale generated-ID assumption. PressWire honors the explicit
`publication-fixture-v2` ID supplied by the workflow. The workflow now uses
that ID for its StoryDesk publication reference and local-effect receipt, and
the fixture verifies that both references match the actual PressWire record.

The standalone command passed with output in an ignored repo-local directory:

```text
bash scripts/run-publishing-house-fixture.sh --out .runs/versionseal-030-compat-20260926-final
```

It verified all 11 workflows, 46 record references, 38 agent receipts, and 34
tool contract preflights. Revision, approval pause/resume, and idempotency
checks passed, and approved/published checksums matched. The proof reports zero
network calls and `live_publication: false`. This supersedes the known
VersionSeal/PressWire incompatibility; the compatibility matrix's active
incompatibility list is empty. Generated proof remains local evidence, not a
tracked clean-install artifact.

Tribunal and Relay gates passed again. Workcell remains blocked by the existing
unavailable Docker socket before container execution; no container success or
live publication support is claimed.

Final follow-up validation passed:

```text
python3 -m unittest discover -s tests -p 'test_*.py'  # 28 tests, 2 skips, 0 failures
python3 scripts/validate_catalog.py --json          # 44 workflows
python3 scripts/validate_contracts.py               # 19 schemas, 16 examples, 314 negatives
python3 scripts/validate_docs.py
python3 scripts/validate_static.py
git diff --check
```

The unit suite independently reran the all-eleven fixture successfully.
