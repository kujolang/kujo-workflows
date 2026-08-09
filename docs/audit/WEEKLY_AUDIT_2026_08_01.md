# Weekly Kujo Workflows Audit - 2026-08-01

Audit ID: `kujo-workflows-audit-2026-08-01`
Captured: `2026-08-01T07:21:00-04:00` (UTC `2026-08-01T11:21:00Z`)
Prior automation run: `2026-07-25T10:01:53.963Z`

## Scope

This audit compared the Kujo workflow catalog against sibling repositories under `$KUJO_REPOS`, prioritizing repositories with commits after the prior automation run and workflow relationships that depend on those tools or skills.

Changed sibling repositories with catalog impact or watch impact:

- `kujo-skills` at `3608cb2` on branch `weekly-kujo-skills-audit-2026-07-04`: refreshed weekly skill audit drift; `kujo-agents-sdk-workflows`, `kujo-ai-chat-workflows`, `kujo-site-kit-workflows`, and `kujo-ssg-workflows` changed in the current refresh.
- `ai-chat` at `87624e3` on `main`: sidebar, hermetic smoke, port-conflict, stream-continuation, and streamed provider-error handling changes; checkout is dirty with unrelated local experiments.
- `agents-sdk` at `67feaa8` on `main`: MCP 2026 adapter helpers; no active workflow consumes this repository yet.
- `watchdog` at `d714742` on `main`: hermetic proxy tests, rate-limit stabilization, configurable load threshold, pricing snapshots, and launch-readiness proof.
- `ai-sdk` at `d3c6def` on `main`: launch-readiness proof and markdown cleanup.
- `relay` at `6487916`, `workcell` at `af119cc`, `tribunal` at `6db336c`, `rag` at `89ae758`, `dispatch` at `35b73ac`, `mcp` at `1e47562`, `howl` at `f2dacc0`, `casefile` at `6e8a6de`, `runledger` at `2fb8645`, `eval` at `aa7c111`, `spec` at `3b6002b`, `scout` at `ecc58d0`, `scent` at `73cae64`, `packwrite` at `ff47505`, `patchbrief` at `ea6f033`, `changebucket` at `373ac51`, `muzzle` at `f734e26`, and `ssg` at `fda4470`: launch-readiness, markdown-cleanup, or bounded platform fixes that did not require new workflow integrations.
- `site-kit` at `2367326`, `lens` at `d45943d`, `shipcheck` at `717b1c3`, and `fence` at `38e5a16`: launch-readiness or Workcell proof changes; no new catalog workflow relationship was validated.

## Updated Records

- `docs/audit/workflow-catalog.json`: audit ID refreshed; documentation references updated after cleanup removed `AGENCY_VERIFIED_FIX_LOOP_HOWTO.md` and `loop-engineering/WORKFLOW.md`.
- `docs/audit/skill-compatibility-matrix.json`: audit ID refreshed; `kujo-skills` checkout updated to `3608cb2`; loop-engineering evidence now points at surviving README, HOWTO, spec, and runner files.
- `docs/audit/tool-integration-matrix.json`: audit ID refreshed; AI Chat, AI SDK, Watchdog, and Relay current repository evidence and boundaries updated.
- `workcell-execution-gate/scripts/run.sh` and `workcell-execution-gate/README.md`: Workcell fixture temp root now defaults to `../.workcell-host-tmp`, matching the launch-checklist Colima mount boundary.
- `docs/audit/README.md` and root `README.md`: stale audit and loop-engineering references corrected.

## Confirmed Current

- `agency-runner`, `agency-verified-fix-loop`, `feature-card-workflow`, `ai-sdk-muzzle-benchmark`, `ai-sdk-watchdog-showcase`, `enterprise-dispatch-approval-router`, `mcp-agent-gateway-review`, `rag-enterprise-knowledge-gate`, `casefile-incident-evidence-packet`, `howl-content-factory`, `loop-engineering`, `docsgen-repo-contract-runner`, `tribunal-decision-gate`, `relay-lifecycle-handoff`, and `workcell-execution-gate` remain present with existing entry points.
- Tribunal, Relay, and Workcell contract-gated workflows remain dedicated integrations and were not promoted into composed production workflows.
- Nine under-tested skill relationships remain under-tested, not upgraded, because provider, consumer, and fully authenticated browser evidence was not added.
- `Workso` remains an alias-only rejected finding; `workcell` remains the canonical repository and skill identity.

## Compatibility Disposition

- Added: no supported workflow relationships.
- Changed: documentation-path evidence for `agency-verified-fix-loop` and `loop-engineering`; current repository SHAs/evidence boundaries for AI Chat, AI SDK, Watchdog, Relay, and `kujo-skills`.
- Preserved: all 45 workflow-to-skill relationships; 36 compatible and 9 compatible-but-under-tested.
- Deferred: Agents SDK, SiteKit, SSG, Lens, ShipCheck, and Fence remain watch items until a workflow contract and direct fixture proof exist in this repository.
- Removed: no workflow relationships. Removed documentation references were already deleted by the 2026-07-28 markdown cleanup and are no longer canonical catalog inputs.

## Verification

Directly verified in this repository:

```text
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash workcell-execution-gate/scripts/run.sh
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
git diff --check
```

Mock-verified:

- Tribunal mock decision receipt remains advisory and unsigned.
- Relay lifecycle fixture verifies local persistence and receipt export, not remote exactly-once delivery.
- Workcell fixture verifies local Docker/Podman bounded execution semantics, not hosted or microVM isolation.

Partially verified or deferred:

- Live-provider AI SDK, AI Chat, Watchdog, browser, and web-search behavior remains credential-, environment-, and artifact-review gated.
- AI Chat sibling checkout is dirty, so catalog evidence is limited to committed `main` changes.
- Agents SDK MCP 2026 adapter helpers were noted as a watch item but not added to the catalog because no workflow contract exists here.
- Clean-checkout validation on a separate machine remains open from the launch checklist.

## Next Watch List

- `kujo-skills`: whether `kujo-agents-sdk-workflows`, `kujo-site-kit-workflows`, or `kujo-ssg-workflows` become backed by workflow contracts in this repository.
- `ai-chat`: stabilize and review benchmark/tool/browser surfaces after the dirty local experiment set is separated from committed product changes.
- `agents-sdk`: decide whether MCP 2026 adapter helpers warrant a dedicated workflow kit or remain sibling SDK scope.
- `watchdog`: keep pricing snapshots and load threshold claims dated and evidence-qualified.
- `relay` and `workcell`: do not compose them into broader workflows until shared recovery, scheduling, and receipt contracts are validated together.
- Launch checklist: clean-checkout workflow validation on a separate machine.
