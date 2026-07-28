# Launch Checklist

Current launch scope: `locally verified support/distribution technical preview`. Workflow catalog, contracts, representative workflows, and unit validation pass locally. Hosted runner behavior, live external-provider workflows, clean-machine install/use, and Workcell proof are not complete.

## Local Gates

- [x] Catalog checked with `python3 scripts/validate_catalog.py --json`.
- [x] Contracts checked with `python3 scripts/validate_contracts.py`.
- [x] Workcell contract examples checked with `python3 scripts/validate_contract_instance.py`.
- [x] Unit validation checked with `python3 -m unittest discover -s tests -p 'test_*.py'`.
- [x] Representative Workcell workflow checked with `bash workcell-execution-gate/scripts/run.sh`.
- [x] Representative Tribunal workflow checked with `bash tribunal-decision-gate/scripts/run.sh`.
- [x] Representative Relay workflow checked with `bash relay-lifecycle-handoff/scripts/run.sh`.
- [x] Formatting checked with `git diff --check`.
- [ ] Workcell proof checked with `workcell run --file docs/workcell-launch-gate.json --repo .`.
- [ ] Clean-checkout workflow validation on a separate machine.

## Current External Blocker

Workcell proof is blocked by the local Docker image build/pull path. The Workcell base image could not be fetched from Docker Hub because `auth.docker.io` timed out.

Closest equivalent proof: local catalog, schema/contract, unit, and representative workflow checks.

Safe resume command:

```bash
cd /Users/robertdevore/2026/Kujolang/kujo-repos/workcell
DOCKER_HOST=unix:///Users/robertdevore/.colima/kujo-workcell/docker.sock docker build --tag kujolang/workcell-base:local docker/
cd /Users/robertdevore/2026/Kujolang/kujo-repos/kujo-workflows
workcell run --file docs/workcell-launch-gate.json --repo .
```

## Forbidden Launch Actions

Hosted runner deployment, live-provider workflows, marketplace publication, public releases, final release tags, live credentials, branch-protection changes, and force-pushes remain out of scope.
