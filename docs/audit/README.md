# Kujo Workflow Ecosystem Audit

Audit ID: `kujo-workflows-audit-2026-07-25`
Captured: `2026-07-25T06:08:02-04:00` (UTC `2026-07-25T10:08:02Z`)

The machine-readable source of truth is [`workflow-catalog.json`](workflow-catalog.json). The validator resolves skill identities from the checked-out `kujo-skills` repository and tool identities from sibling repositories; it fails closed on missing skills, non-canonical paths, unknown tools, missing workflow entries, or missing documentation.

## Scope and disposition

- 15 active workflow kits are inventoried from the catalog and repository README.
- 45 workflow-to-skill relationships are checked against the `kujo-skills` checkout: 36 compatible and 9 compatible but under-tested; no broken, deprecated, or migration-required relationship was found.
- Weekly refresh checked repositories changed in the last 7-10 days, prioritizing AI Chat, AI SDK, Watchdog, Relay, RAG, the command-parser repair sweep for ChangeBucket/Fence/PatchBrief/ShipCheck, Eval command-policy gates, Spec runtime-parity handling, Workcell, Tribunal, and the refreshed `kujo-skills` checkout at `b0233fdfba4b589429f1bd4b73d11581c0d3985c`.
- AI Chat, Watchdog, AI SDK, and Relay records were updated or preserved to reflect current repo-backed tool boundaries: pane benchmark profiles and provider-neutral tools remain related surfaces, AI SDK stream/tool-call fixes remain SDK-owned, Watchdog named upstreams/agent insights/token visibility remain compatible additions, and Relay provider-generated tool planning remains bounded local-alpha behavior with unresolved sibling smoke boundaries.
- Tribunal, Relay, and Workcell were inspected at implementation, schema, documentation, and test surfaces. Dedicated contract-gated integrations now cover advisory decisions, local pause/resume handoffs, and bounded Workcell execution without making existing production workflows depend on them.
- “Workso” was not found as a repository, manifest, or canonical skill. The actual current execution sandbox is Workcell; the alias is recorded and rejected by the validator.
- The catalog is safe as a documentation/inventory contract after validation. Individual workflows remain production-capable with limitations unless their own fixture, provider, host, and approval prerequisites are satisfied.
- Nine previously under-tested skill relationships now have deterministic positive and negative boundary fixtures; they remain under-tested pending provider, consumer, and fully authenticated browser evidence.

## Files

- [`workflow-catalog.json`](workflow-catalog.json) — machine-readable active workflow inventory and canonical skill/tool references.
- [`skill-compatibility-matrix.json`](skill-compatibility-matrix.json) — workflow-to-skill status, action, and evidence.
- [`tool-integration-matrix.json`](tool-integration-matrix.json) — current/proposed tool use, gaps, risks, tests, and rollback.
- [`REPOSITORY_BASELINE.md`](REPOSITORY_BASELINE.md) — branch, SHA, dirty state, and untracked-file snapshot.
- [`PHASE2_REPOSITORY_STATE.md`](PHASE2_REPOSITORY_STATE.md) — Phase 2 tool/runtime state and Relay fix provenance.
- [`CHANGE_REPORT.md`](CHANGE_REPORT.md) — implemented changes and verification evidence.
- [`DEFERRED_OPPORTUNITIES.md`](DEFERRED_OPPORTUNITIES.md) — intentionally unimplemented integrations and next actions.
- [`TOOL_REVIEW.md`](TOOL_REVIEW.md) — implementation-level Tribunal, Relay, and Workcell findings.
- [`VERIFICATION.md`](VERIFICATION.md) — exact commands, passes, partial results, and limitations.
- [`PHASE2_EVIDENCE.md`](PHASE2_EVIDENCE.md) — Relay root cause/fix, browser-loop evidence, under-tested relationship evidence, and contract results.
- [`WEEKLY_AUDIT_2026_07_25.md`](WEEKLY_AUDIT_2026_07_25.md) — latest weekly drift review, affected repositories, compatibility disposition, validation, and next watch list.
- [`WEEKLY_AUDIT_2026_07_18.md`](WEEKLY_AUDIT_2026_07_18.md) — prior weekly drift review and Relay provider-tool partial boundary.

Validate from the repository root:

```bash
python3 scripts/validate_catalog.py --json
python3 -m unittest discover -s tests -p 'test_*.py'
```
