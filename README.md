# Kujo Workflows

Kujo Workflows is a collection of runnable, local-first workflow kits for the Kujo agency and AI tooling ecosystem. Each kit demonstrates one concrete outcome and leaves behind inspectable evidence instead of relying on an opaque hosted runner.

Current release scope: **locally verified support/distribution technical preview** (`0.1.0`). Hosted runners, live-provider coverage, clean-machine installation on a separate host, and production or enterprise readiness are not claimed.

## Start Here

The portable Loop Engineering demo needs Bash and the files in this repository:

```bash
git clone https://github.com/kujolang/kujo-workflows.git
cd kujo-workflows
(cd loop-engineering && bash scripts/run-workflow.sh --demo)
```

Review `loop-engineering/.runs/<timestamp>/SUMMARY.md` after the command finishes.

Most ecosystem demos also require a built Kujo runtime and sibling tool repositories. Keep them under one parent directory and set `KUJO_REPOS`:

```text
/path/to/kujo-repos/
  kujo/
  kujo-skills/
  kujo-workflows/
  casefile/
  dispatch/
  howl/
  mcp/
  rag/
  ...
```

```bash
export KUJO_REPOS=/path/to/kujo-repos
export KUJO_BIN="$KUJO_REPOS/kujo/target/release/kujo"
cd "$KUJO_REPOS/kujo-workflows"
(cd casefile-incident-evidence-packet && bash scripts/run-workflow.sh)
```

Workflow READMEs list any additional runtime, browser, Docker, local-service, or provider requirements. Fixture modes are the default where available; live-provider commands are explicitly opt-in and may incur cost.

## Workflow Catalog

Readiness values come from [`docs/audit/workflow-catalog.json`](docs/audit/workflow-catalog.json):

- **Ready**: production-ready within the documented local contract.
- **Limited**: production-capable with named fixture, provider, host, or approval limitations.
- **Experimental**: useful prototype whose primary path remains under-tested.

All commands below run from the repository root.

| Workflow | Readiness | Audience | What it proves | Run command |
| --- | --- | --- | --- | --- |
| [`agency-runner/`](agency-runner/) | Experimental | Agency owners | Client tasks can become reusable local run packets. | `agency-runner/bin/agency-loop --help` |
| [`agency-verified-fix-loop/`](agency-verified-fix-loop/) | Limited | Agencies, developers | A bug fix can move through spec, context, proof, briefs, and handoff artifacts. | `(cd agency-verified-fix-loop && STRICT=1 bash scripts/run-loop.sh)` |
| [`feature-card-workflow/`](feature-card-workflow/) | Limited | Developers | A task card can drive implementation, verification, proof, and reviewer handoff. | `feature-card-workflow/muzzle-template/workflows/feature-card-full.sh --help` |
| [`ai-sdk-watchdog-showcase/`](ai-sdk-watchdog-showcase/) | Limited | AI app developers | AI SDK calls can be routed through Watchdog and exported as telemetry. | `(cd ai-sdk-watchdog-showcase && bash scripts/run-showcase.sh)` |
| [`ai-sdk-muzzle-benchmark/`](ai-sdk-muzzle-benchmark/) | Limited | AI app teams | Repeated AI SDK app generations can be benchmarked and reviewed. | `(cd ai-sdk-muzzle-benchmark && bash scripts/run-benchmark.sh)` |
| [`enterprise-dispatch-approval-router/`](enterprise-dispatch-approval-router/) | Limited | Enterprise platform teams | Dispatch creates auditable workflow state, trace, report, and diagnostics. | `(cd enterprise-dispatch-approval-router && bash scripts/run-workflow.sh)` |
| [`mcp-agent-gateway-review/`](mcp-agent-gateway-review/) | Limited | Developers, enterprise AI teams | `mcp make` generates a guarded MCP server scaffold and safety packet. | `(cd mcp-agent-gateway-review && bash scripts/run-workflow.sh)` |
| [`rag-enterprise-knowledge-gate/`](rag-enterprise-knowledge-gate/) | Limited | Enterprise knowledge teams | RAG ingests local docs, isolates a namespace, and answers with citations. | `(cd rag-enterprise-knowledge-gate && bash scripts/run-workflow.sh)` |
| [`casefile-incident-evidence-packet/`](casefile-incident-evidence-packet/) | Limited | Developers, support teams | CaseFile captures a failing command as a reproducible evidence bundle. | `(cd casefile-incident-evidence-packet && bash scripts/run-workflow.sh)` |
| [`howl-content-factory/`](howl-content-factory/) | Limited | Developers, agency owners | Howl turns real Kujo examples into Markdown, HTML, SVG, galleries, and captions. | `(cd howl-content-factory && bash scripts/run-workflow.sh)` |
| [`loop-engineering/`](loop-engineering/) | Ready | Agent builders | A bounded Goal → Context → Agent → Evaluation → Stop loop runs portably and stops safely. | `(cd loop-engineering && bash scripts/run-workflow.sh --demo)` |
| [`docsgen-repo-contract-runner/`](docsgen-repo-contract-runner/) | Limited | Developers, agent operators | DocsGen scans a chosen repo and writes an auditable documentation contract packet. | `(cd docsgen-repo-contract-runner && TARGET_REPO=/path/to/repo bash scripts/run-workflow.sh)` |
| [`tribunal-decision-gate/`](tribunal-decision-gate/) | Limited | Governance, release, security teams | Tribunal mock review becomes a verified advisory decision receipt. | `bash tribunal-decision-gate/scripts/run.sh` |
| [`relay-lifecycle-handoff/`](relay-lifecycle-handoff/) | Limited | Workflow operators | Relay pause/resume and integrity-checked export become correlated handoff receipts. | `bash relay-lifecycle-handoff/scripts/run.sh` |
| [`workcell-execution-gate/`](workcell-execution-gate/) | Limited | Agent operators | Workcell validates, inspects, and executes a bounded Docker package with completion evidence. | `bash workcell-execution-gate/scripts/run.sh` |

