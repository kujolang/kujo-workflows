# Weekly Kujo Workflows Audit - 2026-09-05

Audit ID: `kujo-workflows-audit-2026-09-05`
Captured: `2026-09-05T06:05:51-04:00` (UTC `2026-09-05T10:05:51Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under
`$KUJO_REPOS`, prioritizing repositories changed since the 2026-08-29 run. The
named skill `$kujo-workflow-auditor` was not found in the available Codex skill
list or on disk, so the audit followed the repository's `AGENTS.md`,
`README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo-workflows` | `f106061` | Preserved the six VideoOps workflow kits added after the prior audit and refreshed audit records for the production initializer plus five fixture stages. |
| `kujo-skills` | `0d41ab4` | Advanced skill evidence to the weekly skill-drift refresh and recorded VideoOps workflow skill relationships. |
| `kujo-agents` | `062ada1` | Confirmed VideoOps Producer and five specialist agent contracts remain the canonical source for the VideoOps workflow kits. |
| `kujo-videoops` | `fe74ae8` | Confirmed this sibling repository is a current durable local orchestration prototype, not a dependency of the `kujo-workflows` VideoOps proof. |
| `kujo-hyperframes` | `5d72c07` | Recorded as the local render backend used by the VideoOps HyperFrames edit proof. |
| `packwrite`, `eval`, `howl`, `runledger` | `3f0cbf4`, `7ad5cae`, `5470f92`, `92cb063` | Recorded as supporting tools in the VideoOps release proof for intake validation, stage gates, proof cards, and lifecycle evidence. |
| `tribunal`, `relay`, `workcell`, `dispatch`, `ai-sdk`, `ai-chat`, `watchdog`, `casefile`, `kennel`, `spec`, `mcp`, `rag`, `ssg` | current Sep 1-4 commits where present | Refreshed tool-matrix evidence and preserved existing workflow boundaries; no new supported workflow integrations were promoted from sibling hardening or telemetry work. |

Dirty sibling working-tree files in `agents-sdk`, `dispatch`, `email`,
`kujo-videoops`, `kujo-hyperframes`, and unrelated local scratch repositories
were excluded from compatibility claims unless the relevant committed state and
local fixture proof independently supported the claim.

## Updated Workflows And Records

- `docs/audit/skill-compatibility-matrix.json`: added the VideoOps production initializer and five VideoOps stage workflows with their canonical skill relationships; advanced skill evidence to `kujo-skills` `0d41ab4`.
- `docs/audit/tool-integration-matrix.json`: refreshed current sibling commit evidence and added VideoOps supporting relationships for Kujo, PackWrite, Eval, Howl, RunLedger, and HyperFrames.
- `docs/audit/workflow-catalog.json`, `docs/audit/README.md`, and this file: advanced the audit ID and recorded the 2026-09-05 disposition.
- `docs/publishing-house/install-lock.json`, `docs/publishing-house/compatibility-matrix.json`, and `docs/publishing-house/validation-report.md`: advanced the clean `kujo-skills` evidence from `1e0a2ea` to `0d41ab4` after the Publishing House fixture tests exposed the stale lock.

## Confirmed Current

- The 44 active workflow kits remain inventoried in the catalog, including Owned Agent Project, Codebase Cleanup, ten WebOps workflows, eleven Publishing House workflows, Publishing House Operator, VideoOps Production, five VideoOps stages, and the Tribunal/Relay/Workcell representative gates.
- VideoOps remains a credential-free local proof: PackWrite intake, Spec validation, Eval gates, Howl proof cards, RunLedger receipts, HyperFrames local render, ffprobe inspection, critic fail/fix/pass loop, and explicit live-provider boundaries all passed in the release gate.
- Publishing House workflows remain aligned with the committed `kujo-skills` checkout after the compatibility matrix was refreshed.
- WebOps, AI SDK/Watchdog, Relay, Tribunal, Workcell, RAG, MCP, Howl, Casefile, Cleanup, and general agent workflows retain their existing fixture/live/host boundaries.

## Compatibility Disposition

- Added: VideoOps skill-matrix relationships and tool-matrix support records for Kujo, PackWrite, Eval, Howl, RunLedger, and HyperFrames.
- Changed: Publishing House `kujo-skills` lock/matrix evidence advanced to the clean current commit used by the passing fixture tests.
- Preserved: Owned Agent Project, Publishing House, WebOps, AI SDK/Watchdog showcase, Dispatch approval router, Relay local handoff, Workcell local container boundary, Tribunal advisory mock decision boundary, RAG, MCP, Howl, Casefile, and Cleanup workflow relationships.
- Deferred: live VideoOps provider execution, external asset search, authenticated Lens/browser capture, licensed-media acquisition, cloud rendering, publication, hosted runners, separate-machine clean checkout proof, and dirty sibling checkout changes.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 scripts/validate_docs.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash tests/videoops-release-gate.sh
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
bash tests/release-readiness.sh
git diff --check
```

The unit suite passed after refreshing the Publishing House `kujo-skills` lock:
24 tests passed in 347.645 seconds. The release-readiness gate passed, including
static validation and Codebase Cleanup Kujo tests. The VideoOps release gate passed and
validated 6 agents, 5 specialist stages, 36 skills, 7 schemas, 3 positive/
negative schema fixtures, and the integration proof.

`bash workcell-execution-gate/scripts/run.sh` validated and inspected the
package but returned exit code 3 because Colima was not running and Workcell
could not connect to the configured user-specific Colima Docker socket. The run wrote the
expected blocked completion receipt with `cleanup_status: complete`; Docker
execution and required `hello.txt` artifact export were not directly verified
in this pass.

## Partial Verification Boundaries

- Live-provider, paid-provider, external asset, authenticated browser, hosted-runner, cloud-render, and external publication behavior was not run.
- Dirty local sibling checkout files were not treated as authoritative catalog evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- Workcell execution was host-blocked by the stopped Colima/Docker daemon; validate/inspect and blocked receipt generation were verified.
- `$kujo-workflow-auditor` was unavailable; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- VideoOps live adapter work across `kujo-agents`, `kujo-skills`, `kujo-videoops`, PackWrite, Eval, Howl, RunLedger, HyperFrames, and Lens.
- Publishing House lock drift if `kujo`, Dispatch, Agents SDK, `kujo-agents`, or `kujo-skills` commits change after the current fixture matrix.
- Workcell v1.1.0 host proof once Colima/Docker is running.
- AI SDK, Watchdog, Dispatch, Relay, and RunLedger telemetry correlation changes that may justify a future composed workflow.
- Clean-machine, live-provider, authenticated browser, hosted-runner, and publication evidence for currently deferred relationships.
