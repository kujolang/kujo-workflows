# Kujo WebOps Build Report

## 1. Executive Summary

Kujo WebOps v1 is implemented and live. The campaign delivered three executable Kujo-first tools, 28 governed WebOps agents, 30 new skills, 10 resumable workflows, shared capability/history contracts, deterministic fixtures, cross-repository validation, and 28 published profiles at `https://agents.kujolang.ai/agents/webops/`. The existing 28-agent Chain of Command remains intact.

## 2. WebOps Tools

| Tool | Repository | Purpose | Status and primary commands | Primary artifacts | Tests | Maturity boundary |
| --- | --- | --- | --- | --- | --- | --- |
| SiteProbe | `kujolang/siteprobe` | Bounded same-origin crawl, inspect, validate, compare, link, sitemap, and report evidence | Implemented: `doctor`, `crawl`, `inspect`, `validate`, `compare`, `report`, `links`, `sitemap` | `run.json`, `pages.jsonl`, `links.jsonl`, `redirects.jsonl`, `findings.json`, `summary.json`, `report.md` | Python contract tests plus executable Kujo entrypoint tests | Production-capable with explicit crawl bounds; HTML/XML parsing uses a Python standard-library bridge until Kujo has equivalent complete parsers. |
| SearchBridge | `kujolang/searchbridge` | Normalize optional search, analytics, performance, backlink, keyword, inspection, and submission providers | Implemented: `doctor`, `capabilities`, `providers`, `search-performance`, `analytics`, `inspect-url`, `pagespeed`, `crux`, `backlinks`, `keyword-data`, `submit` | Normalized result, capability, error, and submission receipt JSON | Fixture coverage for every provider, degradation, output bounds, and ACT gates through Python and Kujo | Provider availability, quotas, cost, and accuracy remain external; submission never claims indexing. |
| ContentGraph | `kujolang/contentgraph` | Deterministic content inventory, relationship graph, clustering, overlap, orphan, and internal-link analysis | Implemented: `doctor`, `build`, `inspect`, `related`, `orphans`, `clusters`, `overlaps`, `link-opportunities`, `compare`, `export` | `metadata.json`, `nodes.jsonl`, `edges.jsonl`, `graph.json`, `clusters.json`, `overlaps.json`, `orphan-candidates.json`, `link-opportunities.json`, GraphML | Source and SiteProbe ingestion, comparisons, exports, errors, and Kujo entrypoint | Deterministic lexical TF-IDF/cosine analysis, not semantic embeddings; every proposal requires context review. |

## 3. WebOps Agents

