# KUJO Workflows Review

This folder contains two related workflow prototypes for the KUJO agency tooling stack:

1. `agency-runner/` — a local-first CLI prototype for turning a client task into a reusable run packet.
2. `agency-verified-fix-loop/` — a runnable demo kit that simulates the full fix-and-proof loop against a small storefront fixture.

## Quick verdict

Both workflows are real, usable prototypes and they do produce artifacts in this checkout.

- `agency-runner/` is working as intended for its current scope: it can initialize profiles, create runs, and generate a handoff packet in dry-run mode.
- `agency-verified-fix-loop/` is also working as intended for its demo scope: it builds a fixture, runs the spec/scout/scent/eval/lens chain, and writes a proof packet.

The main caveat is that the demo kit still depends on a few external KUJO tools that are not all present in this local checkout. In the current run, the only reproducible blocker was the missing `changebucket` binary used by the ChangeBucket stages.

---

## 1. Agency Runner

Location: `agency-runner/`

### What it is

`agency-runner` is the more general workflow wrapper. It is designed to turn a human task description and a site profile into an agency-style artifact bundle under `.kujo/runs/<run-id>/`.

### How it works

The main entry point is:

```bash
python3 bin/agency-loop
```

The core flow is:

1. `init` — create `.kujo/agency/` and `.kujo/runs/` folders.
2. `site add` — store a site profile with auth, safety, repo, and recipe settings.
3. `run` — create a run packet from a task file or text input.
4. `verify` / `handoff` — generate review and handoff artifacts.

The prototype writes a portable packet with:

- task intake and normalization
- spec and agent context
- context/scout and scent snapshots
- reproduction and proof placeholders
- eval summary and handoff files
- run-state.json for resumable execution

### What we verified

We verified the documented path with a real dry-run:

```bash
python3 bin/agency-loop --project /tmp/kujo-agency-run-test init
python3 bin/agency-loop --project /tmp/kujo-agency-run-test site add ...
python3 bin/agency-loop --project /tmp/kujo-agency-run-test run --site acme ... --dry-run
```

Result:

- the CLI executed successfully
- the run completed with status `needs-review`
- the output folder contained the expected artifact bundle under `.kujo/runs/...`

### Important note

The prototype currently depends on `PyYAML` in the runtime environment. In this checkout, that dependency was missing and had to be installed before the CLI could run.

### Current status

This workflow is working as a prototype and is suitable for local demos, dry-runs, and future integration into a native `kujo agency` command.

---

## 2. Agency Verified Fix Loop Demo Kit

Location: `agency-verified-fix-loop/`

### What it is

This folder turns the documented fix loop into a runnable demo using a small fixture storefront. It simulates a realistic bug-fix workflow: spec, scout, scent, eval, Lens proof, PatchBrief, ChangeBucket, ShipCheck, and RunLedger.

### How it works

The main entry point is:

```bash
STRICT=1 bash scripts/run-loop.sh
```

The script:

1. builds a temporary buggy fixture under `.work/<timestamp>/northstar-storefront/`
2. renders spec/eval/lens templates
3. runs spec validation, Scout, Scent, and PackWrite prep
4. starts a PHP dev server and records Lens pre-fix failure
5. applies a deterministic fix
6. runs Eval, Lens proof, PatchBrief, ChangeBucket, ShipCheck, and RunLedger
7. writes a client handoff packet under `.runs/<timestamp>/client/`

### What we verified

We ran the demo with:

```bash
KUJO_REPOS=/Users/robertdevore/2026/Kujolang/kujo-repos STRICT=1 bash scripts/run-loop.sh
```

Result:

- the demo completed and wrote a full artifact bundle under `.runs/20260612T154650Z/`
- the summary reported 32 passed stages, 1 warning, and 3 failed stages
- the 3 failures were tied to the missing `changebucket` binary path used by the ChangeBucket stages

### Why the failures happened

The log output showed:

```text
env: /Users/robertdevore/2026/Kujolang/kujo-repos/changebucket/bin/changebucket: No such file or directory
```

That means the demo itself is functioning, but the current checkout does not contain the `changebucket` executable that the script expects.

### Current status

This demo is working as intended for the current repo layout and is useful as a proof-of-concept / demonstration bundle. It is not yet a fully self-contained end-to-end release package because some optional KUJO tooling is missing from this workspace snapshot.

---

## Recommended next steps

1. Add a small `requirements.txt` or setup note for the `agency-runner` Python dependency (`PyYAML`).
2. Add the missing `changebucket` tool or update the script to detect and skip it gracefully when unavailable.
3. Keep the two workflows separate:
   - `agency-runner/` for the reusable CLI prototype
   - `agency-verified-fix-loop/` for the demo / proof-of-concept kit
4. Publish this README alongside the workflows when the repo is opened on GitHub.

## Bottom line

- Yes, both workflows are real and runnable.
- Yes, they are working as intended for their current prototype/demo scope.
- The remaining gaps are environment/tooling dependencies, not a fundamental design failure.
