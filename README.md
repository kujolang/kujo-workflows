# Kujo Workflows

[![Version](https://img.shields.io/badge/version-0.5.0-black)](https://github.com/kujolang/kujo-workflows)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![built with Kujo](https://img.shields.io/badge/built%20with-Kujo-white.svg)](https://github.com/kujolang/kujo)
[![CI](https://github.com/kujolang/kujo-workflows/actions/workflows/validate.yml/badge.svg)](https://github.com/kujolang/kujo-workflows/actions/workflows/validate.yml)

Repository-backed, local-first workflow kits for the [Kujo programming language](https://kujolang.ai) and its agency and AI tooling ecosystem. Each kit demonstrates one concrete outcome and leaves behind inspectable evidence instead of relying on an opaque hosted runner.

Current release scope: **locally verified support/distribution technical preview** (`0.5.0`). Hosted runners, live-provider coverage, clean-machine installation on a separate host, and production or enterprise readiness are not claimed.

## Visual WebOps Reports

[`webops-dashboard/`](webops-dashboard/) is the local SQLite-backed reporting
surface for all ten WebOps workflows and the 28-role WebOps catalog. It imports
run packets without replacing their audit evidence, presents SiteKit tables and
filters, renders Dither Kit charts, and can start bounded `OBSERVE` or `PROPOSE`
website reports from the browser. It never grants `ACT`.

```bash
python3 webops-dashboard/dashboard.py sync
python3 webops-dashboard/dashboard.py serve --open
```

## Publishing House Operator

[`publishing-house-operator/`](publishing-house-operator/) is the durable,
low-touch control loop above the eleven Publishing House workflow kits. It
adds portable publication and voice profiles, SourcePack intake, weekly/monthly/
campaign plans imported into StoryDesk, dependency-aware daily ticks, event
commissioning, exact-version approval routing, checkpoints, leases, exception
notifications, fixture verification, and cron/launchd templates. It reuses the
existing Publishing House tools and authority boundaries instead of creating a
second queue, approval store, evidence system, package system, or publisher.

```bash
publishing-house-operator/bin/publishing-house --json init
publishing-house-operator/bin/publishing-house --json plan import \
  publishing-house-operator/fixtures/september-2026.json
publishing-house-operator/bin/publishing-house --json tick --fixture
```

## VideoOps Production Line

The five VideoOps kits form a file-handoff production line: creative planning,
rights-aware asset resolution, explicit media generation, HyperFrames editing,
and independent critique. The complete offline gate renders and inspects a real
1080p30 MP4 with audio, proves fail-closed asset behavior and the bounded
revision loop, and uses no credentials, network calls, or paid services.

```bash
bash tests/videoops-release-gate.sh
```

See the [implementation report](docs/videoops/implementation-report.md) for the
verified boundary and the live-provider work that remains external.

## Why Use These Workflows?

- Start from bounded, runnable examples instead of assembling a multi-tool workflow from scratch.
- Use fixture-first paths that are deterministic, local, and safe to evaluate without provider credentials.
- Inspect evidence packets, receipts, reports, and handoffs produced by each workflow.
- Keep host, provider, approval, and security boundaries explicit in both commands and documentation.
- Adapt individual kits without adopting a hosted workflow service.

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
| [`owned-agent-project/`](owned-agent-project/) | Limited | Agent builders | A repository-owned agent can be scaffolded, installed, diagnosed, inspected, run, evaluated, and evidenced through the canonical Kujo CLI. | `(cd owned-agent-project && bash scripts/run.sh)` |
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
| [`codebase-cleanup/`](codebase-cleanup/) | Limited | Maintainers, agent builders | Repository entropy becomes classified cleanup decisions, guarded reductions, verification, and review evidence. | `bash codebase-cleanup/scripts/run-workflow.sh --repo /path/to/repo` |
| [`webops-site-bootstrap/`](webops-site-bootstrap/) | Limited | Website operators | A site profile becomes validated crawl, graph, browser-capability, and reporting baseline evidence. | `(cd webops-site-bootstrap && bash scripts/run.sh --fixture)` |
| [`webops-weekly-site-health/`](webops-weekly-site-health/) | Limited | Website operators | Weekly crawl, link, performance, accessibility, schema, metadata, and reporting stages run with honest degradation. | `(cd webops-weekly-site-health && bash scripts/run.sh --fixture)` |
| [`webops-weekly-search-intelligence/`](webops-weekly-search-intelligence/) | Limited | Search teams | Search, keyword, and decay modules consume normalized fixture/provider capabilities independently. | `(cd webops-weekly-search-intelligence && bash scripts/run.sh --fixture)` |
| [`webops-weekly-content-intelligence/`](webops-weekly-content-intelligence/) | Limited | Content teams | Trend, opportunity, content graph, gap, accuracy, and linking stages produce proposals. | `(cd webops-weekly-content-intelligence && bash scripts/run.sh --fixture)` |
| [`webops-post-publish/`](webops-post-publish/) | Limited | Publishers | New content moves through targeted QA, graph, optional submission, distribution assets, and receipts. | `(cd webops-post-publish && bash scripts/run.sh --fixture)` |
| [`webops-content-refresh/`](webops-content-refresh/) | Limited | Content maintainers | Decay evidence becomes a Spec, approval boundary, verification plan, and future measurement cue. | `(cd webops-content-refresh && bash scripts/run.sh --fixture)` |
| [`webops-monthly-seo-review/`](webops-monthly-seo-review/) | Limited | SEO leads | Monthly specialist evidence is synthesized without reimplementing specialist analysis. | `(cd webops-monthly-seo-review && bash scripts/run.sh --fixture)` |
| [`webops-quarterly-content-portfolio/`](webops-quarterly-content-portfolio/) | Limited | Content strategists | Graph, measurement, portfolio, pruning, and IA evidence produce reviewed states. | `(cd webops-quarterly-content-portfolio && bash scripts/run.sh --fixture)` |
| [`webops-ai-visibility-benchmark/`](webops-ai-visibility-benchmark/) | Experimental | AI-search analysts | A fixed query-suite contract tracks only explicitly available surfaces. | `(cd webops-ai-visibility-benchmark && bash scripts/run.sh --fixture)` |
| [`webops-finding-to-fix/`](webops-finding-to-fix/) | Limited | Maintainers | A stable finding moves through Spec, approval, implementation boundary, Eval, Lens, SiteProbe, and receipt stages. | `(cd webops-finding-to-fix && bash scripts/run.sh --fixture)` |
| [`docsgen-repo-contract-runner/`](docsgen-repo-contract-runner/) | Limited | Developers, agent operators | DocsGen scans a chosen repo and writes an auditable documentation contract packet. | `(cd docsgen-repo-contract-runner && TARGET_REPO=/path/to/repo bash scripts/run-workflow.sh)` |
| [`tribunal-decision-gate/`](tribunal-decision-gate/) | Limited | Governance, release, security teams | Tribunal mock review becomes a verified advisory decision receipt. | `bash tribunal-decision-gate/scripts/run.sh` |
| [`relay-lifecycle-handoff/`](relay-lifecycle-handoff/) | Limited | Workflow operators | Relay pause/resume and integrity-checked export become correlated handoff receipts. | `bash relay-lifecycle-handoff/scripts/run.sh` |
| [`workcell-execution-gate/`](workcell-execution-gate/) | Limited | Agent operators | Workcell validates, inspects, and executes a bounded Docker package with completion evidence. | `bash workcell-execution-gate/scripts/run.sh` |
| [`publishing-house-governance/`](publishing-house-governance/) | Limited | Publishers and editorial leaders | A house mandate becomes explicit portfolio priorities and accountable operating handoffs. | `(cd publishing-house-governance && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-daily-desk/`](publishing-house-daily-desk/) | Limited | Editorial operators | A daily packet becomes explicit routes, deferrals, and blockers without manufacturing downstream state. | `(cd publishing-house-daily-desk && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-commissioning/`](publishing-house-commissioning/) | Limited | Commissioning teams | A specific editorial opportunity becomes a StoryDesk brief and evidence work order. | `(cd publishing-house-commissioning && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-evidence-dossier/`](publishing-house-evidence-dossier/) | Limited | Research and standards teams | Claims become classified, checksum-bound Dossier evidence and an independent readiness decision. | `(cd publishing-house-evidence-dossier && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-primary-piece/`](publishing-house-primary-piece/) | Limited | Writers and creative editors | An evidence-ready brief becomes a versioned primary artifact with claim lineage. | `(cd publishing-house-primary-piece && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-asset-production/`](publishing-house-asset-production/) | Limited | Media production teams | Supported local assets, accessibility records, provenance, and checksums become an AssetWorks manifest. | `(cd publishing-house-asset-production && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-editorial-review/`](publishing-house-editorial-review/) | Limited | Editorial review teams | Independent reviews and a bounded revision produce an exact reviewed GalleyPack version. | `(cd publishing-house-editorial-review && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-adaptation/`](publishing-house-adaptation/) | Limited | Franchise and creative teams | An approved primary artifact becomes a claim-bounded, versioned adaptation plan. | `(cd publishing-house-adaptation && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-format-production/`](publishing-house-format-production/) | Limited | Format desks and producers | Approved lineage becomes reviewable newsletter, social, case-study, and audiovisual packages. | `(cd publishing-house-format-production && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-approval-publication/`](publishing-house-approval-publication/) | Limited | Publishing operators and approvers | Dispatch pauses for checksum-bound VersionSeal approval before a bounded PressWire fixture effect. | `(cd publishing-house-approval-publication && bash scripts/test.sh)` |
| [`publishing-house-post-publication/`](publishing-house-post-publication/) | Limited | Audience and strategy teams | A verified receipt and compatible measurements become bounded learning and a StoryDesk follow-up. | `(cd publishing-house-post-publication && bash bin/run --request fixtures/request.fixture.json --json)` |
| [`publishing-house-operator/`](publishing-house-operator/) | Limited | Publishing operators | Publication-profile-driven intake, plans, event candidates, daily bounded progression, checkpoint/resume, approval pauses, and exception-only notifications. | `publishing-house-operator/bin/publishing-house --json doctor` |
| [`videoops-creative-planning/`](videoops-creative-planning/) | Limited | Video producers | Validated PackWrite intake becomes a timed creative brief, transcript, shot list, style plan, asset requirements, and explicit handoff. | `videoops-creative-planning/bin/run --fixture --workspace /absolute/project/path --run-id example` |
| [`videoops-asset-resolution/`](videoops-asset-resolution/) | Limited | Video producers | Every asset requirement terminates as found, captured, generated, not required, or blocked with rights and provenance evidence. | `videoops-asset-resolution/bin/run --fixture --workspace /absolute/project/path --run-id example` |
| [`videoops-media-generation/`](videoops-media-generation/) | Limited | Video producers | Only requirements explicitly marked `GENERATE` are processed and registered; other assets remain untouched. | `videoops-media-generation/bin/run --fixture --workspace /absolute/project/path --run-id example` |
| [`videoops-hyperframes-edit/`](videoops-hyperframes-edit/) | Limited | Video editors | Approved plans and assets become a checked HyperFrames composition, real render, audio-muxed output, technical evidence, and bounded revisions. | `videoops-hyperframes-edit/bin/run --fixture --workspace /absolute/project/path --run-id example` |
| [`videoops-quality-review/`](videoops-quality-review/) | Limited | Video reviewers | An independent critic issues PASS or an actionable timestamped fix list and stops after the revision limit. | `videoops-quality-review/bin/run --fixture --workspace /absolute/project/path --run-id example` |