| Agent | Category | Primary tools | Primary skills | Required capability | Optional integrations | Permission range |
| --- | --- | --- | --- | --- | --- | --- |
| Trend Scout | Discovery & Intelligence | SearchBridge, ContentGraph, RAG | search-standards-watch, keyword-opportunity, RAG, RunLedger | website, web-search | keyword data | OBSERVE–PROPOSE |
| Keyword Opportunity Analyst | Discovery & Intelligence | SearchBridge, ContentGraph, SiteProbe | keyword-opportunity, capability-preflight, RAG, RunLedger | website | keyword data, web search | OBSERVE–PROPOSE |
| Competitor Intelligence Analyst | Discovery & Intelligence | SiteProbe, SearchBridge, ContentGraph, RAG | competitor-intelligence, longitudinal-findings, RAG, RunLedger | web-search | backlinks, keyword data | OBSERVE–PROPOSE |
| Content Gap Analyst | Discovery & Intelligence | ContentGraph, SearchBridge, RAG | content-gap, keyword-opportunity, RAG, RunLedger | website, content-graph | search performance, keyword data | OBSERVE–PROPOSE |
| Backlink & Mention Analyst | Discovery & Intelligence | SearchBridge, SiteProbe | backlink-and-mention-analysis, longitudinal-findings, RunLedger, CaseFile | web-search | backlinks | OBSERVE–PROPOSE |
| SEO Auditor | Search Operations | SiteProbe, SearchBridge, ContentGraph, Lens | technical-seo, reporting, longitudinal-findings, Lens, RunLedger | website | analytics, backlinks, performance | OBSERVE–PROPOSE |
| Search Performance Analyst | Search Operations | SearchBridge, ContentGraph | search-performance, longitudinal-findings, RunLedger | search performance | content graph, analytics | OBSERVE–PROPOSE |
| Indexation Analyst | Search Operations | SiteProbe, SearchBridge, ContentGraph | indexation, technical-seo, RunLedger | website, site-crawl | search performance | OBSERVE–PROPOSE |
| Technical SEO Auditor | Search Operations | SiteProbe, ContentGraph, Lens, SearchBridge | technical-seo, link-health, schema-and-metadata, Lens, RunLedger | website, site-crawl | browser, URL inspection | OBSERVE–PROPOSE |
| AI Search Visibility Analyst | Search Operations | SearchBridge, RunLedger | ai-search-visibility, longitudinal-findings, RunLedger, CaseFile | website, web-search | search performance | OBSERVE–PROPOSE |
| Content Decay Analyst | Content Operations | SearchBridge, ContentGraph, SiteProbe, RAG | content-decay, content-accuracy, RAG, RunLedger | website | analytics, keyword data | OBSERVE–PROPOSE |
| Internal Link Specialist | Content Operations | ContentGraph, SiteProbe, SearchBridge, Eval | internal-linking, information-architecture, Eval, Lens, RunLedger | website, content-graph | search performance | OBSERVE–ACT |
| Content Accuracy Reviewer | Content Operations | RAG, ContentGraph, SiteProbe | content-accuracy, RAG, CaseFile | website, web-search | repository, content graph | OBSERVE–PROPOSE |
| Cannibalization Analyst | Content Operations | ContentGraph, SearchBridge, SiteProbe | cannibalization, search-performance, RunLedger | website, content-graph | keyword data | OBSERVE–PROPOSE |
| Content Portfolio Manager | Content Operations | ContentGraph, SearchBridge, SiteProbe | content-portfolio, longitudinal-findings, Spec, RunLedger | website, content-graph | keyword data | OBSERVE–PROPOSE |
| Content Pruning Analyst | Content Operations | ContentGraph, SearchBridge, SiteProbe | content-pruning, content-portfolio, Spec, RunLedger | website, content-graph | backlinks | OBSERVE–PROPOSE |
| Site QA Operator | Quality Operations | Lens, SiteProbe, CaseFile, Eval | link-health, accessibility-review, Lens, CaseFile, Eval | website, browser | repository | OBSERVE–PROPOSE |
| Performance Analyst | Quality Operations | SearchBridge, Lens | web-performance, longitudinal-findings, Lens, RunLedger | website | field performance, browser | OBSERVE–PROPOSE |
| Accessibility Auditor | Quality Operations | Lens, Eval, CaseFile | accessibility-review, Lens, CaseFile | website, browser | repository | OBSERVE–PROPOSE |
| Schema Auditor | Quality Operations | SiteProbe, Lens, Eval | schema-and-metadata, Eval, Lens | website, site-crawl | web search, repository | OBSERVE–PROPOSE |
| Link Health Auditor | Quality Operations | SiteProbe, Lens, CaseFile | link-health, Lens, CaseFile | website, site-crawl | browser, repository | OBSERVE–PROPOSE |
| Metadata Auditor | Quality Operations | SiteProbe, Lens | schema-and-metadata, technical-seo, Lens, RunLedger | website, site-crawl | repository | OBSERVE–PROPOSE |
| Search Submission Operator | Operations & Management | SearchBridge, RunLedger, Dispatch | search-submission, capability-preflight, RunLedger, Dispatch | search submission | none | ACT only |
| Analytics Analyst | Operations & Management | SearchBridge, ContentGraph | analytics-analysis, longitudinal-findings, RunLedger | analytics | content graph, search performance | OBSERVE–PROPOSE |
| Information Architecture Auditor | Operations & Management | ContentGraph, SiteProbe, Lens | information-architecture, internal-linking, Lens, Spec | website, content-graph | browser, repository | OBSERVE–PROPOSE |
| Distribution Operator | Operations & Management | Howl, CMS, SSG, RunLedger | distribution, Howl, CMS, SSG, RunLedger | website | publishing provider | PROPOSE–ACT |
| Search & Web Standards Watch | Operations & Management | RAG, RunLedger | search-standards-watch, longitudinal-findings, RAG, RunLedger | web-search | website | OBSERVE–PROPOSE |
| WebOps Reporter | Operations & Management | RunLedger, CaseFile | reporting, longitudinal-findings, RunLedger, CaseFile | website | crawl, graph, search, analytics | OBSERVE–PROPOSE |

## 4. Skills

- New tool skills: `kujo-siteprobe-workflows`, `kujo-searchbridge-workflows`, `kujo-contentgraph-workflows`.
- New WebOps domain skills: `webops-site-profile`, `webops-capability-preflight`, `webops-longitudinal-findings`, plus 24 specialist skills covering search, content, quality, intelligence, operations, and reporting (27 domain skills total).
- Existing Kujo skills reused where relevant: Lens, RAG, RunLedger, CaseFile, Eval, Spec, Scout, Dispatch, Howl, CMS, SSG, PatchBrief, and ChangeBucket workflows.

