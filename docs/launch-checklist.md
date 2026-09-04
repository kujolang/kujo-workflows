# Launch Checklist

Current launch scope: `locally verified support/distribution technical preview` (`0.5.0`). Repository-owned validation, WebOps fixture workflows, the locked Publishing House all-eleven installation proof, the Publishing House Operator control layer, and the credential-free VideoOps integration proof pass on the development host. Hosted runner behavior, live external-provider workflows, and clean-machine installation on a separate host are not complete.

The synchronized three-tool contract is `docs/webops-toolchain-contract.json`.
Its release evidence is
`docs/evidence/WEBOPS_TOOLCHAIN_RELEASE_QUALIFICATION_2026-08-11.md`.

## Self-Contained Gates

These commands run from the repository root without sibling tool checkouts, except for the optional Spec CLI command:

- [x] Release metadata and Markdown links: `python3 scripts/validate_docs.py`.
- [x] Catalog structure: `python3 scripts/validate_catalog.py --structure-only --json`.
- [x] Contract schemas and examples: `python3 scripts/validate_contracts.py`.
- [x] Unit validation: `python3 -m unittest discover -s tests -p 'test_*.py'`. The sibling-tool relationship test skips in standalone clones.
- [x] Shell, JavaScript, Python, JSON, and YAML syntax validation.
- [x] Formatting: `git diff --check`.
- [x] Release-readiness Spec: `spec validate kujo-workflows.spec.yml --strict`.
- [x] Version agreement across README, VERSION, package metadata, changelog, and Spec.
- [x] Public contribution, support, security, and conduct guidance.
- [x] Portable release gate: `bash tests/release-readiness.sh`.
- [x] Tracked-file clean-checkout gate: `bash tests/clean-checkout.sh`.

Individual contract instances use both required arguments. For example:

```bash
python3 scripts/validate_contract_instance.py \
  contracts/workcell/work-package.v1.schema.json \
  contracts/examples/workcell-work-package.json
```

## Host-Dependent Gates

These commands require the local Kujo runtime, sibling tool repositories, and any named host dependency:

- [x] Cross-repository relationship contracts: `bash tests/skill_relationship_contracts.sh`.
- [x] Full catalog identity and repository resolution: `python3 scripts/validate_catalog.py --json`.
- [x] Agency Verified Fix Loop strict gate: `agency-runner/bin/agency-loop demo-verified-loop --strict`.
- [x] Representative Workcell workflow: `bash workcell-execution-gate/scripts/run.sh`.
- [x] Representative Tribunal workflow: `bash tribunal-decision-gate/scripts/run.sh`.
- [x] Representative Relay workflow: `bash relay-lifecycle-handoff/scripts/run.sh`.
- [x] Six catalog workflow fixture demos documented in the root README.
- [x] Loop Engineering, AI SDK + Watchdog, and AI SDK + Muzzle fixture demos.
- [x] Workcell proof: `workcell run --file docs/workcell-launch-gate.json --repo . --no-pull`.
- [x] Detached clean local worktree validation on the development host.
- [x] Locked Publishing House installation and all-eleven first run from a tracked archive on the development host: `bash tests/publishing-house-install.sh`.
- [x] Five-stage VideoOps proof with PackWrite, Spec, Eval, Howl, RunLedger, real HyperFrames rendering, audio mux/inspection, asset fail-closed behavior, and bounded revision: `bash tests/videoops-release-gate.sh`.
- [ ] Clean-checkout installation and workflow validation on a separate machine.
- [ ] Live-provider and fully authenticated browser validation.
- [ ] Hosted runner validation.

## Workcell Proof Notes

The development-host proof uses the local `kujolang/workcell-base:local` image and a Docker/Colima socket. Keep the disposable worktree under a host path visible to the selected Docker VM:

```bash
export KUJO_REPOS=/path/to/kujo-repos
export DOCKER_HOST=unix:///path/to/docker.sock
export DOCKER_CONFIG=/tmp/kujo-workflows-docker-config
export TMPDIR="$KUJO_REPOS/.workcell-host-tmp"
workcell run --file docs/workcell-launch-gate.json --repo . --no-pull
workcell verify --run .workcell/runs/<run-id> --json
```

The exact socket path is host-specific and must not be copied from another developer's machine.

## Evidence Policy

Generated `.runs/` and `.workcell/` directories are ignored local evidence. A launch claim must name the command, exit status, and expected artifact contract; it must not link to an ignored path as if that path were part of a fresh clone.

## Forbidden Launch Actions

Hosted runner deployment, live-provider workflows, marketplace publication, live credentials, branch-protection changes, and force-pushes remain out of scope. Public releases and final tags require explicit maintainer authorization; this change does not create a `v0.5.0` tag.
