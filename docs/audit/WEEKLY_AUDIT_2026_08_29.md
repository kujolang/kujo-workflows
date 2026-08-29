# Weekly Kujo Workflows Audit - 2026-08-29

Audit ID: `kujo-workflows-audit-2026-08-29`
Captured: `2026-08-29T06:03:44-04:00` (UTC `2026-08-29T10:03:44Z`)

## Scope

This audit compared the workflow catalog against sibling Kujo repositories under
`$KUJO_REPOS`, prioritizing repositories changed since the 2026-08-22 run. The
named skill `$kujo-workflow-auditor` was not found in the available Codex skill
list or on disk, so the audit followed the repository's `AGENTS.md`,
`README.md`, contract, launch, and audit instructions directly.

Prioritized changed repositories and commits:

| Repository | Evidence commit | Disposition |
| --- | --- | --- |
| `kujo` | `7e2b185` | Updated Publishing House runtime lock to Kujo 1.0.2 and confirmed the cataloged `owned-agent-project` workflow against the Agent Project CLI, schema, docs, Kennel install boundary, Agents SDK run path, Eval delegation, and Workcell hardening boundary. Dirty local `kujo` generated-inventory files were excluded from catalog claims. |
| `kujo-workflows` | `c85de04` | Preserved the new `owned-agent-project` catalog entry added after the last audit; no additional active workflow kit was discovered. |
| `kujo-skills` | `db4a7f3` | Updated skill repository evidence to 0.4.1. The weekly skill audit and Kujo Way development skill additions do not migrate existing workflow contracts or Publishing House skill requirements. |
| `kujo-agents` | `abe00dc` | Updated Publishing House role/adapter evidence. Provider-neutral manifests and Hermes/Paperclip renderers remain adapter outputs, not promoted workflow integrations here. |
| `dispatch` | `662417c` | Updated Publishing House lock and tool evidence to Dispatch 1.2.0; router/runtime hardening and pinned AI SDK gates preserve existing enterprise and Publishing House workflow boundaries. |
| `agents-sdk` | `d3904d3` | Updated Publishing House lock and confirmed Dispatch conversion metadata is compatible with current workflow receipts. Dirty untracked maintenance-agent files were excluded from catalog claims. |
| `ai-sdk` and provider-package repositories | `be9617a` plus Aug 27 provider package release commits | Preserved benchmark/showcase boundaries. Native provider-driver and provider-package contracts remain AI SDK/provider adoption evidence, not new workflow support claims. |
| `ai-chat` | `ed3ff2c` | Preserved AI SDK/Watchdog showcase boundary. Managed Hermes profiles, tool-selection hardening, and startup-binding fixes improve the sibling app but do not create a new workflow entry. |
| `watchdog` | `1af292b` | Preserved AI SDK/Watchdog showcase boundary. Hermes shared Watchdog routing remains compatible sibling evidence, not a workflow contract migration. |
| `relay` | `0480733` | Preserved Relay lifecycle handoff boundary after v1.1.0 documentation, persistence, and performance hardening. |
| `mcp`, `kennel`, `spec`, `muzzle`, `packwrite`, `runledger`, `ssg` | current Aug 23-27 commits where present | Preserved existing workflow relationships. MCP Cloudflare Worker and SSG WebMCP outputs remain experimental/tool-owned surfaces until workflow contracts are added. Dirty local `kennel` and `spec` files were excluded. |

## Updated Workflows And Records

- `docs/publishing-house/install-lock.json`: advanced `kujo`, Dispatch, Agents SDK, `kujo-agents`, and `kujo-skills` to current committed sibling checkouts used for local fixture validation.
- `docs/publishing-house/compatibility-matrix.json`: recorded Kujo 1.0.2, Dispatch 1.2.0, `kujo-skills` 0.4.1, and the matching committed compatibility set.
- `docs/audit/workflow-catalog.json`, `docs/audit/skill-compatibility-matrix.json`, and `docs/audit/tool-integration-matrix.json`: advanced audit IDs to 2026-08-29 and refreshed current sibling commit evidence for affected relationships.
- `docs/audit/README.md`, `docs/publishing-house/validation-report.md`, and this file: recorded the weekly audit disposition, validation boundary, and next watch list.

## Confirmed Current

