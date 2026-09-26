# Kujo Workflow Ecosystem Audit

Audit ID: `kujo-workflows-audit-2026-09-26`
Captured: `2026-09-26T06:06:17-04:00` (UTC `2026-09-26T10:06:17Z`)

The machine-readable source of truth is [`workflow-catalog.json`](workflow-catalog.json). The validator resolves skill identities from the checked-out `kujo-skills` repository and tool identities from sibling repositories; it fails closed on missing skills, non-canonical paths, unknown tools, missing workflow entries, or missing documentation.

## Scope and disposition

- 44 active workflow kits are inventoried from the catalog and repository README, including the Owned Agent Project proof, ten WebOps kits, the reusable Codebase Cleanup workflow, eleven Publishing House kits, the VideoOps production initializer, and five VideoOps stage kits.
- The catalog resolves every Publishing House kit to the dedicated `kujo-publishing-house-workflows` skill alongside Dispatch and Agents SDK guidance, and now links AssetWorks and ReaderSignal workflow skills where those tool-owned records are directly consumed.
- Weekly refresh checked repositories changed in the last 7-10 days, prioritizing `kujo`, `kujo-skills`, Publishing House tool repositories, Workcell, Tribunal, Relay, Dispatch, Eval, AI Chat, Watchdog, Lens, SiteProbe, Howl, RunLedger, Scout, Kennel, Muzzle, SSG, and related workflow kits.
- Publishing House support-lock records were advanced for clean current support evidence after the unit suite exposed stale support evidence, including Kujo `v1.5.0`, Dispatch `a01a365`, `kujo-skills` `ab77f5c`, StoryDesk `18adafa`, Dossier `c3ab2e2`, GalleyPack `e4acb84`, BluePencil `9d38046`, VersionSeal `cf14a2d`, PressWire `3b80332`, ReaderSignal `512963e`, and AssetWorks `63d892d`; the all-eleven fixture is now blocked at the VersionSeal `0.3.0` to PressWire `0.2.0` approval-record boundary.
- Owned Agent Project remains aligned with Kujo Agent Project commands, Kennel dependency installation, Agents SDK fixture execution, and Eval delegation.
- Publishing House AssetWorks and ReaderSignal skill relationships are represented in the catalog and compatibility matrix without promoting live media adapters, analytics, publication, or measurement support.
- VideoOps skill and tool relationships remain represented in the compatibility and tool matrices while live providers, external assets, authenticated capture, cloud rendering, and publication remain deferred.
- WebOps and general workflow skill routing records were preserved: recent AI SDK, Watchdog, Dispatch, Relay, Workcell, SSG/WebMCP, and Kujo Agents hardening or telemetry work does not create new supported workflow integrations without separate contracts.
- Tribunal, Relay, and Workcell were inspected at implementation, schema, documentation, and test surfaces. Dedicated contract-gated integrations now cover advisory decisions, local pause/resume handoffs, and bounded Workcell execution without making existing production workflows depend on them.
- “Workso” was not found as a repository, manifest, or canonical skill. The actual current execution sandbox is Workcell; the alias is recorded and rejected by the validator.
- The catalog is safe as a documentation/inventory contract after validation. Individual workflows remain production-capable with limitations unless their own fixture, provider, host, and approval prerequisites are satisfied. Workcell execution was blocked during the 2026-09-26 pass because the configured Docker socket was unavailable.
- Nine previously under-tested skill relationships still have deterministic positive and negative boundary fixtures; they remain under-tested pending provider, consumer, and fully authenticated browser evidence.
- The 2026-07-28 Markdown cleanup removed stale review docs, including `AGENCY_VERIFIED_FIX_LOOP_HOWTO.md` and `loop-engineering/WORKFLOW.md`; surviving workflow docs no longer link to those deleted files.

## Files

- [`workflow-catalog.json`](workflow-catalog.json) — machine-readable active workflow inventory and canonical skill/tool references.
- [`skill-compatibility-matrix.json`](skill-compatibility-matrix.json) — workflow-to-skill status, action, and evidence.
- [`tool-integration-matrix.json`](tool-integration-matrix.json) — current/proposed tool use, gaps, risks, tests, and rollback.
- [`WEEKLY_AUDIT_2026_09_26.md`](WEEKLY_AUDIT_2026_09_26.md) — latest weekly drift review, affected repositories, compatibility disposition, validation, and next watch list.
- [`WEEKLY_AUDIT_2026_09_19.md`](WEEKLY_AUDIT_2026_09_19.md) — previous weekly drift review.
- [`WEEKLY_AUDIT_2026_09_12.md`](WEEKLY_AUDIT_2026_09_12.md) — previous weekly drift review.
- [`WEEKLY_AUDIT_2026_09_05.md`](WEEKLY_AUDIT_2026_09_05.md) — previous weekly drift review.
- [`WEEKLY_AUDIT_2026_08_29.md`](WEEKLY_AUDIT_2026_08_29.md) — previous weekly drift review.
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
