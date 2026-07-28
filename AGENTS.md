# Kujo Workflows Agent Instructions

This repository collects runnable local workflow kits. Treat it as a support/distribution repository for proof workflows, not a hosted workflow runner.

## Required Reading

- `README.md`
- `contracts/README.md`
- `docs/audit/README.md`
- `docs/launch-checklist.md`
- Relevant workflow `README.md`, `HOWTO.md`, and scripts before editing that workflow.

## Validation

```bash
python3 scripts/validate_catalog.py --json
python3 scripts/validate_contracts.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash workcell-execution-gate/scripts/run.sh
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
git diff --check
```

## Evidence Rules

- Preserve generated `.runs/<timestamp>/SUMMARY.md` packets only when they are intentional proof artifacts.
- Keep workflow commands local, deterministic, and explicit about external blockers.
- Workcell proof is required for this launch batch unless a blocker receipt documents the Docker/host blocker and closest equivalent proof.

## Prohibited Without Approval

Do not deploy hosted runners, call live external providers, publish packages, create public releases, push final tags, alter branch protection, force-push, rewrite history, or discard user changes.
