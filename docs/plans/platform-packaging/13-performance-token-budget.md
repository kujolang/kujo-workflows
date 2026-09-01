# 13 — Performance and Token Budget

## Baseline observations

Local measurements on 2026-09-01:

| Measure | Observed |
| --- | --- |
| WebOps domain skills | 27 files, 42,253 bytes, 5,347 words (~7.1k tokens by word heuristic; ~10.6k by bytes/4) |
| Fixture `site-bootstrap` | 3.04 s wall, 184 KiB run packet, 10 findings |
| Fixture `weekly-site-health` | 3.45 s wall, 168 KiB run packet, 10 findings |

These are two single host observations, not statistical performance claims. The current runtime is dominated by the shared fixture crawl/tool startup; adapter resolution must add negligible local overhead.

## Initial budgets

| Surface | Budget/target | Verification |
| --- | --- | --- |
| Profile parse + detection plan (no build/network) | p95 <= 100 ms on reference fixture repo | 20-run local benchmark |
| Adapter discovery + resolution for 20 instances/50 Abilities | p95 <= 50 ms | deterministic benchmark |
| Added workflow startup overhead | <= 150 ms and <= 5% of current fixture median, report both | counterbalanced runs |
| Adapter manifest | <= 32 KiB | schema gate |
| Resolver receipt | <= 2 KiB per requested Ability; summary <= 32 KiB | byte gate |
| Default active skills | <= 12; target <= 20 KiB prose per outcome | activation test |
| MCP tools visible by default | <= 12 per outcome/site | registry snapshot |
| Agent-visible adapter metadata | <= 4 KiB/provider/run | serialized fixture |
| Provider calls | explicit per-Ability budget; list reads default <= 20 calls | receipt assertion |
| Provider output | default normalized result <= 1 MiB, report <= 2,000 tokens | existing output guards |

Budgets may be revised only from measured fixtures and documented use cases.

## Context minimization

- select skills by outcome/workflow, not installed platform;
- expose only available/allowed Abilities, not the provider API schema;
- keep provider field mapping in adapter code/fixtures;
- provide concise limitations and source links rather than embedding docs;
- return references/digests for full evidence and bounded summaries to agents;
- lazy-load mutation schemas only after a proposal reaches an approval gate;
- filter MCP tools and agent roles by the chosen site and workflow.

## Benchmarks

Create deterministic benchmarks for:

1. profile v1 migration/v2 validation;
2. repository-only detection on small/medium/large fixture trees;
3. binding conflict resolution;
4. 1/10/50 adapter manifest discovery;
5. pagination normalization for 100/1,000/10,000 records;
6. evidence/receipt byte bounds;
7. workflow startup with zero/one/five installed bundles;
8. active skill/tool definition bytes by outcome.

No live API latency benchmark belongs in the release gate; provider smoke reports it separately.

