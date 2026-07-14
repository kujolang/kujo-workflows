# Enterprise Dispatch Approval Router

This workflow shows Kujo as a control layer for enterprise AI work: a structured request goes through a repeatable Dispatch template, approval behavior is captured, and the run leaves behind state, trace, report, and catalog artifacts.

It is designed for enterprise buyers and engineering leaders who need more than a chat transcript. The output proves that an AI-assisted workflow can be routed, resumed, inspected, and audited.

## Pillar

- Audience: enterprise engineering, platform, compliance, and operations teams.
- Kujo value: reliable orchestration, persisted state, traceability, policy profiles, and human approval points.
- Content angle: "AI workflows need receipts, not just responses."

## Quick Start

From this directory:

```bash
bash scripts/run-workflow.sh
```

Artifacts are written to:

```text
.runs/<timestamp>/
```

Start with:

```text
.runs/<timestamp>/SUMMARY.md
.runs/<timestamp>/dispatch/<run-id>/report.md
.runs/<timestamp>/dispatch/<run-id>/trace.md
.runs/<timestamp>/dispatch/<run-id>/state.json
```

## What It Runs

The script:

1. Uses the local Kujo runtime.
2. Runs `dispatch.kujo templates --json` to prove the template catalog is available.
3. Runs a local offline Dispatch demo with the `crud-reliability` workflow.
4. Captures the generated run directory.
5. Runs `dispatch.kujo runs --json --diagnostics` and `inspect <run-id> --json`.
6. Writes a short executive summary for content and review.

The default path uses `DISPATCH_OFFLINE_FIXTURE=true`; no provider key or network service is required.

## Leash ChatOps contract path

The approval checkpoint now emits the versioned `human_intervention_required`
event used by Leash. Dispatch persists `state.json` before delivery, then
returns with no further model work while the run is paused. Configure a Leash
ingress URL with the additive `--leash-url` flag:

```bash
kujo run dispatch.kujo demo "Release readiness review" \
  --non-interactive --output-root .runs/chatops \
  --leash-url http://127.0.0.1:9191/v1/intervention-events
```

Leash redacts and routes the same event to Slack and Discord, verifies an
authorized provider action, atomically claims the decision, and submits the
normalized decision to the configured Dispatch callback. The local deterministic
resume proof remains:

```bash
RID=$(kujo run dispatch.kujo runs --output-root .runs/chatops --status paused --json \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["runs"][0]["run_id"])')
kujo run dispatch.kujo resume "$RID" --yes --non-interactive --output-root .runs/chatops
```

See [`dispatch/docs/chatops-integration.md`](../../dispatch/docs/chatops-integration.md)
and the Leash checkout's `docs/chatops.md` for the contracts, provider setup,
failure model, and real-workspace limitations.

For bidirectional conversations and backend routing, use the Leash gateway
contracts documented in `ruff-leash/docs/gateway.md`. The local fixture path
supports durable conversations, primary-agent discovery, structured control
classification, subscriptions, proactive events, and a restart-safe Dispatch
resume outbox without requiring live provider credentials.

## Why This Matters

Developers get a repeatable local workflow instead of a one-off prompt. Agency owners can show clients a clean run packet. Enterprise teams get the evidence they need for approval workflows, policy review, and audit trails.
