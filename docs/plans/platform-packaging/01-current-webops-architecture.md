# 01 — Current WebOps Architecture

## What Kujo WebOps is today

Kujo WebOps is a repository-backed, local-first operating system for recurring website evidence and governed change. It consists of ten fixture-first workflow kits, a shared Python execution harness, 27 domain skills plus three tool skills, a 28-role agent catalog, a local SQLite reporting dashboard, and three primary evidence tools: SiteProbe, SearchBridge, and ContentGraph. It composes Lens, Eval, Spec, Dispatch, RunLedger, Howl, RAG, Scout, CaseFile, PatchBrief, and ChangeBucket at workflow boundaries rather than hiding them behind a hosted service.

The current implementation is a credible platform-neutral proof, but not yet a platform packaging system. The shared harness directly switches on tool names, accepts one `site.platform` string, treats capabilities as loosely typed booleans/strings, and writes specialist receipts without invoking most specialist implementations. Live mutation adapters, adapter discovery, multi-provider binding, and conformance do not exist.

## Current dependency map

```text
site profile v1
  -> scripts/webops_workflow.py
      -> SiteProbe ------> crawl/headers/metadata/schema/links/robots/sitemap
      -> SearchBridge ---> normalized search/analytics/performance/backlinks/submission
      -> ContentGraph ---> content inventory/relationships/clusters/opportunities
      -> Lens -----------> browser/render/accessibility/visual evidence (optional)
      -> specialist stage receipts
      -> findings + report + run receipt

Spec defines bounded work        Eval verifies expected outcomes
Dispatch owns orchestration      RunLedger owns run/action correlation
Howl owns distribution assets    CaseFile owns failure evidence
```

## Workflow audit

| Workflow | Inputs and assumptions | Outputs/evidence | Dependencies | Network/browser/filesystem | Effect boundary |
| --- | --- | --- | --- | --- | --- |
| `site-bootstrap` | HTTP(S) URL; optional repository; current profile assumes one `platform` | profile, capabilities, crawl, graph, findings, report, receipt | SiteProbe, Scout, ContentGraph, RAG, Lens, RunLedger | Live crawl; optional browser; local run directory/repository | OBSERVE; repository read-only |
| `weekly-site-health` | URL, prior run optional | crawl/render quality, performance, accessibility, schema, metadata findings | SiteProbe, Lens, SearchBridge, RunLedger | Live HTTP; optional provider/browser | OBSERVE; no site mutation |
| `weekly-search-intelligence` | provider capabilities and optional historical evidence | search/keyword/decay evidence and report | SearchBridge, ContentGraph, RunLedger | Provider network optional | OBSERVE; missing providers degrade |
| `weekly-content-intelligence` | website/corpus, optional research and query data | graph, gaps, accuracy/link proposals | ContentGraph, SearchBridge, RAG, SiteProbe, RunLedger | crawl and optional providers; local corpus | PROPOSE; never edits content |
| `post-publish` | published URL/item, optional provider capabilities | targeted QA, graph, submission/distribution receipts | SiteProbe, ContentGraph, Lens, Eval, SearchBridge, Howl, RunLedger | live site/browser; optional submission provider | PROPOSE default; submission/publishing ACT |
| `content-refresh` | stable decay finding, content evidence, target | Spec, proposed update, evaluation/QA plan, future measurement cue | SearchBridge, ContentGraph, Spec, Eval, Lens, RunLedger | repository/CMS assumed for real update but not modeled | PROPOSE default; content mutation and submission ACT |
| `monthly-seo-review` | specialist run evidence | synthesis and prioritized findings | SiteProbe, SearchBridge, ContentGraph, Lens, RunLedger | inherited from evidence providers | OBSERVE; fixes route to finding-to-fix |
| `quarterly-content-portfolio` | graph and measurement history | retain/refresh/consolidate/retire proposals and IA evidence | ContentGraph, SearchBridge, SiteProbe, RunLedger | crawl/providers/local history | PROPOSE; merge/redirect/retire ACT |
| `ai-visibility-benchmark` | fixed query suite and explicitly available surfaces | capabilities, longitudinal visibility findings, report | SearchBridge, RunLedger, CaseFile | provider/web access optional | OBSERVE; never fabricates absent surfaces |
| `finding-to-fix` | one stable finding and target | Spec, approval receipt, implementation boundary, Eval/Lens/SiteProbe proof | Spec, Eval, Lens, SiteProbe, RunLedger, CaseFile, PatchBrief, ChangeBucket | repository/build/browser as selected | PROPOSE default; implementation ACT |

All ten produce `state.json`, `capabilities.json`, `steps/*.json`, `findings.json`, `report.md`, and `run-receipt.json`. Finding identity is deterministic. Runs resume from completed steps. Fixture mode is offline and credential-free. Missing optional evidence becomes `skipped-degraded`, not a false zero.

## Existing reusable contracts

- `webops.workflow/v1` already provides workflow identity, default permission, tools, skills, agents, credentials, approval boundaries, and outputs.
- `webops.site-profile/v1` already has the correct home: profile, integrations, permission default, and credential references. Extend it; do not create `webops.platform.json`.
- `webops.capability-receipt/v1`, `webops.step-receipt/v1`, `webops.finding/v1`, and `webops.run-receipt/v1` provide the evidence spine.
- The agent permission model already defines OBSERVE, PROPOSE, and ACT as upper bounds.
- `kujo.ability/v1` already separates semantic operation definitions from bindings, authorization, approval, and transport. Reuse it instead of inventing a parallel generic provider-capability schema.
- Kujo workflow packs already provide local namespaced commands and doctor contributions, but run external Kujo scripts with `--allow-all`; this is a distribution shell, not yet the adapter security boundary.
- Agent packages and MCP already support projection of selected Abilities without making MCP the semantic source of truth.

## Current limitations that implementation must address

1. `site.platform` encodes one fake site identity.
2. Capability values are not typed declarations, provider bindings, or verified availability.
3. Core dispatch switches on internal tool names, not semantic operations.
4. Live profiles cannot compose framework, CMS, commerce, deployment, edge, analytics, and search providers.
5. The harness has no adapter manifest, identity verification, pagination/rate handling, error normalization, or receipt contract.
6. Provider mutations are represented only as generic approval-required stage receipts.
7. Dashboard-launched runs generate a minimal v1 profile and cannot select or verify providers.
8. All workflow skills are discoverable as one large set; there is no outcome/platform-scoped activation manifest.
9. Workflow-pack distribution has no remote install and insufficient effect enforcement for untrusted adapters.

## Repository ownership conclusion

`kujo-workflows` should own site-profile, WebOps Ability catalog, adapter/binding manifests, resolver, workflow integration, fixtures, conformance, support-bundle manifests, docs, and release proof. Canonical `kujo.ability/v1` remains owned by the Ability package. Provider measurement implementations remain in SearchBridge. Site inspection remains in SiteProbe. Content relationships remain in ContentGraph. Runtime orchestration remains in Dispatch.

