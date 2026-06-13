# Artifacts

Every task run writes a portable bundle:

```text
.kujo/runs/<run-id>/
  task/raw.md
  task/normalized.md
  task/questions.md
  task/assumptions.md
  spec/task.spec.yml
  spec/task.spec.md
  spec/agent-context.md
  context/site-profile.snapshot.yml
  context/recipe.snapshot.yml
  reproduce/report.md
  reproduce/result.json
  implementation/agent-pack/
  eval/summary.json
  lens/proof/walkthrough.html
  briefs/patchbrief.md
  briefs/changebucket.md
  briefs/shipcheck.md
  ledger/run.json
  ledger/report.md
  handoff/HANDOFF.md
  handoff/client/
```

`run-state.json` is the resumable state machine. Phases can be rerun:

```bash
agency-loop run --run <run-id> --phase reproduce
agency-loop verify --run <run-id>
agency-loop handoff --run <run-id>
```
