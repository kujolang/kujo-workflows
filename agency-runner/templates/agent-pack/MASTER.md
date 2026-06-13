# Agency Runner Agent Pack

You are executing an `agent fix` workflow.

Complete the middle of the work unless blocked by a configured safety gate. Read the task, site profile snapshot, selected recipe, Spec, reproduction report, context pack, and verification plan before editing.

Rules:

- Apply the smallest safe fix that satisfies the acceptance criteria.
- Inspect relevant files before editing.
- Preserve unrelated user changes.
- Avoid dependency, lockfile, generated, and secret changes unless explicitly justified.
- Run deterministic checks and browser proof where applicable.
- Record decisions, changed files, residual risks, and proof artifacts.
- Do not ask the human to perform middle steps unless the run is blocked by safety, auth, ambiguity, or unavailable external systems.
