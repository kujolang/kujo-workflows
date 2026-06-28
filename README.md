# Kujo Workflows

This repo collects runnable workflow kits for the Kujo agency and AI tooling stack. Each workflow is meant to be a content pillar: it demonstrates a concrete developer, agency, or enterprise outcome and leaves behind reviewable local artifacts.

## Workflow Catalog

| Workflow | Audience | What it proves | Run command |
| --- | --- | --- | --- |
| `agency-runner/` | Agency owners | Client tasks can become reusable local run packets. | `python3 bin/agency-loop ...` |
| `agency-verified-fix-loop/` | Agencies, developers | A bug fix can move through spec, context, proof, brief, and handoff artifacts. | `bash scripts/run-loop.sh` |
| `feature-card-workflow/` | Developers | A task card can drive implementation, verification, proof, and reviewer handoff. | `bash muzzle-template/workflows/feature-card-full.sh ...` |
| `ai-sdk-watchdog-showcase/` | AI app developers | AI SDK calls can be routed through Watchdog and exported as telemetry. | `bash scripts/run-showcase.sh` |
| `ai-sdk-muzzle-benchmark/` | AI app teams | Repeated AI SDK app generations can be benchmarked and reviewed. | `bash scripts/run-suite.sh` |
| `enterprise-dispatch-approval-router/` | Enterprise platform teams | Dispatch creates auditable workflow state, trace, report, and diagnostics. | `bash scripts/run-workflow.sh` |
| `mcp-agent-gateway-review/` | Developers, enterprise AI teams | `mcp make` generates a guarded MCP server scaffold and safety packet. | `bash scripts/run-workflow.sh` |
| `rag-enterprise-knowledge-gate/` | Enterprise knowledge teams | RAG ingests local docs, isolates a namespace, and answers with citations. | `bash scripts/run-workflow.sh` |
| `casefile-incident-evidence-packet/` | Developers, support teams | CaseFile captures a failing command as a reproducible evidence bundle. | `bash scripts/run-workflow.sh` |
| `howl-content-factory/` | Developers, agency owners | Howl turns real Kujo examples into Markdown, HTML, SVG, gallery, and captions. | `bash scripts/run-workflow.sh` |
| `loop-engineering/` | Anyone building agents | A bounded Goal→Context→Agent→Evaluation→Stop loop runs portably and stops safely. | `bash scripts/run-workflow.sh` |
| `docsgen-repo-contract-runner/` | Developers, agent operators | DocsGen scans a user-chosen repo and writes an auditable docs contract packet. | `TARGET_REPO=/path/to/repo bash scripts/run-workflow.sh` |

## Portable Pattern: Loop Engineering

`loop-engineering/` is different from the other kits: it is not bound to a single
fixture or local path. It is a decentralized, system-agnostic implementation of the
agent-loop pattern (Goal → Context → Agent → Evaluation → Stop) that maps onto real
Kujo tooling through adapters while running anywhere — local CLI harnesses, repo
bots, CI, scheduled jobs, human-in-the-loop review, and future Kujo/BZBY
orchestration. The reference driver runs with zero dependencies and enforces the
stop conditions; see [`loop-engineering/WORKFLOW.md`](loop-engineering/WORKFLOW.md)
and [`loop-engineering/loop.spec.yml`](loop-engineering/loop.spec.yml).

## New Content Pillars

The newer workflow kits cover a broad buyer story without duplicating the existing agency fix-loop examples.

1. `enterprise-dispatch-approval-router/` - governed AI workflow orchestration for enterprise review and approval.
2. `mcp-agent-gateway-review/` - safe agent tool gateways for codebases and internal platforms.
3. `rag-enterprise-knowledge-gate/` - grounded local knowledge retrieval with namespace isolation and citations.
4. `casefile-incident-evidence-packet/` - incident and failed-run evidence that another human or agent can act on.
5. `howl-content-factory/` - deterministic content asset generation from real examples.
6. `docsgen-repo-contract-runner/` - user-chosen repo documentation generation with JSON, gap files, and agent handoff artifacts.

Each newer workflow includes:

- `README.md`
- `HOWTO.md`
- `TODO.md`
- `scripts/run-workflow.sh`

Generated `.runs/<timestamp>/SUMMARY.md` packets are local proof artifacts and are ignored in most workflow directories.

## Verification Snapshot

The newer workflow demos were run successfully in this workspace:

```text
enterprise-dispatch-approval-router/.runs/20260613T150711Z/SUMMARY.md
mcp-agent-gateway-review/.runs/20260613T150737Z/SUMMARY.md
rag-enterprise-knowledge-gate/.runs/20260613T150746Z/SUMMARY.md
casefile-incident-evidence-packet/.runs/20260613T150757Z/SUMMARY.md
howl-content-factory/.runs/20260613T150812Z/SUMMARY.md
docsgen-repo-contract-runner/.runs/20260628T015632Z/SUMMARY.md
```

Useful verification command:

```bash
for d in enterprise-dispatch-approval-router mcp-agent-gateway-review rag-enterprise-knowledge-gate casefile-incident-evidence-packet howl-content-factory docsgen-repo-contract-runner; do
  (cd "$d" && bash scripts/run-workflow.sh)
done
```

## Current Caveats

- Some Kujo interpreter runs emit type-checking warnings before successful output. For these workflow demos, exit status and generated artifacts are the verification source.
- `agency-verified-fix-loop/` can still expose missing optional tool binaries in this checkout, especially the historical `changebucket` path. The newer workflows were chosen to run with the tools available locally.
- Generated `.runs/` folders are proof artifacts. Keep or clean them based on whether you want verified packets committed.

## Content Positioning

Use the workflows as a sequence:

1. Developers: start with `feature-card-workflow/`, `casefile-incident-evidence-packet/`, and `mcp-agent-gateway-review/`.
2. Agency owners: show `agency-verified-fix-loop/`, `agency-runner/`, and `howl-content-factory/`.
3. Enterprise: lead with `enterprise-dispatch-approval-router/`, `rag-enterprise-knowledge-gate/`, and `ai-sdk-watchdog-showcase/`.

The common message is simple: Kujo turns AI-assisted work into local, inspectable, repeatable artifacts.
