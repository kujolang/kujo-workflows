# CaseFile Incident Evidence Packet

This workflow shows Kujo CaseFile turning a local failure into a structured evidence bundle for debugging, review, and handoff.

It is designed for developers, agencies, and enterprise support teams that need crisp failure packets instead of scattered logs and chat notes.

## Pillar

- Audience: developers, support engineers, agency retainers, enterprise incident response.
- Kujo value: deterministic failure capture, reproduction notes, redaction, git context, and handoff artifacts.
- Content angle: "Every failed run should become a useful case packet."

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
.runs/<timestamp>/fixture/.casefile/<case-id>/case.md
.runs/<timestamp>/fixture/.casefile/<case-id>/handoff.md
.runs/<timestamp>/logs/show-latest.md
```

## What It Runs

The script:

1. Creates a tiny fixture repo.
2. Initializes CaseFile.
3. Captures a deterministic failing command.
4. Renders the latest case as Markdown and JSON.
5. Verifies the key case artifacts exist.

## Why This Matters

Developers get a reproducible failure packet. Agencies can hand clients evidence without rewriting notes. Enterprise teams get consistent incident artifacts with command, logs, environment, and git context.

