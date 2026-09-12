# Weekly Kujo Workflows Audit - 2026-09-12

Audit ID: `kujo-workflows-audit-2026-09-12`
Captured: `2026-09-12T09:09:51-04:00` (UTC `2026-09-12T13:09:52Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under
`$KUJO_REPOS`, prioritizing repositories changed since the 2026-09-05 run. The
named skill `$kujo-workflow-auditor` was not found in the available Codex skill
list or on disk, so the audit followed the repository's `AGENTS.md`,
`README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo-skills` | `e7362c4` | Advanced skill evidence to the current clean v0.7.0 checkout. The new `kujo-release-video` and `kujo-video-styles` distribution does not create a supported `kujo-workflows` integration; existing VideoOps skills remain present and compatible. |
| `kujo-agents` | `17ae095` | Confirmed VideoOps media tools are now the canonical `kujo-agents/videoops/tools` runtime consumed by `videoops-media-generation --media`; the weekly agent audit does not add a new workflow dependency. |
| `kujo-hyperframes` | `1981df2` | Preserved only the VideoOps render-backend relationship after reusable release-video/style skills moved to `kujo-skills`. Dirty local video scratch directories were excluded from catalog claims. |
| `dispatch`, `agents-sdk`, `watchdog`, `runledger` | `dcffd8f`, `bb2202d`, `314698b`, `92cb063` | Preserved existing telemetry and lifecycle boundaries; observer identity and correlation changes do not promote new composed workflows. |
| `workcell`, `tribunal`, `relay` | `3999f11`, `936c5e9`, `01c44da` | Preserved the representative gates and versioned receipt boundaries. Workcell remains a local Docker/Podman execution proof, not a hosted runner. |
| `mcp`, `rag`, `lens`, `siteprobe`, `kennel`, `howl`, `shipcheck`, `fence` | current Sep 6-9 commits where present | Confirmed no repository-backed workflow contract drift requiring catalog promotion. |

Dirty sibling working-tree files in `agents-sdk`, `kujo-hyperframes`, and local
scratch/video repositories were excluded from compatibility claims unless the
relevant committed state and local fixture proof independently supported the
claim.

## Updated Workflows And Records

- `docs/audit/workflow-catalog.json`, `docs/audit/skill-compatibility-matrix.json`, `docs/audit/tool-integration-matrix.json`, `docs/audit/README.md`, and this file: advanced the audit ID and sibling evidence to the 2026-09-12 pass.
- `docs/audit/skill-compatibility-matrix.json`: advanced `kujo-skills` evidence to `e7362c4` and recorded the canonical `kujo-agents/videoops/tools` media route for VideoOps production/media-generation.
- `docs/publishing-house/install-lock.json`, `docs/publishing-house/compatibility-matrix.json`, and `docs/publishing-house/validation-report.md`: advanced clean Publishing House support evidence for `kujo-agents`, `kujo-skills`, and `dossier` after the unit suite exposed stale support-lock commits.
- `docs/audit/tool-integration-matrix.json`: refreshed current sibling commit evidence for the cataloged tools and clarified that HyperFrames remains a render backend after reusable video skills moved to `kujo-skills`.

## Confirmed Current

- The 44 active workflow kits remain inventoried in the catalog.
- VideoOps production/media generation now points at the canonical `kujo-agents/videoops/tools` runtime; fixture proof remains credential-free and live providers remain deferred.
- Publishing House records remain aligned after advancing clean support-lock evidence for `kujo-agents`, `kujo-skills`, and `dossier`; the current `kujo-skills` diff did not modify `skills/kujo-publishing-house-workflows`.
- WebOps, AI SDK/Watchdog, Relay, Tribunal, Workcell, RAG, MCP, Howl, Casefile, Cleanup, and general agent workflows retain their existing fixture/live/host boundaries.

## Compatibility Disposition

- Added: none.
- Changed: audit evidence advanced to current sibling commits; VideoOps media-generation documentation records the canonical agent-owned media runtime.
- Preserved: Owned Agent Project, Publishing House, WebOps, AI SDK/Watchdog showcase, Dispatch approval router, Relay local handoff, Workcell local container boundary, Tribunal advisory mock decision boundary, RAG, MCP, Howl, Casefile, Cleanup, and VideoOps stage relationships.
- Deferred: `kujo-release-video`/`kujo-video-styles` workflow-kit integration, live VideoOps provider execution, external asset search, authenticated Lens/browser capture, licensed-media acquisition, cloud rendering, publication, hosted runners, and separate-machine clean checkout proof.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash workcell-execution-gate/scripts/run.sh
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
git diff --check
```

The full unit suite passed with 28 tests run and 2 skipped. Catalog, contract,
documentation, Tribunal, Relay, and whitespace validation passed.
`bash workcell-execution-gate/scripts/run.sh` returned exit code 1 before
container execution because the configured local Docker socket was unavailable.

## Partial Verification Boundaries

- Live-provider, paid-provider, external asset, authenticated browser, hosted-runner, cloud-render, and external publication behavior was not run.
- Workcell container execution was host-blocked by the missing Docker socket; package validation could not reach Docker execution in this pass.
- Dirty local sibling checkout files were not treated as authoritative catalog evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- Whether `kujo-release-video` and `kujo-video-styles` should become explicit workflow kits or remain reusable skill distributions.
- VideoOps live adapter work across `kujo-agents`, `kujo-skills`, PackWrite, Eval, Howl, RunLedger, HyperFrames, and Lens.
- Publishing House lock drift if `kujo`, Dispatch, Agents SDK, `kujo-agents`, or the Publishing House skill changes after the current fixture matrix.
- AI SDK, Watchdog, Dispatch, Relay, Agents SDK, and RunLedger telemetry correlation changes that may justify a future composed workflow.
- Clean-machine, live-provider, authenticated browser, hosted-runner, and publication evidence for currently deferred relationships.
