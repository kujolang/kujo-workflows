# Kujo Agency Runner Prototype

Agency Runner is a local-first workflow wrapper for turning a messy client task into a Kujo-style proof packet.

It keeps the human loop small:

1. Kick off the task.
2. Select or provide a site profile.
3. Let the runner prepare the middle of the workflow for `agent fix`.
4. Review the generated handoff, proof artifacts, logs, and run ledger.

The prototype is intentionally self-contained in this folder. It does not modify core Kujo repos.

## Quick Start

```bash
export KUJO_WORKFLOWS=/path/to/kujo-workflows
cd /path/to/client-repo
"$KUJO_WORKFLOWS/agency-runner/bin/agency-loop" init

"$KUJO_WORKFLOWS/agency-runner/bin/agency-loop" site add acme \
  --type wordpress \
  --environment staging \
  --base-url https://staging.acme.example \
  --login-url https://staging.acme.example/wp-login.php \
  --repo-path "$PWD"

"$KUJO_WORKFLOWS/agency-runner/bin/agency-loop" run \
  --site acme \
  --recipe account-settings \
  --file task.md \
  --dry-run
```

Artifacts are written to:

```text
.kujo/runs/<run-id>/
```

Start review with:

```text
.kujo/runs/<run-id>/handoff/HANDOFF.md
.kujo/runs/<run-id>/handoff/client/CLIENT_SUMMARY.md
.kujo/runs/<run-id>/run-state.json
```

## Commands

```bash
agency-loop init
agency-loop site add <name>
agency-loop site list
agency-loop site doctor --site <name>
agency-loop login --site <name> --role <role>
agency-loop task --site <name> --file task.md
agency-loop run --site <name> --recipe account-settings --file task.md
agency-loop continue --run <run-id>
agency-loop verify --run <run-id>
agency-loop handoff --run <run-id>
agency-loop status --run <run-id>
agency-loop open --run <run-id>
agency-loop demo-verified-loop --strict
```

`--dry-run` is useful for validating profile, recipe, artifact, and handoff behavior without needing a live site or saved session.

## Run Folder Contract

```text
.kujo/runs/<run-id>/
  run-state.json
  summary.md
  task/
  spec/
  context/
    scout/
    scent/
  auth/
  reproduce/
  implementation/
    agent-pack/
  eval/
  lens/
    pre-fix/
    proof/
  casefile/
    pre-fix/
  briefs/
  ledger/
  handoff/
    client/
  logs/
  errors/
```

## Current Status

This is a working prototype, not yet a first-class `kujo agency` subcommand.

The delegated context phase resolves sibling Kujo tools from `KUJO_REPOS` or
the repository layout, runs Spec from the target project for safe-write
compatibility, excludes generated `.kujo` output from Scent, applies bounded
tool timeouts, and fails the phase when Scout or Scent cannot run or produce
their expected artifacts.

Implemented:

- Site profile onboarding.
- CMS-style profile schema.
- Recipe schema and default recipes.
- Run folder creation.
- Task intake from file, text, stdin, or URL metadata.
- Spec, context, reproduction, agent-pack, verify, proof, briefs, ledger, and handoff artifact generation.
- Saved-session login command using Playwright from the existing Lens dependency tree.
- Redaction hooks for generated handoff/log content.
- Resumable phase state in `run-state.json`.
- Integration command for the existing Agency Verified Fix Loop demo.
- Non-dry Lens pre-fix reproduction and post-fix proof execution when a live site and required saved session are available.
- Scout and Scent context invocations resolve sibling repositories portably, exclude the run packet from Scent selection, enforce bounded tool timeouts, and fail the context phase when required tools are missing or return non-zero.

Still early:

- Recipe Lens flows are generic starting points; real CMS selectors usually need site-specific refinement.
- `agent fix` currently produces the implementation contract and pack; a future backend should execute edits directly.
- Eval plans are generated, but project-specific command discovery is intentionally conservative.
- JSON Schema validation is documented and schemas are present; the CLI does not yet enforce schemas internally.

## Design Notes

The runner is decentralized and local-first. It uses:

- Local repo files.
- `.kujo/agency/` for profiles and sessions.
- `.kujo/runs/` for portable artifacts.
- Environment variables for credentials.
- Existing Kujo tools when available.

No hosted service, database, dashboard, or cloud artifact storage is required.

The implementation phase is called `agent fix`.
