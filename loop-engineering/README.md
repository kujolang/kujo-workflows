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
| [`loop.spec.yml`](loop.spec.yml) | Canonical machine-readable loop contract: goal, context sources, eval gates, stop conditions, approval gates, and adapters. |
| [`HOWTO.md`](HOWTO.md) | How to adopt and run the loop in your own system. |
| [`scripts/init-repo-loop.sh`](scripts/init-repo-loop.sh) | Repo-local initializer that creates `.loop-engineering/` state, config, ledger, evidence, blockers, and summary files. |
| [`scripts/run-workflow.sh`](scripts/run-workflow.sh) | A portable loop driver with explicit demo, config, and Markdown checklist modes. |

## Quick Start

Initialize any target repo:

```bash
/path/to/loop-engineering/scripts/init-repo-loop.sh
```

Then edit `.loop-engineering/loop.yml` and run the configured gates:

```bash
/path/to/loop-engineering/scripts/run-workflow.sh --config .loop-engineering/loop.yml
```

Checklist mode classifies Markdown tasks before any local work:

```bash
/path/to/loop-engineering/scripts/run-workflow.sh --checklist docs/checklist.md
```

Artifacts are written to `.loop-engineering/SUMMARY.md`, `ledger.tsv`, `blockers.md`, and `iterations/001/`. The old placeholder loop is still available, but only by request:

```bash
bash scripts/run-workflow.sh --demo
```

## Why This Matters

A loop that never stops, silently expands scope, or ships without evaluation is a liability. Loop Engineering makes the boundaries first-class: the goal is a contract, context is fetched on demand instead of dumped, every iteration is evaluated before it continues, risky actions pause for a human, and the whole run leaves a ledger of decisions and evidence.
