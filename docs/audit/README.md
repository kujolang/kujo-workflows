# Kujo Workflow Ecosystem Audit

Audit ID: `kujo-workflows-audit-2026-08-29`
Captured: `2026-08-29T06:03:44-04:00` (UTC `2026-08-29T10:03:44Z`)

The machine-readable source of truth is [`workflow-catalog.json`](workflow-catalog.json). The validator resolves skill identities from the checked-out `kujo-skills` repository and tool identities from sibling repositories; it fails closed on missing skills, non-canonical paths, unknown tools, missing workflow entries, or missing documentation.

## Scope and disposition

- 44 active workflow kits are inventoried from the catalog and repository README, including the Owned Agent Project proof, ten WebOps kits, the reusable Codebase Cleanup workflow, eleven Publishing House kits, the VideoOps production initializer, and five VideoOps stage kits.
- The catalog resolves every Publishing House kit to the dedicated `kujo-publishing-house-workflows` skill alongside Dispatch and Agents SDK guidance.
- Weekly refresh checked repositories changed in the last 7-10 days, prioritizing `kujo`, `kujo-skills`, `kujo-agents`, Dispatch, Agents SDK, AI SDK/provider packages, AI Chat, Watchdog, Relay, SSG/WebMCP, and the workflow kits that integrate with them.
- Publishing House records were updated for the current committed `kujo`, Dispatch, Agents SDK, `kujo-agents`, and `kujo-skills` checkouts; the workflow lock now matches the sibling commits used by fixture proof. Dirty sibling working-tree files in `kujo`, `agents-sdk`, `kennel`, and `spec` were excluded from catalog claims.
- The new Owned Agent Project workflow is now part of the catalog and remains aligned with Kujo 1.0.2 Agent Project commands, Kennel dependency installation, Agents SDK fixture execution, and Eval delegation.
- WebOps and general workflow skill routing records were preserved: recent AI SDK provider-driver work, SSG WebMCP output, Watchdog Hermes routing, Relay v1.1.0 hardening, and Kujo Agents provider-neutral adapters do not create new supported workflow integrations without separate contracts.
- AI Chat committed main evidence is now `ed3ff2c`; managed Hermes profiles and tool-selection changes remain supporting app behavior, not new workflow catalog entries.
- Tribunal, Relay, and Workcell were inspected at implementation, schema, documentation, and test surfaces. Dedicated contract-gated integrations now cover advisory decisions, local pause/resume handoffs, and bounded Workcell execution without making existing production workflows depend on them.
- “Workso” was not found as a repository, manifest, or canonical skill. The actual current execution sandbox is Workcell; the alias is recorded and rejected by the validator.
- The catalog is safe as a documentation/inventory contract after validation. Individual workflows remain production-capable with limitations unless their own fixture, provider, host, and approval prerequisites are satisfied.
- Nine previously under-tested skill relationships still have deterministic positive and negative boundary fixtures; they remain under-tested pending provider, consumer, and fully authenticated browser evidence.
- The 2026-07-28 Markdown cleanup removed stale review docs, including `AGENCY_VERIFIED_FIX_LOOP_HOWTO.md` and `loop-engineering/WORKFLOW.md`; surviving workflow docs no longer link to those deleted files.

## Files

- [`workflow-catalog.json`](workflow-catalog.json) — machine-readable active workflow inventory and canonical skill/tool references.
- [`skill-compatibility-matrix.json`](skill-compatibility-matrix.json) — workflow-to-skill status, action, and evidence.
- [`tool-integration-matrix.json`](tool-integration-matrix.json) — current/proposed tool use, gaps, risks, tests, and rollback.
- [`WEEKLY_AUDIT_2026_08_29.md`](WEEKLY_AUDIT_2026_08_29.md) — latest weekly drift review, affected repositories, compatibility disposition, validation, and next watch list.
- [`WEEKLY_AUDIT_2026_08_22.md`](WEEKLY_AUDIT_2026_08_22.md) — previous weekly drift review.
- [`WEEKLY_AUDIT_2026_08_15.md`](WEEKLY_AUDIT_2026_08_15.md) — previous weekly drift review.
- [`WEEKLY_AUDIT_2026_08_08.md`](WEEKLY_AUDIT_2026_08_08.md) — previous weekly drift review.
- [`WEEKLY_AUDIT_2026_08_01.md`](WEEKLY_AUDIT_2026_08_01.md) — earlier weekly drift review.
- [`markdown-cleanup-summary-2026-07-28.md`](markdown-cleanup-summary-2026-07-28.md) — durable policy and outcome from the July Markdown cleanup; exact bulk inventories remain available in Git history.

Validate from the repository root:

```bash
python3 scripts/validate_catalog.py --json
python3 scripts/validate_docs.py
python3 -m unittest discover -s tests -p 'test_*.py'
```
