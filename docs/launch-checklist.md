# Launch Checklist

Current launch scope: `locally verified support/distribution technical preview`. Workflow catalog, contracts, representative workflows, unit validation, and Workcell proof pass locally. Hosted runner behavior, live external-provider workflows, and clean-machine install/use are not complete.

## Local Gates

- [x] Catalog checked with `python3 scripts/validate_catalog.py --json`.
- [x] Contracts checked with `python3 scripts/validate_contracts.py`.
- [x] Workcell contract examples checked with `python3 scripts/validate_contract_instance.py`.
- [x] Unit validation checked with `python3 -m unittest discover -s tests -p 'test_*.py'`.
- [x] Representative Workcell workflow checked with `bash workcell-execution-gate/scripts/run.sh`.
- [x] Representative Tribunal workflow checked with `bash tribunal-decision-gate/scripts/run.sh`.
- [x] Representative Relay workflow checked with `bash relay-lifecycle-handoff/scripts/run.sh`.
- [x] Formatting checked with `git diff --check`.
- [x] Workcell proof checked with `workcell run --file docs/workcell-launch-gate.json --repo . --no-pull`.
- [ ] Clean-checkout workflow validation on a separate machine.

## Workcell Proof Notes

Workcell proof passed after building `kujolang/workcell-base:local` with `DOCKER_BUILDKIT=0`, using the Colima Workcell Docker host, and setting `TMPDIR` to a path under `/Users/robertdevore/2026/Kujolang/kujo-repos/.workcell-host-tmp` so the disposable worktree mount was visible inside the Colima VM.

Resume command:

```bash
export DOCKER_HOST=unix:///Users/robertdevore/.colima/kujo-workcell/docker.sock
export DOCKER_CONFIG=/tmp/kujo-next-batch-docker-config
export TMPDIR=/Users/robertdevore/2026/Kujolang/kujo-repos/.workcell-host-tmp
workcell run --file docs/workcell-launch-gate.json --repo . --no-pull
workcell verify --run .workcell/runs/<run-id> --json
```

## Forbidden Launch Actions

Hosted runner deployment, live-provider workflows, marketplace publication, public releases, final release tags, live credentials, branch-protection changes, and force-pushes remain out of scope.