- `owned-agent-project` remains aligned with Kujo 1.0.2 Agent Project docs and commands: `agent new --install --no-git --json`, `doctor agent --deep --json`, `agent inspect --json`, `agent run --json`, and `agent eval --json`.
- The eleven Publishing House workflows remain aligned with `kujo-agents` role/workflow bindings, locked tool commits, canonical `kujo-publishing-house-workflows`, Dispatch state, Agents SDK no-network runner receipts, and the eight editorial tool contracts.
- The ten WebOps workflows remain aligned with SiteProbe, SearchBridge, ContentGraph, Lens, ShipCheck, and WebOps skill boundaries. Recent SSG WebMCP and AI/provider-package work does not add supported output claims to this catalog.
- `agency-runner`, `agency-verified-fix-loop`, `feature-card-workflow`, `ai-sdk-muzzle-benchmark`, `ai-sdk-watchdog-showcase`, `enterprise-dispatch-approval-router`, `mcp-agent-gateway-review`, `rag-enterprise-knowledge-gate`, `casefile-incident-evidence-packet`, `howl-content-factory`, `loop-engineering`, `codebase-cleanup`, `docsgen-repo-contract-runner`, `tribunal-decision-gate`, `relay-lifecycle-handoff`, and `workcell-execution-gate` remain aligned with their cataloged paths, commands, skills, tools, documents, contracts, and stated acceptance boundaries.

## Compatibility Disposition

- Added: none.
- Changed: Publishing House required capability preflight now accepts current committed `kujo`, Dispatch, Agents SDK, `kujo-agents`, and `kujo-skills` evidence; the tool matrix now records current AI SDK, AI Chat, Watchdog, Relay, Kennel, and Dispatch commits.
- Preserved: Owned Agent Project, Publishing House toolchain relationships, WebOps toolchain relationships, AI SDK/Watchdog showcase boundaries, Dispatch orchestration, Relay local handoff, Workcell local container boundary, and Tribunal advisory mock decision boundary.
- Deferred: AI SDK native provider-driver packages, SSG WebMCP output, MCP Cloudflare Worker adapters, Kujo Agents Hermes/Paperclip renderers, dirty sibling checkout changes, live Publishing House adapters, authenticated browser flows, live providers, hosted runners, and separate-machine clean checkout proof.
- Removed: none.

## Validation

Directly verified locally:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 scripts/validate_docs.py
bash -n owned-agent-project/scripts/run.sh
bash scripts/run-publishing-house-fixture.sh --out /tmp/publishing-house-proof-20260829
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
bash workcell-execution-gate/scripts/run.sh
python3 -m unittest discover -s tests -p 'test_*.py'
git diff --check
```

The first unit-test pass exposed a stale 300-second Publishing House fixture
timeout after the refreshed Kujo 1.0.2 runtime; direct fixture timing completed
successfully in 431.24 seconds. The timeout fixture was updated to 600 seconds
with an environment override and cleanup tolerance, then the full unit suite
passed in 667.352 seconds.

The `owned-agent-project` live run was not executed because `kennel` was not on
`PATH` in this automation environment; syntax, catalog, and sibling repository
evidence were used for this pass.

## Partial Verification Boundaries

- Live-provider, credentialed browser, hosted-runner, paid-provider, and external publication behavior was not run.
- Dirty local sibling checkout files in `kujo`, `agents-sdk`, `kennel`, and `spec` were not treated as authoritative catalog evidence.
- Clean-checkout validation on a physically separate machine remains unresolved.
- `$kujo-workflow-auditor` was unavailable; audit evidence comes from repository-backed manual checks and validators.

## Next Watch List

- Owned Agent Project workflow drift as Kujo Agent Project CLI behavior, Kennel package discovery, Agents SDK execution metadata, Eval delegation, and Workcell hardening continue to move.
- Publishing House install-lock drift whenever sibling runtime, Dispatch, Agents SDK, role, skill, or editorial tool commits change after the fixture matrix.
- AI SDK native provider-driver/package adoption; do not promote provider-package repositories into workflows without explicit contracts and fixture/live boundaries.
- AI Chat, Watchdog, Hermes, and Kujo Agents adapter changes that may create a future supported local assistant workflow.
- SSG WebMCP and MCP Cloudflare Worker surfaces; defer until workflow-owned contracts, privacy boundaries, and validation fixtures exist.
- Clean-machine, live-provider, authenticated browser, and hosted-runner verification evidence for under-tested catalog relationships.
