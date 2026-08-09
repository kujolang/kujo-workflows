# MCP Agent Gateway Review HOWTO

## 1. Run The Demo

```bash
cd mcp-agent-gateway-review
bash scripts/run-workflow.sh
```

Override local paths if needed:

```bash
KUJO_REPOS=/path/to/kujo-repos KUJO_BIN=/path/to/kujo bash scripts/run-workflow.sh
```

## 2. Review The Generated Server

Start here:

```text
.runs/<timestamp>/SUMMARY.md
.runs/<timestamp>/generated-server/README.md
.runs/<timestamp>/generated-server/mcp.manifest.json
.runs/<timestamp>/generated-server/repo-profile.json
```

Then review the safety packet:

```text
.runs/<timestamp>/artifacts/safety-review.md
.runs/<timestamp>/artifacts/mcp-surface-plan.md
.runs/<timestamp>/artifacts/validation-report.md
.runs/<timestamp>/artifacts/agent-handoff.md
```

## 3. Use A Real Repo

Run the underlying command against any local repo:

```bash
export KUJO_REPOS=/path/to/kujo-repos
export KUJO_BIN="$KUJO_REPOS/kujo/target/release/kujo"
cd "$KUJO_REPOS/mcp"
"$KUJO_BIN" run mcp.kujo --interpreter make /path/to/repo --no-ai --validate
```

For a custom output location:

```bash
"$KUJO_BIN" run mcp.kujo --interpreter make /path/to/repo \
  --out /tmp/generated-server \
  --artifacts /tmp/mcp-artifacts \
  --no-ai \
  --validate
```

## 4. Content Notes

The strongest demo moment is opening `safety-review.md` beside `mcp.manifest.json`. That shows Kujo's position clearly: agent surfaces should be generated with guardrails and reviewed before use.

## 5. Troubleshooting

The MCP command may print Kujo type warnings before the success text. For this workflow, use the command exit code and generated files as the verification source.