All 30 new skills have distinct triggers, workflows, outputs, stop rules, anti-scope, capability degradation, and deterministic validation coverage. The full repository gate validates 83 skills.

## 5. Workflows

Every workflow supports fixtures, stable artifacts, resumable `state.json`, step receipts, capability preflight, and final validation.

| Name | Purpose | Agent sequence | Tools | Credentials required? | Fixture mode | Validation |
| --- | --- | --- | --- | --- | --- | --- |
| `webops-site-bootstrap` | Establish initial evidence baseline | Site Profile → Preflight → SiteProbe → Scout → ContentGraph → RAG → Site QA → Reporter | SiteProbe, Scout, ContentGraph, RAG, Lens, RunLedger | No | Yes | Pass |
| `webops-weekly-site-health` | Compare crawl/rendered quality | SiteProbe → Site QA → Link → Performance → Accessibility → Schema → Metadata → Reporter | SiteProbe, Lens, SearchBridge, RunLedger | No; performance provider optional | Yes | Pass |
| `webops-weekly-search-intelligence` | Compare search and decay evidence | SearchBridge → Search Performance → Keyword → Decay → Reporter | SearchBridge, ContentGraph, RunLedger | Optional | Yes | Pass |
| `webops-weekly-content-intelligence` | Find trends, gaps, accuracy, and link proposals | Trend → Keyword → ContentGraph → Gap → Accuracy → Links → Reporter | ContentGraph, SearchBridge, RAG, SiteProbe, RunLedger | Optional | Yes | Pass |
| `webops-post-publish` | Verify a newly published item | SiteProbe → Metadata → Schema → Links → Site QA → Submission → Distribution → Reporter | SiteProbe, ContentGraph, Lens, Eval, SearchBridge, Howl, RunLedger | Only optional ACT steps | Yes | Pass |
| `webops-content-refresh` | Turn decay evidence into a verified update boundary | Decay → Accuracy → Search → Graph → Spec → authorized update → Eval → QA → Submission → Reporter | SearchBridge, ContentGraph, Spec, Eval, Lens, RunLedger | Optional measurement/submission | Yes | Pass |
| `webops-monthly-seo-review` | Synthesize specialist SEO evidence | SEO and ten specialist audits → Reporter | SiteProbe, SearchBridge, ContentGraph, Lens, RunLedger | Optional | Yes | Pass |
| `webops-quarterly-content-portfolio` | Classify the content portfolio | Graph → Search → Analytics → Decay → Portfolio → Pruning → IA → Reporter | ContentGraph, SearchBridge, SiteProbe, RunLedger | Optional | Yes | Pass |
| `webops-ai-visibility-benchmark` | Run a fixed longitudinal visibility suite | Preflight → AI Visibility → Reporter | SearchBridge, RunLedger, CaseFile | Optional by surface | Yes | Pass |
| `webops-finding-to-fix` | Carry one stable finding through a governed fix | Finding → Spec → Proposal → Approval → Implementation → Eval → QA → SiteProbe → Reporter | Spec, Eval, Lens, SiteProbe, RunLedger, CaseFile, PatchBrief, ChangeBucket | No; ACT approval required | Yes | Pass |

## 6. Integrations

| Integration | Classification | Notes |
| --- | --- | --- |
| Google Search Console Search Analytics | Implemented, optional, fixture-supported | Live mode requires scoped OAuth token and property access. |
| Google Search Console URL Inspection | Implemented, optional, fixture-supported | Availability degrades independently. |
| Google Analytics 4 Data API | Implemented, optional, fixture-supported | Preserves requested dimensions/metrics and provider uncertainty. |
| PageSpeed Insights | Implemented, optional, fixture-supported | Can run without a key at provider limits; key is optional. |
| Chrome UX Report | Implemented, optional, fixture-supported | Field data may be absent for low-traffic origins/URLs. |
| IndexNow | Implemented, optional, fixture-supported | Submission requires `--act --yes`; receipt states submitted, never indexed. |
| Bing Webmaster | Implemented, optional, fixture-supported | Search/backlink reads and sitemap submission are capability-scoped. |
| Ahrefs API v3 | Implemented, optional, fixture-supported | Paid units and subscription are explicit capability/cost boundaries. |
| Google Indexing API for general pages | Deferred | Official scope is job-posting and livestream pages, so WebOps does not misrepresent it as general-content indexing. |
| Browser, repository, CMS, publishing, and distribution adapters | Optional | Consumed only when a workflow profile declares the capability and appropriate permission. |

## 7. History & Learning

