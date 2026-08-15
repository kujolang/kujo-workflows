# Weekly Kujo Workflows Audit - 2026-08-15

Audit ID: `kujo-workflows-audit-2026-08-15`
Captured: `2026-08-15T06:02:35-04:00` (UTC `2026-08-15T10:02:35Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under `$KUJO_REPOS`, prioritizing repositories changed since the 2026-08-08 run. The named skill `$kujo-workflow-auditor` was not found on disk, so the audit followed the repository's `AGENTS.md`, `README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo-skills` | `b931c68` | Updated audit and Publishing House lock baselines; weekly skill drift changed ContentGraph, Lens, SearchBridge, ShipCheck, SiteProbe, Kujo core, and standard-library guidance, not Publishing House workflow skill content. |
| `kujo-workflows` | `a1dd52f` plus this audit | Fixed stale Publishing House `kujo-skills` lock after sibling drift made required capability preflight fail closed. |
| `kujo-agents` | `823ea12` | Confirmed Publishing House tool/workflow bindings and role contract references match the eleven workflow kits. |
| `storydesk`, `dossier`, `bluepencil`, `presswire`, `readersignal`, `assetworks`, `versionseal` | current Aug 14 commits | Preserved Publishing House tool relationships; changes were portable validation, OpenSSL runtime, or CI updates except GalleyPack. |
| `galleypack` | `5a9ec24` | Preserved package/checksum relationship; materialization hardening remains compatible with fixture proof. |
| `contentgraph`, `siteprobe`, `lens`, `searchbridge`, `shipcheck` | current Aug 11-13 commits | Preserved WebOps catalog relationships; skill updates document new flags, evidence, or validation guidance without changing workflow inputs or supported outcomes. |
| `ai-chat` | `479ce92` committed main; dirty checkout present | Preserved prior boundary; dirty local experiment files were not used as catalog evidence. |
| `ai-sdk`, `watchdog`, `dispatch`, `relay`, `workcell`, `tribunal` | current Aug 11-12 commits | Updated or preserved tool matrix version evidence; no workflow contract migration required. |

## Updated Workflows And Records

- `docs/publishing-house/install-lock.json`: advanced `kujo-skills` from `50d299a` to `b931c68` so the checked-out sibling skill repository again satisfies required capability preflight.
- `docs/publishing-house/compatibility-matrix.json`: recorded the same `kujo-skills` commit and test timestamp for the verified fixture boundary.
- `docs/audit/workflow-catalog.json`, `docs/audit/skill-compatibility-matrix.json`, and `docs/audit/tool-integration-matrix.json`: advanced audit IDs to 2026-08-15 and refreshed current sibling commit evidence.
- `docs/audit/README.md` and this file: recorded the weekly audit disposition, validation boundary, and next watch list.

## Confirmed Current

- The eleven Publishing House workflows remain aligned with `kujo-agents` role/workflow bindings, locked tool commits, canonical `kujo-publishing-house-workflows`, Dispatch state, Agents SDK no-network runner receipts, and the eight editorial tool contracts.
- `webops-site-bootstrap`, `webops-weekly-site-health`, `webops-weekly-search-intelligence`, `webops-weekly-content-intelligence`, `webops-post-publish`, `webops-content-refresh`, `webops-monthly-seo-review`, `webops-quarterly-content-portfolio`, `webops-ai-visibility-benchmark`, and `webops-finding-to-fix` remain aligned with their current tool/skill contract boundaries.
- `agency-runner`, `agency-verified-fix-loop`, `feature-card-workflow`, `ai-sdk-muzzle-benchmark`, `ai-sdk-watchdog-showcase`, `enterprise-dispatch-approval-router`, `mcp-agent-gateway-review`, `rag-enterprise-knowledge-gate`, `casefile-incident-evidence-packet`, `howl-content-factory`, `loop-engineering`, `codebase-cleanup`, `docsgen-repo-contract-runner`, `tribunal-decision-gate`, `relay-lifecycle-handoff`, and `workcell-execution-gate` remain aligned with their cataloged paths, commands, skills, tools, documents, contracts, and stated acceptance boundaries.

## Compatibility Disposition

- Changed: Publishing House required capability preflight now accepts current `kujo-skills` commit `b931c68`.
- Preserved: Publishing House toolchain relationships, WebOps toolchain relationships, Howl social rendering coverage, AI SDK/Watchdog showcase boundaries, Dispatch orchestration, Relay local handoff, Workcell local container boundary, and Tribunal advisory mock decision boundary.
- Deferred: agency-runner's seven provider/consumer-heavy relationships and docsgen/RAG relationships remain compatible-but-under-tested pending provider, consumer, authenticated browser, or clean target-repo evidence. Live Publishing House adapters, authenticated browser flows, live providers, hosted runners, and separate-machine clean checkout proof remain external verification boundaries.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash scripts/run-publishing-house-fixture.sh --out /tmp/publishing-house-proof-20260815
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
bash workcell-execution-gate/scripts/run.sh
```

`workcell-execution-gate/scripts/run.sh` produced valid work-package and completion-receipt contract instances, then exited blocked because Docker was unavailable at `unix:///var/run/docker.sock`. This is a host runtime boundary, not a catalog compatibility pass.

## Partial Verification Boundaries

- Live-provider, credentialed browser, hosted-runner, paid-provider, and external publication behavior was not run.
- AI Chat's dirty local checkout was not treated as authoritative beyond committed main evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable in local skill paths; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- `kujo-skills` drift that changes `kujo-publishing-house-workflows` or any WebOps workflow skill from documentation expansion into contract migration.
- Publishing House install-lock drift whenever sibling tool commits change after the proof matrix.
- AI Chat browser/tool surfaces after the current dirty checkout is either committed or discarded.
- SiteProbe signed artifact verification, SearchBridge batch/replay evidence, ContentGraph incremental cache/GraphML/SARIF exports, and Lens quick-check support before promoting new workflow outputs.
- Clean-machine, live-provider, and hosted-runner verification evidence for the under-tested catalog relationships.
