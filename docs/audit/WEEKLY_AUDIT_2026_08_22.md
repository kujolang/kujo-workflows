# Weekly Kujo Workflows Audit - 2026-08-22

Audit ID: `kujo-workflows-audit-2026-08-22`
Captured: `2026-08-22T02:20:00-04:00` (UTC `2026-08-22T06:20:00Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under `$KUJO_REPOS`, prioritizing repositories changed since the 2026-08-15 run. The named skill `$kujo-workflow-auditor` was not found on disk, so the audit followed the repository's `AGENTS.md`, `README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo-skills` | `f0cf740` | Updated audit and Publishing House lock baselines. SearchBridge and Workcell skill evidence changed, and AssetWorks, PressWire, ReaderSignal, and VersionSeal skill hardening notes changed; no workflow input or outcome contract migration was required. |
| `kujo-agents` | `6c9b499` | Preserved Publishing House workflow bindings; the weekly agent audit added deferred Static Commerce Operator and Image Authenticity Analyst records without creating supported workflow relationships here. |
| `kujo` | `b03e3d5` | Updated Publishing House local runtime lock to the checked-out `1.0.1` runtime used by fixture validation. |
| `ai-chat` | `8e4c6f0` committed main; dirty checkout present | Preserved prior AI SDK/Watchdog showcase boundary. Stream timeout and tool-pathing fixes are compatible sibling evidence; dirty local experiment files were not used as catalog evidence. |
| `workcell` | `7bcdb7f` | Preserved Workcell gate boundary. Git patch secret-redaction and rejection hardening tightens evidence handling but does not change the workflow's Docker/Podman trust boundary or receipt contract. |
| `watchdog` | `e009ecd` | Preserved AI SDK/Watchdog showcase boundary. Pricing catalog refresh is dated provider-cost evidence, not a workflow contract migration. |
| `source`, `agents.kujolang.ai`, `kujo-docs`, `truthlens`, `kujo-hyperframes`, WebOps and Publishing House tool repositories | current Aug 13-18 commits where present | No active workflow relationship was added or promoted; changes were product, docs, validation, or release-evidence updates outside current workflow contracts. |

## Updated Workflows And Records

- `docs/publishing-house/install-lock.json`: advanced `kujo`, `kujo-agents`, and `kujo-skills` to the current clean sibling checkouts so required capability preflight again matches local proof inputs.
- `docs/publishing-house/compatibility-matrix.json`: recorded the same tested commits and audit timestamp for the verified fixture boundary.
- `docs/audit/workflow-catalog.json`, `docs/audit/skill-compatibility-matrix.json`, and `docs/audit/tool-integration-matrix.json`: advanced audit IDs to 2026-08-22 and refreshed current sibling commit evidence for affected relationships.
- `docs/audit/README.md`, `docs/publishing-house/validation-report.md`, and this file: recorded the weekly audit disposition, validation boundary, and next watch list.

## Confirmed Current

- The eleven Publishing House workflows remain aligned with `kujo-agents` role/workflow bindings, locked tool commits, canonical `kujo-publishing-house-workflows`, Dispatch state, Agents SDK no-network runner receipts, and the eight editorial tool contracts.
- The ten WebOps workflows remain aligned with SiteProbe, SearchBridge, ContentGraph, Lens, ShipCheck, and WebOps skill boundaries. Recent sibling evidence does not add supported output claims to this catalog.
- `agency-runner`, `agency-verified-fix-loop`, `feature-card-workflow`, `ai-sdk-muzzle-benchmark`, `ai-sdk-watchdog-showcase`, `enterprise-dispatch-approval-router`, `mcp-agent-gateway-review`, `rag-enterprise-knowledge-gate`, `casefile-incident-evidence-packet`, `howl-content-factory`, `loop-engineering`, `codebase-cleanup`, `docsgen-repo-contract-runner`, `tribunal-decision-gate`, `relay-lifecycle-handoff`, and `workcell-execution-gate` remain aligned with their cataloged paths, commands, skills, tools, documents, contracts, and stated acceptance boundaries.

## Compatibility Disposition

- Changed: Publishing House required capability preflight now accepts current `kujo`, `kujo-agents`, and `kujo-skills` commits used by local fixture validation.
- Preserved: Publishing House toolchain relationships, WebOps toolchain relationships, AI SDK/Watchdog showcase boundaries, Dispatch orchestration, Relay local handoff, Workcell local container boundary, and Tribunal advisory mock decision boundary.
- Deferred: the new Static Commerce Operator and Image Authenticity Analyst agent opportunities remain deferred or rejected in `kujo-agents` and are not supported workflow integrations. Agency-runner's provider/consumer-heavy relationships and docsgen/RAG relationships remain compatible-but-under-tested pending provider, consumer, authenticated browser, or clean target-repo evidence. Live Publishing House adapters, authenticated browser flows, live providers, hosted runners, and separate-machine clean checkout proof remain external verification boundaries.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 scripts/validate_docs.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash scripts/run-publishing-house-fixture.sh --out /tmp/publishing-house-proof-20260822
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
bash workcell-execution-gate/scripts/run.sh
git diff --check
```

`workcell-execution-gate/scripts/run.sh` validated the Workcell package and completion receipt on this host. Broader Workcell Docker/Podman backend coverage remains governed by the Workcell repository's own host-runtime validation matrix.

## Partial Verification Boundaries

- Live-provider, credentialed browser, hosted-runner, paid-provider, and external publication behavior was not run.
- AI Chat's dirty local checkout was not treated as authoritative beyond committed main evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable in local skill paths; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- `kujo-skills` drift that changes `kujo-publishing-house-workflows`, SearchBridge, Workcell, or WebOps workflow skills from documentation expansion into contract migration.
- Publishing House install-lock drift whenever sibling tool, agent, skill, or runtime commits change after the proof matrix.
- AI Chat browser/tool surfaces after the current dirty checkout is either committed or discarded.
- Static Commerce Operator and Image Authenticity Analyst proposals in `kujo-agents`; do not promote them without stable skills, workflow contracts, and explicit authority boundaries.
- Workcell secret-redaction behavior if future workflows consume Git patch artifacts directly.
- Clean-machine, live-provider, and hosted-runner verification evidence for the under-tested catalog relationships.
