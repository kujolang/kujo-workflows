# Contributing

Contributions should keep each workflow local-first, deterministic where possible, explicit about external dependencies, and honest about the evidence it produces.

## Workflow

1. Create a focused branch.
2. Read the workflow's `README.md`, `HOWTO.md` when present, and scripts before editing it.
3. Update `docs/audit/workflow-catalog.json` when a workflow's entry point, tools, skills, readiness, inputs, outputs, approval boundaries, tests, or documentation changes.
4. Add or update deterministic fixtures and failure-path coverage.
5. Run the portable release gates and the affected workflow's own gate.
6. Open a pull request describing the supported boundary, validation evidence, and any external proof that remains pending.

```bash
python3 -m pip install jsonschema PyYAML
bash tests/release-readiness.sh
bash tests/clean-checkout.sh
```

Do not commit generated `.runs/`, `.workcell/`, provider state, credentials, or disposable agent artifacts. Do not add live-provider execution to default tests, broaden security guarantees beyond the underlying tools, or describe fixture evidence as production certification.