### Install Publishing House locally

The eleven Publishing House kits have one locked, tested installation path.
Supply an existing Kujo 1.0.1 binary; the installer uses local sibling
checkouts when available and otherwise clones the exact commits in the install
lock:

```bash
bash scripts/install-publishing-house.sh \
  --prefix "$PWD/.local/publishing-house" \
  --kujo-bin /absolute/path/to/kujo \
  --demo

.local/publishing-house/bin/publishing-house-doctor
.local/publishing-house/bin/publishing-house-demo \
  --out "$PWD/.local/publishing-house/runs/second-run"
```

The installer refuses an existing target, installs into a staging directory,
pins clean dependency checkouts, runs the Kujo-native contract doctor, and can
run the complete eleven-workflow offline proof before reporting success. It
does not install credentials or enable live publication.

## Verification

Run the portable release gates:

```bash
python3 -m pip install jsonschema PyYAML
bash tests/release-readiness.sh
bash tests/clean-checkout.sh
```

The first command validates release metadata, documentation links, catalog structure, contracts, tests, syntax, artifact-ignore coverage, and whitespace. The clean-checkout gate repeats the repository-owned checks from a temporary archive containing only tracked files.

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

See the current [launch checklist](docs/launch-checklist.md) and [release-readiness Spec](kujo-workflows.spec.yml) for the exact boundary and acceptance contract.

