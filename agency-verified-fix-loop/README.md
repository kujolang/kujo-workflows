# Agency Verified Fix Loop Demo Kit

This folder turns the Agency Verified Fix Loop HOWTO into a runnable local demo.

It includes a small PHP/JS/CSS storefront fixture with a real browser-visible bug:

- On mobile, the promo-code drawer opens.
- The first tap on `Apply` does not apply the code.
- The mobile sticky checkout bar can crowd the drawer.

The automation resets the fixture to the buggy state, proves the Lens flow fails, applies a deterministic fix, then chains several Kujo tools to produce verification and handoff artifacts.

## Quick Start

From this directory:

```bash
bash scripts/run-loop.sh
```

Artifacts are written to:

```text
.runs/<timestamp>/
```

The resettable working copy is written to:

```text
.work/<timestamp>/northstar-storefront/
```

## What The Script Runs

The script attempts these stages:

- Preflight local tools.
- Reset a PHP/JS/CSS storefront fixture.
- Initialize git for diff-aware tools.
- Render templates for the selected local port.
- Validate and render a Spec task contract.
- Export agent context and an Eval suite from Spec.
- Run Scout against the fixture repo.
- Run Scent to build task-specific context.
- Prepare a static agent execution pack.
- Start a RunLedger record.
- Start the PHP dev server.
- Run the Lens flow before the fix and expect failure.
- Capture that expected failure with CaseFile.
- Apply the deterministic fix.
- Run Eval.
- Run Lens check, inspect, and proof recording.
- Run PatchBrief.
- Run ChangeBucket.
- Run ShipCheck.
- Finish RunLedger.
- Assemble a client handoff packet.

## Useful Options

```bash
PORT=8099 bash scripts/run-loop.sh
```

Use a different local server port.

```bash
KEEP_WORK=1 bash scripts/run-loop.sh
```

Keep older `.work/` directories instead of deleting the current run workspace first.

```bash
STRICT=1 bash scripts/run-loop.sh
```

Exit non-zero if any non-expected stage fails.

```bash
RUN_PACKWRITE=1 PACKWRITE_API_KEY=... bash scripts/run-loop.sh
```

Reserved for trying a live PackWrite generation path. The default demo uses a static agent pack so the loop can run without model credentials.

## Reading Results

Start with:

```text
.runs/<timestamp>/summary.md
```

Then inspect:

```text
.runs/<timestamp>/client/CLIENT_HANDOFF.md
.runs/<timestamp>/lens/proof/walkthrough.html
.runs/<timestamp>/briefs/patchbrief.md
.runs/<timestamp>/briefs/changebucket.md
.runs/<timestamp>/briefs/runledger-report.md
```

## Intentional Honesty

This kit does not pretend the whole ecosystem is already one polished product command.

It shows which pieces can be chained today, which produce useful artifacts, and which seams should become first-class in a future `kujo agency-loop` wrapper.
