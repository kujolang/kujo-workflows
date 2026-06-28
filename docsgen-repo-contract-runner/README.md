# DocsGen Repo Contract Runner

This workflow lets an agent run Kujo DocsGen against a repo chosen by the user, capture machine-readable output, and leave behind a reviewable documentation contract packet.

It is designed for documentation refreshes, API surface audits, gap discovery, public-only coverage checks, and agent-readable handoffs before docs are committed or published.

## Pillar

- Audience: developers, agent operators, agency teams, and platform teams.
- Kujo value: scan-only DocsGen, deterministic output, JSON contract payloads, gap files, search indexes, optional strict gates, and local artifacts.
- Content angle: "Documentation generation should be reviewable before it becomes public."

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
.runs/<timestamp>/generated-docs/docgen.md
.runs/<timestamp>/generated-docs/docgen.json
.runs/<timestamp>/generated-docs/docgen-gaps.json
.runs/<timestamp>/artifacts/agent-handoff.md
.runs/<timestamp>/logs/docgen-cli.json
```

## Run Against A User Repo

```bash
TARGET_REPO=/path/to/user/repo bash scripts/run-workflow.sh
```

Use strict public API gates when the repo is ready for enforcement:

```bash
TARGET_REPO=/path/to/user/repo DOCGEN_STRICT=1 bash scripts/run-workflow.sh
```

## What It Runs

The script:

1. Uses `TARGET_REPO` or creates a small documented fixture repo.
2. Runs `kujo docgen` with JSON output, AI task emission, local anchor validation, and search indexes.
3. Writes generated docs under the run packet.
4. Captures stdout JSON, stderr, exit status, and command metadata.
5. Writes an agent handoff with review steps and follow-up guidance.

## Why This Matters

Developers get reproducible documentation generation. Agents get a stable JSON and gap-file contract. Agencies and platform teams get a local evidence packet before updating public docs, opening a docs PR, or enforcing strict coverage gates.
