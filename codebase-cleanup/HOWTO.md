# Codebase Cleanup HOWTO

## 1. Establish Repository-Owned Verification

Pass the target's real build, test, lint, contract, and architecture commands as
repeatable `--verify-cmd` flags. The workflow intentionally does not guess and
execute package scripts because arbitrary repositories own different safety and
credential boundaries.

```bash
bash /path/to/kujo-workflows/codebase-cleanup/scripts/run-workflow.sh \
  --repo "$PWD" \
  --verify-cmd "make lint" \
  --verify-cmd "make test" \
  --output .cleanup-runs/review-1
```

An existing failure is allowed as a baseline fact. Read its captured output and
decide whether cleanup can still be proven. A newly failing command is a
regression and blocks the batch.

## 2. Review The Analysis Packet

Review every `PROVEN` candidate as well as `Preserved Complexity`. Confirm entry
points, exports, reflection, plugins, configuration-driven loading, generated
code, external APIs, serialization, FFI, macros, and framework conventions.
Do not promote `LIKELY` or `UNKNOWN` findings simply to increase deletion count.

For dependency candidates, verify lockfiles, binaries used by scripts, loaders,
plugins, peers, build hooks, and external packaging before removing them with the
repository's package manager. The v1 workflow does not auto-promote dependency
text absence to proof.

## 3. Approve A Small Batch

Copy only reviewed IDs into the generated plan:

```json
{
  "schema": "kujo.codebase-cleanup/v1",
  "repository_fingerprint": "...",
  "approved_finding_ids": ["CC-DEAD_CODE-..."],
  "candidates": []
}
```

Keep the generated `candidates`; they contain exact operation hashes used to
detect analysis/apply drift. A changed repository fingerprint forces a new
analysis rather than applying a stale decision.

## 4. Apply And Verify

```bash
bash /path/to/kujo-workflows/codebase-cleanup/scripts/run-workflow.sh \
  --repo "$PWD" \
  --verify-cmd "make test" \
  --apply-plan .cleanup-runs/review-1/cleanup-plan.json \
  --output .cleanup-runs/apply-1
```

Inspect the diff, ChangeBucket evidence, PatchBrief, and final test output. Commit
one logical cleanup batch at a time. Run a fresh analysis before the next batch.

## 5. Optional Ecosystem Evidence

Set `KUJO_REPOS` and `KUJO_BIN` as documented in the repository root, then add
`--run-integrations`. Only read-only, applicable checks run. Logs remain under
the selected output directory. Fence is skipped without `fence.toml`; Kennel is
skipped without a compatible manifest; Casefile and RunLedger require their
own triggering context and are reported as adapters rather than invoked blindly.

## Report Contract

`report.json` uses `kujo.codebase-cleanup/v1`. Findings have stable content-based
IDs and include category, confidence, location, evidence, risk, behavior/API/test
impact, recommended action, and an optional guarded operation. Arrays and
findings are sorted for automation. Durations and command output hashes are run
evidence and are expected to vary; finding IDs and classification are stable for
unchanged inputs.

## Limitations

- The workflow implementation and test suite are Kujo-native. Python source is
  the first language syntax supported for guarded deletion and exact-duplication
  application; this does not invoke Python to perform analysis.
- JavaScript package dependency detection is conservative repository text search,
  not a package-manager graph proof.
- Generic unreachable branches, semantic near-duplication, public API counts,
  transitive dependency pressure, feature flags, and circular dependencies need
  stronger language/build-system primitives before automatic action.
- Applying one approved batch at a time is required; this is deliberately not an
  autonomous rewrite engine.
- Verification commands run through Bash in the target repository and therefore
  must be reviewed like any other repository-owned command.
