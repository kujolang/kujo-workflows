# Loop Engineering

This workflow is a portable, system-agnostic implementation of the **agent loop** pattern (Goal → Context → Agent → Evaluation → Stop). It lets an AI agent or agent system repeatedly work toward a scoped objective, refresh context as it goes, evaluate its own progress, delegate subtasks when useful, and **stop safely** when it succeeds, stalls, or exceeds scope.

Unlike the other kits in this repo, Loop Engineering is not a single concrete demo bound to one fixture. It is a reusable control pattern that maps the four loop pieces onto real Kujo tooling while staying decentralized: it does not depend on Paperclip, a single Git host, one model provider, one CI provider, or one repo layout.

## Pillar

- Audience: developers, agency owners, enterprise platform teams, and anyone wiring autonomous or semi-autonomous agents.
- Kujo value: bounded loops, fetchable/refreshable context, mandatory evaluation gates, explicit human approval points, and a decision ledger — turning "let the agent run" into reviewable, repeatable work.
- Content angle: "An agent loop is only safe when the goal, context, evaluation, and stop conditions are explicit."

## The Loop

```
        ┌──────────────────────────────────────────────┐
        │ 1. GOAL      objective, success criteria,      │
        │              constraints, allowed actions,     │
        │              approval gates, stop conditions   │
        └──────────────────────┬───────────────────────┘
                               ▼
        ┌──────────────────────────────────────────────┐
   ┌──▶ │ 2. CONTEXT   fetch/refresh only what's needed  │
   │    └──────────────────────┬───────────────────────┘
   │                           ▼
   │    ┌──────────────────────────────────────────────┐
   │    │ 3. AGENT     choose next action, make scoped   │
   │    │              progress, delegate, record        │
   │    └──────────────────────┬───────────────────────┘
   │                           ▼
   │    ┌──────────────────────────────────────────────┐
   │    │ 4. EVALUATE  tests, CI, lint/type, visual QA,  │
   │    │              blast radius → pass/fail/stall    │
   │    └──────────────────────┬───────────────────────┘
   │                           ▼
   │    ┌──────────────────────────────────────────────┐
   └─no─│ 5. STOP?     success / repeated failure /      │
        │              scope creep / approval / budget   │
        └──────────────────────┬───────────────────────┘
                               ▼ yes
                             DONE
```

## Files

| File | Purpose |
| --- | --- |
| [`WORKFLOW.md`](WORKFLOW.md) | The full portable workflow definition (the canonical, agent-readable spec). |
| [`loop.spec.yml`](loop.spec.yml) | Machine-readable loop contract: goal, context sources, eval gates, stop conditions, approval gates, adapters. |
| [`HOWTO.md`](HOWTO.md) | How to adopt and run the loop in your own system. |
| [`scripts/run-workflow.sh`](scripts/run-workflow.sh) | A portable reference loop driver that runs the bounded control flow and emits a reviewable run packet. |
| [`TODO.md`](TODO.md) | Status and future seams. |

## Quick Start

From this directory:

```bash
bash scripts/run-workflow.sh
```

The reference driver runs with safe, no-op default adapters so it executes anywhere `bash` is available — no Kujo runtime, model key, or network required. Artifacts are written to:

```text
.runs/<timestamp>/SUMMARY.md
.runs/<timestamp>/ledger.tsv
.runs/<timestamp>/iterations/
```

To wire it to real Kujo tooling, point the adapter environment variables at your local tools (see [`HOWTO.md`](HOWTO.md)). To embed the loop in another agent system, treat [`loop.spec.yml`](loop.spec.yml) and [`WORKFLOW.md`](WORKFLOW.md) as the contract and implement the five adapter hooks however your runtime prefers.

## Why This Matters

A loop that never stops, silently expands scope, or ships without evaluation is a liability. Loop Engineering makes the boundaries first-class: the goal is a contract, context is fetched on demand instead of dumped, every iteration is evaluated before it continues, risky actions pause for a human, and the whole run leaves a ledger of decisions and evidence.
