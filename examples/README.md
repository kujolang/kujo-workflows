# Workflow Examples

The workflow directories at the repository root are the executable examples. This index provides low-risk starting points.

## Repository-owned Agent Project

Scaffolds, installs, diagnoses, inspects, runs, and evaluates a deterministic
Agent Project while retaining the JSON evidence from every stage:

```bash
export KUJO_BIN=/absolute/path/to/kujo
(cd owned-agent-project && bash scripts/run.sh)
```

See [`owned-agent-project/README.md`](../owned-agent-project/README.md) for the
dependency and boundary contract.

## Portable Agent Loop

Runs with Bash and no sibling Kujo tools:

```bash
(cd loop-engineering && bash scripts/run-workflow.sh --demo)
```

See [`loop-engineering/README.md`](../loop-engineering/README.md) for real configuration and checklist modes.

## Local Failure Evidence

Requires the Kujo runtime and sibling CaseFile checkout:

```bash
export KUJO_REPOS=/path/to/kujo-repos
export KUJO_BIN="$KUJO_REPOS/kujo/target/release/kujo"
(cd casefile-incident-evidence-packet && bash scripts/run-workflow.sh)
```

See [`casefile-incident-evidence-packet/README.md`](../casefile-incident-evidence-packet/README.md) for the generated evidence contract.
