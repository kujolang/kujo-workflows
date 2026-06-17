# RAG Enterprise Knowledge Gate

This workflow shows Kujo RAG as a local-first enterprise knowledge gate: ingest a controlled corpus, query it with citations, and keep the index inside a reviewable run packet.

It is designed for teams that need grounded answers over internal docs without sending the demo corpus to an external service.

## Pillar

- Audience: enterprise knowledge, support, platform, and security teams.
- Kujo value: offline hash embeddings, namespace isolation, local JSON indexes, citations, and configurable guardrails.
- Content angle: "Enterprise AI answers should cite local source material."

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
.runs/<timestamp>/logs/ingest.json
.runs/<timestamp>/logs/query-security.json
.runs/<timestamp>/logs/query-onboarding.json
```

## What It Runs

The script:

1. Creates a small enterprise policy and onboarding corpus.
2. Runs RAG ingest with a demo namespace.
3. Runs two grounded queries.
4. Stores the local index under the run directory.
5. Writes a summary tying the evidence to buyer value.

## Why This Matters

Developers get deterministic local retrieval. Agency owners can demo knowledge assistants without client data leaving the machine. Enterprise teams get namespace isolation, local indexes, and citation-backed answers.

