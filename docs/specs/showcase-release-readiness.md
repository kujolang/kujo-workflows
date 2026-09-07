# Spec: Kujo Workflows technical preview

| | |
|---|---|
| **Priority** | high |
| **Status** | ready |
| **Version** | 0.6.0 |
| **ID** | `2f091169-b4cf-4d24-9783-617129d055f8` |
| **Estimated Effort** | medium |

**Tags:** `release-readiness`, `documentation`, `showcase`, `ci`, `technical-preview`

## Goal

Ship a portable, truthful 0.6.0 workflow-kit distribution with 44 catalog workflows, the verified Publishing House lifecycle and operator, a harness-neutral VideoOps initializer, and a credential-free VideoOps production proof.

## Background

A 2026-08-08 release-readiness review found that the local workflow demos are useful and largely healthy, but the public repository surface has missing release metadata, broken documentation references, host-specific commands, incomplete CI coverage, stale proof claims, and a failing strict agency demo.


## Scope

Maintain repository-level release metadata and public policy files; present the root README as a portable technical-preview landing page; keep Markdown links and copyable commands portable; preserve concise audit evidence; run self-contained and clean-checkout CI validation; keep the strict agency fixture gate deterministic; and align launch-readiness documentation with current evidence.

## Non-Goals

- Deploy hosted workflow runners.
- Run live external providers or spend provider credits.
- Claim production or enterprise readiness.
- Publish packages or deploy hosted workflow runners.
- Change branch protection or repository visibility.

## Relevant Systems

- `Kujo Spec`
- `ShipCheck`
- `GitHub Actions`
- `Agency Verified Fix Loop`
- `Workflow catalog and contract validators`
- `VideoOps`
- `HyperFrames`
- `FFmpeg`

## Likely Files

- `README.md`
- `LICENSE`
- `VERSION`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CODE_OF_CONDUCT.md`
- `package.json`
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
2. The repository contains an MIT LICENSE, VERSION, and CHANGELOG.md appropriate for a 0.6.0 technical preview.
3. README, VERSION, package metadata, changelog, and the canonical Spec agree on version 0.6.0.
4. The catalog contains 44 active workflows, including all eleven independently runnable Publishing House workflow kits, the Publishing House Operator, the VideoOps production initializer, and five VideoOps stage kits.
5. The locked Publishing House installer, Kujo-native doctor, and all-eleven offline fixture complete from the final install path with resolvable record references and contract-loaded agent receipts.
6. Ten WebOps workflow kits run in deterministic fixture mode with resumable evidence and explicit approval boundaries.
7. The VideoOps release gate validates five Kujo-native stages, 35 skills, seven schemas, PackWrite intake, Spec and Eval gates, Howl proof cards, RunLedger evidence, a real HyperFrames 1080p30 render with audio, and a bounded critic revision loop without credentials or paid calls.
8. The Kujo-native VideoOps production initializer preserves an arbitrary request, refuses unsafe or accidental replacement, and emits a non-fixture VideoOps Producer invocation.
9. WebOps site-profile and history schemas preserve credential references, stable finding states, and separate recommendation/action/outcome records.
10. Public contribution, support, security, and conduct policies are present and linked from the README.
11. Every checked-in relative Markdown link resolves to an existing file or local anchor target.
12. Active documentation contains no maintainer-specific /Users path and all copyable commands state or encode their working directory.
13. The root README distinguishes experimental, production-capable-with-limitations, and production-ready workflows and provides one portable first-run path.
14. GitHub Actions runs self-contained contract, unit, documentation, metadata, and static validation on pushes and pull requests.
15. Portable release-readiness and tracked-file clean-checkout gates run locally and in GitHub Actions.
16. Agency Verified Fix Loop completes with STRICT=1 and produces passing ChangeBucket and ShipCheck gates.
17. Catalog, contract, unit, Workcell, Tribunal, Relay, and representative workflow validations pass in the current checkout.
18. The required validation set passes from a detached clean local worktree without relying on untracked files.
19. The tracked worktree is clean, committed in meaningful commits, and pushed without rewriting history.

## Eval Requirements

| # | Description | Check Type |
|---|---|---|
| 1 | Validate the task Spec in strict mode. | `command_succeeds` |
| 2 | Validate repository documentation and release metadata. | `command_succeeds` |
| 3 | Run repository unit tests. | `command_succeeds` |
| 4 | Run the portable release-readiness gate. | `command_succeeds` |
| 5 | Run the tracked-file clean-checkout gate. | `command_succeeds` |
| 6 | Run the host-dependent VideoOps integration gate. | `command_succeeds` |
| 7 | Run the strict agency workflow. | `command_succeeds` |
| 8 | Pass the ShipCheck release gate. | `command_succeeds` |

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

1. The maintainer explicitly authorized the v0.3.0 release and tag on 2026-08-14.
2. The maintainer explicitly authorized the v0.4.0 release and tag on 2026-09-02.
3. Changing the repository's technical-preview scope requires maintainer approval.

---

*Generated by Spec v0.6.0*
