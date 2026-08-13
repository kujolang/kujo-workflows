# Codebase Cleanup

Codebase Cleanup is Kujo's evidence-first workflow for reducing a repository to
the smallest, clearest implementation that preserves its intended behavior. It
investigates entropy across code, dependencies, configuration, tests,
documentation, and architecture. Analysis is the default. Mutation requires a
reviewer-approved plan containing stable finding IDs, and only `PROVEN`
candidates with supported mechanical operations can be applied automatically.
The analyzer, safety engine, applicator, metrics, reports, companion-tool
orchestration, and tests are implemented in Kujo; the Bash entrypoint only
locates the Kujo runtime.

The workflow rewards removed concepts, not rearranged code. Zero actionable
findings is a valid result.

## Quick Start

Analyze a repository without modifying it:

```bash
bash codebase-cleanup/scripts/run-workflow.sh \
  --repo /path/to/repository \
  --verify-cmd "make test"
```

The command prints the path to `REPORT.md`. By default, evidence is written to
`<repo>/.cleanup-runs/<timestamp>/`:

```text
REPORT.md             human review packet
report.json           deterministic machine-readable evidence
cleanup-plan.json     PROVEN candidates with an empty approval list
integrations/         optional companion-tool logs
```

Analysis-only mode never edits the target. To apply reviewed candidates, copy
their IDs into `approved_finding_ids` in `cleanup-plan.json`, then run:

```bash
bash codebase-cleanup/scripts/run-workflow.sh \
  --repo /path/to/repository \
  --verify-cmd "make test" \
  --verify-cmd "make lint" \
  --apply-plan /path/to/reviewed-cleanup-plan.json
```

If a previously passing verification command fails after cleanup, every change
from that apply run is rolled back. Commands that already failed at baseline are
reported separately and are not mislabeled as cleanup regressions.

## Workflow Architecture

1. **Reconnaissance** inventories scoped source, tests, manifests, documentation,
   languages, metrics, dynamic/export surfaces, and available Kujo companions.
2. **Baseline** runs every explicit `--verify-cmd` before modification and stores
   exit status plus output hashes.
3. **Analysis** investigates all ten cleanup categories with Kujo-native
   structural scanners and conservative repository-wide heuristics.
4. **Classification** records evidence, confidence, behavioral risk, public API
   impact, related tests, documentation impact, and a stable finding ID.
5. **Cleanup** accepts only explicitly approved `PROVEN` operations from a plan
   whose repository fingerprint still matches.
6. **Batch verification** reruns the configured build/test/lint gates and rolls
   the batch back on a new failure.
7. **Full validation** is supplied through repeatable `--verify-cmd` arguments;
   repositories retain ownership of their actual gates.
8. **Drift and architecture checks** are delegated to Concord and Fence when
   available and applicable; the workflow does not invent project boundaries.
9. **Evidence reporting** emits JSON, Markdown, before/after metrics, preserved
   complexity, skipped candidates, and tool dispositions.

## Cleanup Coverage

| Category | Investigation | Automatic mutation |
| --- | --- | --- |
| Dead code | private top-level functions, unreferenced public/dynamic candidates | exact private Python function removal when all guards pass |
| Duplication | normalized exact function bodies, intentional markers | consolidation of exactly duplicated private Python functions with local call redirection |
| Unnecessary abstraction | one-statement forwarding wrappers | review only |
| Over-engineering | speculative extension/future-use markers | review only |
| Legacy and compatibility | deprecation, shim, migration, and fallback markers | never without support-policy evidence |
| Dependencies | direct package entries without repository references | plan operation is emitted, but remains `LIKELY` and therefore cannot auto-apply |
| Configuration | single-use environment/configuration surfaces | review only |
| Tests | stale skip/TODO combinations and test metrics | review only; coverage is never deleted automatically |
| Documentation | references to missing repository paths | review only |
| Architecture | repository-owned Fence model and companion evidence | never based on guessed boundaries |

The Kujo-native analyzer recognizes the initial Python mutation surface because
that syntax can currently be bounded without an external parser. Other languages
still receive inventory, metrics, text evidence, dependency, drift, and
companion-tool coverage, but no deletion is claimed `PROVEN` from generic text
search alone.

## Safety Model

- `PROVEN`: strong, reproducible evidence; may be represented by a guarded
  mechanical operation.
- `LIKELY`: credible cleanup candidate requiring review or more verification.
- `INTENTIONAL`: suspicious-looking complexity with an explicit reason to keep it.
- `UNKNOWN`: insufficient evidence; preserve it.

Static absence of a caller is never enough for public code. Decorators,
`__all__`, string references, project entry points, test discovery, public names,
and repository-wide references lower confidence or suppress deletion. Reviewers
must also account for reflection, dynamic loading, plugins, CLIs, serialization,
generated interfaces, FFI, macros, frameworks, and external consumers.

`cleanup: intentional-duplication` can document a deliberate local duplicate;
include the reason in the same comment. This is evidence, not an escape hatch:
review it when the surrounding contract changes.

## Kujo Integrations

Use `--run-integrations` to execute available and applicable read-only companion
checks. The workflow uses the checked-out `KUJO_REPOS`/`KUJO_BIN` layout already
documented by this repository and records the exact command and result.

- Scout supplies repository inventory and entry-point context.
- Fence supplies reviewed architecture boundaries only when `fence.toml` exists.
- Concord supplies implementation/docs/CLI/manifest drift evidence.
- Kennel validates a repository-owned Kujo package manifest.
- ChangeBucket measures diff footprint and blast radius.
- PatchBrief summarizes diff risk for reviewers.
- ShipCheck adds release-readiness evidence.
- Casefile is reserved for actual failing-command capture; it is not invoked to
  manufacture evidence.
- RunLedger remains a host adapter when a caller owns a RunLedger task.
- Dispatch `cleanup` is deliberately not invoked: that command removes old
  Dispatch run outputs, not repository source entropy. Dispatch may orchestrate
  this workflow externally without duplicating its source-cleanup logic.

Unavailable or inapplicable tools are reported honestly. They are never faked.

## Scope Controls

```bash
# One directory and category
bash codebase-cleanup/scripts/run-workflow.sh --repo . --path src \
  --category dead-code --minimum-confidence LIKELY

# Changed and untracked files only
bash codebase-cleanup/scripts/run-workflow.sh --repo . --changed
```

`--category` may be repeated. Confidence filtering is for report focus; it does
not upgrade or weaken the apply safety threshold.

## Realistic Example

An established service contains two identical private request normalizers, an
unreferenced private migration helper, a package dependency no code mentions,
and an old README command. Its baseline unit and contract tests pass.

Analysis reports the private helper and exact private duplicate as `PROVEN`, the
dependency and README path as `LIKELY`, and preserves a compatibility adapter as
`UNKNOWN` because downstream API support is not known. A maintainer approves
only the two proven IDs. The workflow removes the helper, consolidates the
normalizers, redirects local calls, and reruns the unit and contract suites.
The report shows fewer functions and LOC, unchanged test status, the dependency
and docs candidate still pending, and the compatibility adapter explicitly
preserved. This is successful cleanup: a smaller implementation with behavior
evidence, not a broad rewrite.

## When Not To Use It

Do not use automatic apply for style rewrites, behavior changes, public API
removal, speculative architecture redesign, dependency fashion changes, or
large subsystem replacement. Localized simplification with clear proof is the
boundary. See [`HOWTO.md`](HOWTO.md) for the operational review sequence and
limitations.
