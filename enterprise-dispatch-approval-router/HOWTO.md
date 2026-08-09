# Enterprise Dispatch Approval Router HOWTO

## 1. Verify Prerequisites

Expected local repos:

```text
/path/to/kujo-repos/kujo
/path/to/kujo-repos/dispatch
```

The script defaults to:

```bash
KUJO_REPOS=/path/to/kujo-repos
KUJO_BIN=$KUJO_REPOS/kujo/target/release/kujo
```

Override them when needed:

```bash
KUJO_REPOS=/path/to/kujo-repos KUJO_BIN=/path/to/kujo bash scripts/run-workflow.sh
```

## 2. Run The Workflow

```bash
cd enterprise-dispatch-approval-router
bash scripts/run-workflow.sh
```

Use a custom topic for the run:

```bash
DISPATCH_TOPIC="Review the CRM rollout for migration, auth, and error-budget risk" \
bash scripts/run-workflow.sh
```

## 3. Review Evidence

Open:

```text
.runs/<timestamp>/SUMMARY.md
.runs/<timestamp>/logs/templates.log
.runs/<timestamp>/logs/dispatch-demo.log
.runs/<timestamp>/logs/runs-diagnostics.json
.runs/<timestamp>/logs/inspect.json
```

Then inspect the generated Dispatch packet:

```text
.runs/<timestamp>/dispatch/<run-id>/report.md
.runs/<timestamp>/dispatch/<run-id>/trace.md
.runs/<timestamp>/dispatch/<run-id>/state.json
.runs/<timestamp>/dispatch/<run-id>/report.json
```

## 4. Turn It Into Content

For a short post or sales demo, show three screens:

1. The command that starts a governed workflow.
2. `trace.md`, proving that the run had structured steps.
3. `state.json` or `runs-diagnostics.json`, proving machine-readable audit output.

## 5. Troubleshooting

If Dispatch rejects the output root, keep the script's `DISPATCH_ALLOW_ANY_OUTPUT_ROOT=true` setting. It is scoped to this local demo because `.runs/<timestamp>/` is outside the Dispatch repo.

If Kujo prints type warnings but exits `0` and writes artifacts, treat the artifact output as authoritative for this demo.
