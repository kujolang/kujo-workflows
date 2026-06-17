# MCP Agent Gateway Review

This workflow shows how Kujo can turn an existing codebase into a guarded, reviewable MCP server scaffold for agents.

It is aimed at developers and enterprise platform teams who want agents to inspect project context through constrained tools instead of broad filesystem access.

## Pillar

- Audience: developers, platform engineers, enterprise AI enablement teams.
- Kujo value: generated MCP surface, safety review, read-only defaults, explicit blocked commands, and artifact-backed handoff.
- Content angle: "Give agents tools, but make the tools reviewable."

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
.runs/<timestamp>/artifacts/safety-review.md
.runs/<timestamp>/generated-server/mcp.manifest.json
.runs/<timestamp>/generated-server/repo-profile.json
```

## What It Runs

The script:

1. Creates a tiny CRM service fixture repo.
2. Runs `mcp make` with `--no-ai --validate`.
3. Writes a generated MCP server scaffold.
4. Writes safety, surface, validation, handoff, PatchBrief, and ShipCheck artifacts.
5. Verifies the key generated files exist.

## Why This Matters

Developers get a fast local way to expose repo context safely. Agencies can hand a client a readable safety review. Enterprise teams can review capabilities before connecting agents to internal code.