Each site owns `.webops/profiles`, `runs`, `findings`, `history`, and `baselines`. Finding identity is a stable hash of agent, check, normalized target, and issue identity rather than run time. Comparisons classify evidence as `NEW`, `PERSISTENT`, `RESOLVED`, `REGRESSED`, or `REOPENED`. Recommendation records say what should happen; action records prove what was authorized/executed; outcome records capture later measured effects. These IDs are linked, never collapsed into an unsupported causal claim.

## 8. `kujo-agents`

The package now has sibling `chain-of-command/` and `webops/` sets. WebOps contains 28 `AGENT.md` contracts, 28 role `SKILL.md` files, central agent/tool/capability/permission/history/workflow maps, and `webops-catalog.json`. Validation proves the exact roster, required headings and governance fields, known capability/tool/skill/workflow references, unchanged 28-agent Chain of Command, safe secret patterns, and generated-source consistency.

## 9. `agents.kujolang.ai`

- Collection: `https://agents.kujolang.ai/agents/webops/`
- Published: 28 WebOps agents; all individual routes are in the generated site and sitemap.
- Live result: collection and sample profile returned 200 after Pages deployment; the live collection contains 28 cards.
- Regression result: Chain of Command collection still contains 28 cards.
- Sync: multi-set sync owns stale deletion per set, preserves unrelated sets, uses Git-derived update dates, records sync state, and validates canonical GitHub sources.
- Images: existing Chain of Command portraits use checked-in WebP assets; agents without portraits use the Kujo logomark fallback. No invented portraits were generated.

## 10. Dogfood Results

Local SiteProbe inspected 60 generated pages and 1,177 links. Its only 60 warnings were expected canonical conflicts between the local test origin and production canonicals; there were no orphan nodes in the 60-node/1,558-edge ContentGraph. Final Lens runs passed on `/agents/`, `/agents/webops/`, and an individual WebOps profile at desktop and mobile widths with zero errors, zero automated accessibility violations, no broken checked links, and no horizontal overflow. A deliberately low-concurrency live SiteProbe crawl then verified all 60 public pages and 1,177 links with zero findings; all 28 WebOps profile URLs independently returned HTTP 200.

## 11. Validation

- `bash siteprobe/scripts/validate.sh` — pass (Python tests, Kujo check, executable Kujo test entrypoint, schemas, diff check).
- `bash searchbridge/scripts/validate.sh` — pass with the same layers and provider fixtures/ACT gates.
- `bash contentgraph/scripts/validate.sh` — pass with the same layers and graph fixtures/exports.
- `bash kujo-skills/tests/release-readiness.sh` — pass; 83 skills validated.
- `python3 kujo-agents/scripts/validate_webops.py` — pass; 28 WebOps, 28 role skills, 28 Chain of Command agents.
- `python3 kujo-workflows/tests/test_webops_workflows.py` — pass; all 10 workflows plus resume/stable-ID behavior.
- `bash kujo-workflows/tests/release-readiness.sh` and `bash scripts/validate-webops-campaign.sh` — pass.
- Agent-site source/content/build validators — pass; 61 HTML files checked.
- Lens final route checks — pass at desktop/mobile with accessibility, links, and performance enabled.
- Credential-pattern scan and `git diff --check` across all seven campaign repositories — pass.

## 12. GitHub Changes

- Created and pushed public repositories: `kujolang/siteprobe` (`4436189`), `kujolang/searchbridge` (`6995d7d`), `kujolang/contentgraph` (`94e28aa`).
- Modified and pushed: `kujo-agents` (`8c1cc16`), `kujo-skills` (`c1c00df`), `agents.kujolang.ai` (`8374042`, `803c889`).
- Modified: `kujo-workflows` (`0121b77` plus the evidence/report commit containing this file).
- Branches/PRs: direct authorized updates to each repository's `main`; no PRs.
- Deployment: GitHub Pages run `31474529867` completed successfully.

## 13. Known Limitations

- Live third-party modules were not invoked without owner credentials; fixture contracts and missing-capability behavior were verified instead.
- ContentGraph v1 uses deterministic lexical similarity rather than embeddings and marks link proposals for human/context review.
- SiteProbe uses a bounded Python standard-library parsing bridge behind its Kujo entrypoint.
- Four Lens warnings come from its deprecated browser performance entry probe; site console, link, layout, and accessibility error counts are zero.
- Custom WebOps portraits were not supplied, so the documented Kujo logomark fallback is active.

## 14. Remaining Manual Actions

- Supply any optional third-party provider credentials only when live SearchBridge modules are desired.
- Optionally add approved custom WebOps portraits later; this is cosmetic and does not block WebOps operation.
