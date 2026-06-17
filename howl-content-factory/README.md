# Howl Content Factory

This workflow shows Kujo Howl turning real example files into deterministic content assets: Markdown, HTML, SVG cards, captions, and a static gallery.

It is designed for developers and agency owners who need content pillars that stay tied to working examples instead of hand-made slides that drift.

## Pillar

- Audience: developers, developer advocates, agency owners, product marketing.
- Kujo value: deterministic showcase generation from real examples and manifest metadata.
- Content angle: "Turn working Kujo examples into launch-ready assets."

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
.runs/<timestamp>/showcase/dist/howl/index.html
.runs/<timestamp>/logs/list.txt
.runs/<timestamp>/logs/caption-agent-handoff.txt
```

## What It Runs

The script:

1. Creates a mini showcase project with real `.kujo` examples.
2. Validates the Howl manifest.
3. Lists cards and renders deterministic Markdown, HTML, SVG, and gallery artifacts.
4. Generates a platform-safe caption for one card.
5. Verifies the generated content files exist.

## Why This Matters

Developers can publish examples without design-tool overhead. Agency owners can build repeatable content packages. Enterprise teams can review generated assets because the manifest and example source stay in the run packet.

