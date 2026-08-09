# Spec: Prepare Kujo Workflows for external showcasing

| | |
|---|---|
| **Priority** | high |
| **Status** | ready |
| **Version** | 1.0.0 |
| **ID** | `2f091169-b4cf-4d24-9783-617129d055f8` |
| **Estimated Effort** | medium |

**Tags:** `release-readiness`, `documentation`, `showcase`, `ci`, `technical-preview`

## Goal

Make the repository's technical-preview release surface portable, truthful, legally distributable, continuously validated, and reproducible from a clean checkout.

## Background

A 2026-08-08 release-readiness review found that the local workflow demos are useful and largely healthy, but the public repository surface has missing release metadata, broken documentation references, host-specific commands, incomplete CI coverage, stale proof claims, and a failing strict agency demo.


## Scope

Add repository-level release metadata; rewrite the root README as a portable technical-preview landing page; repair missing Markdown links; replace maintainer-specific paths; condense obsolete cleanup inventories; add self-contained CI validation; make the strict agency fixture gate deterministic; and refresh launch-readiness and audit documentation from current evidence.

## Non-Goals

- Deploy hosted workflow runners.
- Run live external providers or spend provider credits.
- Claim production or enterprise readiness.
- Publish packages, releases, or tags.
- Change branch protection or repository visibility.

## Relevant Systems

- `Kujo Spec`
- `ShipCheck`
- `GitHub Actions`
- `Agency Verified Fix Loop`
- `Workflow catalog and contract validators`

## Likely Files

- `README.md`
- `LICENSE`
- `VERSION`
- `CHANGELOG.md`
- `Makefile`
- `examples/README.md`
- `.github/workflows/validate.yml`
- `scripts/validate_docs.py`
- `docs/launch-checklist.md`
- `docs/audit/README.md`
- `loop-engineering/README.md`
- `loop-engineering/HOWTO.md`
- `loop-engineering/loop.spec.yml`
- `agency-verified-fix-loop/fixtures/northstar-storefront-buggy/`
- `agency-verified-fix-loop/scripts/run-loop.sh`

## Acceptance Criteria

1. ShipCheck gate passes at the repository root with no error-level findings.
2. The repository contains an MIT LICENSE, VERSION, and CHANGELOG.md appropriate for a 0.1.0 technical preview.
3. Every checked-in relative Markdown link resolves to an existing file or local anchor target.
4. Active documentation contains no maintainer-specific /Users path and all copyable commands state or encode their working directory.
5. The root README distinguishes experimental, production-capable-with-limitations, and production-ready workflows and provides one portable first-run path.
6. GitHub Actions runs self-contained contract, unit, documentation, metadata, and static validation on pushes and pull requests.
7. Agency Verified Fix Loop completes with STRICT=1 and produces passing ChangeBucket and ShipCheck gates.
8. Catalog, contract, unit, Workcell, Tribunal, Relay, and representative workflow validations pass in the current checkout.
9. The required validation set passes from a detached clean local worktree without relying on untracked files.
10. The tracked worktree is clean, committed in meaningful commits, and pushed without rewriting history.

## Eval Requirements

| # | Description | Check Type |
|---|---|---|
| 1 | Validate the task Spec in strict mode. | `command_succeeds` |
| 2 | Validate repository documentation and release metadata. | `command_succeeds` |
| 3 | Run repository unit tests. | `command_succeeds` |
| 4 | Run the strict agency workflow. | `command_succeeds` |
| 5 | Pass the ShipCheck release gate. | `command_succeeds` |

## Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | Removing dated cleanup inventories could discard useful evidence. | medium | Preserve their durable conclusions and provenance in a concise replacement before deleting bulk inventories. |
| 2 | CI cannot execute sibling-repository integration gates in an isolated checkout. | high | Keep those gates explicit as host-dependent validation and do not represent them as self-contained CI coverage. |
| 3 | Fixture changes made solely to satisfy release tools could weaken the demo. | medium | Keep metadata honest and verify that the functional ChangeBucket diff contains only the intended CSS and JavaScript changes. |

## Dependencies

- Python 3 with jsonschema
- Local Kujo runtime and sibling repositories for host-dependent workflow gates
- Docker or Podman for Workcell proof

## Review Expectations

- Review public claims for technical-preview accuracy and avoid production-readiness language.
- Verify all README commands from their documented working directory.
- Inspect the strict agency run summary and ensure only the intended CSS/JavaScript fix remains in its ChangeBucket diff.
- Confirm the condensed audit summary preserves provenance without retaining bulk disposable inventories.

## Human Approval Points

1. Publishing a release or tag remains a separate explicit decision.
2. Changing the repository's technical-preview scope requires maintainer approval.

---

*Generated by Spec v1.0.0*