## Repository Map

- [`agency-runner/`](agency-runner/) and the other top-level workflow directories contain runnable kits and workflow-specific guidance.
- [`contracts/`](contracts/) contains versioned Tribunal, Relay, and Workcell evidence contracts.
- [`docs/audit/`](docs/audit/) contains the machine-readable workflow catalog and compatibility evidence.
- [`docs/publishing-house/`](docs/publishing-house/) documents the eleven-kit editorial lifecycle, ownership boundaries, fixture proof, and compatibility matrix.
- [`docs/videoops/`](docs/videoops/) documents the VideoOps implementation and verified offline/live boundary.
- [`publishing-house-operator/`](publishing-house-operator/) contains the operator, publication and voice profiles, SourcePack/plan schemas, scheduler templates, Eval suite, fixtures, and tests.
- [`examples/`](examples/) identifies low-risk starting points.
- [`scripts/`](scripts/) contains repository validators.
- [`tests/`](tests/) contains portable release and integration checks.
- [`kujo-workflows.spec.yml`](kujo-workflows.spec.yml) is the canonical `0.5.0` acceptance contract.

## Documentation

- [`contracts/README.md`](contracts/README.md) — versioned evidence contracts and compatibility rules.
- [`docs/audit/README.md`](docs/audit/README.md) — catalog, compatibility, and weekly drift evidence.
- [`docs/publishing-house/README.md`](docs/publishing-house/README.md) — Publishing House lifecycle, fixture/live boundaries, approval, inspection, and recovery.
- [`docs/videoops/implementation-report.md`](docs/videoops/implementation-report.md) — VideoOps architecture, proof coverage, and external limits.
- [`docs/launch-checklist.md`](docs/launch-checklist.md) — verified launch gates and remaining external proof.
- [`docs/specs/showcase-release-readiness.md`](docs/specs/showcase-release-readiness.md) — rendered `0.5.0` acceptance contract.

## Release and Support Status

This repository is the MIT-licensed `0.5.0` technical preview of the Kujo workflow-kit distribution. The checkout covers 43 local workflows, including the Owned Agent Project proof, the eleven-workflow Publishing House lifecycle, the Publishing House Operator control layer, and the five-stage VideoOps production line, plus shared contracts, documentation, versioned evidence contracts, and repository-owned validation gates. It does not publish a package, container image, hosted runner, or workflow service.

For contribution, support, conduct, and vulnerability-reporting guidance, see [CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md).

## Known Limits

- Some Kujo interpreter runs emit type-checking warnings before successful artifact output; workflow scripts use exit status plus expected artifacts as the contract.
- Live providers, authenticated browser flows, external customer repositories, and hosted execution require separate credentials and approval.
- Tribunal mock decisions are advisory and unsigned.
- Relay proves local persistence and bounded retries, not remote exactly-once delivery.
- Workcell is a trusted local Docker/Podman boundary, not a hosted scheduler or microVM isolation layer.
- The locked Publishing House installer and all-eleven first run pass from a tracked archive on the development host; validation on a physically separate host remains open.

## License

Kujo Workflows is available under the [MIT License](LICENSE). Changes are recorded in [CHANGELOG.md](CHANGELOG.md).