## Verification

Self-contained checks:

```bash
python3 -m pip install jsonschema PyYAML
make validate
make format
```

Catalog validation additionally resolves canonical skills and sibling tool repositories:

```bash
python3 scripts/validate_catalog.py \
  --skills-root "$KUJO_REPOS/kujo-skills" \
  --tools-root "$KUJO_REPOS" \
  --json
```

Host-dependent representative gates:

```bash
bash workcell-execution-gate/scripts/run.sh
bash tribunal-decision-gate/scripts/run.sh
bash relay-lifecycle-handoff/scripts/run.sh
```

Generated `.runs/`, `.workcell/`, and tool-specific state directories are local evidence. They are ignored unless a deliberately reviewed proof artifact is promoted into a tracked documentation location.

See the current [launch checklist](docs/launch-checklist.md) and [release-readiness Spec](specs/showcase-release-readiness.spec.yml) for the exact boundary and acceptance contract.

## Documentation

- [`contracts/README.md`](contracts/README.md) — versioned evidence contracts and compatibility rules.
- [`docs/audit/README.md`](docs/audit/README.md) — catalog, compatibility, and weekly drift evidence.
- [`docs/launch-checklist.md`](docs/launch-checklist.md) — verified launch gates and remaining external proof.
- [`docs/specs/showcase-release-readiness.md`](docs/specs/showcase-release-readiness.md) — rendered implementation contract for this release cleanup.

## Known Limits

- Some Kujo interpreter runs emit type-checking warnings before successful artifact output; workflow scripts use exit status plus expected artifacts as the contract.
- Live providers, authenticated browser flows, external customer repositories, and hosted execution require separate credentials and approval.
- Tribunal mock decisions are advisory and unsigned.
- Relay proves local persistence and bounded retries, not remote exactly-once delivery.
- Workcell is a trusted local Docker/Podman boundary, not a hosted scheduler or microVM isolation layer.
- The clean-worktree gate has passed on the development host; clean-machine installation on a separate host remains open.

## License

Kujo Workflows is available under the [MIT License](LICENSE). Changes are recorded in [CHANGELOG.md](CHANGELOG.md).
