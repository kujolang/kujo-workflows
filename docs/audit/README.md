# Kujo Workflow Ecosystem Audit

Audit ID: `kujo-workflows-audit-2026-08-08`
Captured: `2026-08-08T06:03:48-04:00` (UTC `2026-08-08T10:03:48Z`)

The machine-readable source of truth is [`workflow-catalog.json`](workflow-catalog.json). The validator resolves skill identities from the checked-out `kujo-skills` repository and tool identities from sibling repositories; it fails closed on missing skills, non-canonical paths, unknown tools, missing workflow entries, or missing documentation.

## Scope and disposition

- 15 active workflow kits are inventoried from the catalog and repository README.
- 45 workflow-to-skill relationships are checked against the `kujo-skills` checkout: 36 compatible and 9 compatible but under-tested; no broken, deprecated, or migration-required relationship was found.
- Weekly refresh checked repositories changed in the last 7-10 days, prioritizing `kujo-skills`, Howl, Watchdog, Kujo v1 release-sweep repositories, AI Chat, Agents SDK, AI SDK, RAG, MCP, RunLedger, Eval, Spec, Scout, Scent, PackWrite, PatchBrief, Muzzle, SSG, Lens, ShipCheck, and Kennel.
- Howl, Watchdog, AI SDK, AI Chat, and skill-routing records were updated or preserved to reflect current repo-backed tool boundaries: Howl branded social SVG rendering is now directly covered by the content factory, Watchdog August pricing remains a compatible addition, AI SDK/provider ownership did not move, AI Chat dirty local experiments were not promoted, and the `kujo-skills` checkout is recorded at `9376808`.
- Tribunal, Relay, and Workcell were inspected at implementation, schema, documentation, and test surfaces. Dedicated contract-gated integrations now cover advisory decisions, local pause/resume handoffs, and bounded Workcell execution without making existing production workflows depend on them.
- “Workso” was not found as a repository, manifest, or canonical skill. The actual current execution sandbox is Workcell; the alias is recorded and rejected by the validator.
- The catalog is safe as a documentation/inventory contract after validation. Individual workflows remain production-capable with limitations unless their own fixture, provider, host, and approval prerequisites are satisfied.
- Nine previously under-tested skill relationships still have deterministic positive and negative boundary fixtures; they remain under-tested pending provider, consumer, and fully authenticated browser evidence.
- The 2026-07-28 markdown cleanup removed stale review docs, including `AGENCY_VERIFIED_FIX_LOOP_HOWTO.md` and `loop-engineering/WORKFLOW.md`; the catalog now points at surviving canonical workflow docs.

## Files

- [`workflow-catalog.json`](workflow-catalog.json) — machine-readable active workflow inventory and canonical skill/tool references.
- [`skill-compatibility-matrix.json`](skill-compatibility-matrix.json) — workflow-to-skill status, action, and evidence.
- [`tool-integration-matrix.json`](tool-integration-matrix.json) — current/proposed tool use, gaps, risks, tests, and rollback.
- [`WEEKLY_AUDIT_2026_08_08.md`](WEEKLY_AUDIT_2026_08_08.md) — latest weekly drift review, affected repositories, compatibility disposition, validation, and next watch list.
- [`WEEKLY_AUDIT_2026_08_01.md`](WEEKLY_AUDIT_2026_08_01.md) — previous weekly drift review.
- [`markdown-doc-triage-2026-07-25.md`](markdown-doc-triage-2026-07-25.md), [`markdown-doc-review-disposition-2026-07-28.md`](markdown-doc-review-disposition-2026-07-28.md), [`markdown-doc-needs-review-2026-07-28.md`](markdown-doc-needs-review-2026-07-28.md), and [`markdown-doc-delete-candidates-missing-2026-07-28.txt`](markdown-doc-delete-candidates-missing-2026-07-28.txt) — markdown cleanup evidence and remaining review inventory.

Validate from the repository root:

```bash
python3 scripts/validate_catalog.py --json
python3 -m unittest discover -s tests -p 'test_*.py'
```
