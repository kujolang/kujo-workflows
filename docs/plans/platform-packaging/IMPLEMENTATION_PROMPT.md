# Implementation Prompt — Kujo WebOps Platform Packaging

You are implementing the first release of Kujo WebOps platform-aware packaging in `kujolang/kujo-workflows`. Read this entire plan directory before editing. Treat the JSON proposals as normative architecture inputs and `ACCEPTANCE_CRITERIA.md` as the completion contract. Inspect current repository code before changing it, but do not redo platform research or redesign the architecture unless repository evidence proves a material contradiction; document any such contradiction before proceeding.

## Objective

Turn the existing ten platform-neutral WebOps workflows into a compositional, capability-driven system without copying workflows. Users install a narrow platform support bundle; workflows invoke portable semantic Abilities; a deterministic resolver selects one explicitly configured provider adapter; Dispatch governs ACT; existing Kujo tools retain ownership.

The final runtime path is:

```text
existing WebOps workflow
  -> required `kujo.ability/v1` semantic operation
  -> `webops.site-profile/v2` binding resolver
  -> thin provider adapter
  -> platform API/local repository/build artifact
  -> normalized evidence/effect receipt
  -> Eval/SiteProbe/Lens verification + RunLedger correlation
```

Do not create `shopify-weekly-site-health`, `webflow-post-publish`, or any equivalent provider copy.

## Required architecture

1. Extend `webops.site-profile/v1` to one canonical v2 with optional arrays for `framework`, `content`, `commerce`, `deployment`, `edge`, `analytics`, and `search`; explicit Ability bindings; declared/detected/verified provenance; structured credential references; and mutation policies.
2. Preserve v1 reading. Migration produces a deterministic proposal and never overwrites by default.
3. Use canonical `kujo.ability/v1` for semantic operations. Do not invent a parallel generic capability schema. Extend the existing capability receipt to report binding availability.
4. Create a narrow adapter manifest and invocation/receipt protocol matching `PLATFORM_ADAPTER_CONTRACT_PROPOSAL.json`.
5. Keep authentication, runtime binding, provider resource identity, authorization/approval, exposure, transport, and handler code outside Ability definitions.
6. Permit multiple adapters per site. Explicit binding wins; one verified provider may satisfy an OBSERVE request; ambiguous mutation fails closed; provider measurements remain labeled through SearchBridge.
7. Keep generic URL/static WebOps first-class when no adapter exists.

## Batch 1

Implement in this order:

1. generic static-site profile/local adapter;
2. Shopify hosted commerce/content adapter;
3. Webflow hosted visual CMS adapter;
4. Vercel deployment adapter;
5. Cloudflare edge plus optional Pages deployment adapter.

Netlify is Tier 1 but begins batch 2. Batch 2 continues with Sanity, Contentful, Astro thin integration, and GitHub Pages Action or Firebase Hosting.

## Ability catalog

Start with only operations in `CAPABILITY_MATRIX.json`. Reads/identity/preview resolution are OBSERVE. PROPOSE is local artifact generation and never invokes a provider mutation. Every provider mutation—including remote draft writes, webhook registration, deployment trigger, promotion, rollback, redirect/header change, or cache purge—is ACT.

Do not add provider CRUD unless an existing WebOps workflow consumes it. Add a new provider by binding existing Abilities; add a new Ability only through core review.

## Ownership

- SearchBridge: normalized search, analytics, PageSpeed/CrUX, backlinks, keywords, URL inspection/submission, and provider-native measurements.
- SiteProbe: live crawl, headers, metadata, schema, links, robots/sitemap, status/site structure.
- ContentGraph: content relationships/scoring.
- Lens: browser/visual/accessibility checks; adapters supply preview URLs/access metadata.
- Dispatch: workflow DAG, approval, resume, retry/reconciliation, compensation.
- RunLedger: correlated run/action receipts; no adapter-specific ledger.
- Eval: outcome verification.
- Howl: distribution assets.
- Spec: task/change contract.

## File ownership and layout

Keep batch-1 implementation in this repository under a coherent `webops/` core/adapters/bundles/fixtures/conformance/commands layout. Preserve existing top-level workflow directories and generator ownership. Update generated artifacts through their generator. Do not modify sibling repositories unless a separately approved phase explicitly requires it; if a canonical Ability/Agents SDK/Dispatch change is necessary, stop with a precise cross-repository change request rather than duplicating its contract here.

## Migration sequence

Follow `IMPLEMENTATION_PLAN.md` phases in order. First capture baseline executable truth and label invoked versus synthesized steps. Then profile v2, Ability/adapter contracts, fixture conformance, generic static, provider adapters, workflow/Dispatch integration, packaging/agent/MCP integration, and clean-machine proof. Make small meaningful commits with tests passing at each boundary.

## Adapter requirements

Each adapter must provide manifest, identity inspection, exact Ability bindings, auth/scope declaration, resource schema, error normalization, pagination/rate metadata, bounded result/effect receipts, rollback descriptor, fixtures, and conformance declaration. It may normalize provider data but must not reason about SEO/content strategy, orchestrate, evaluate, report, build content graphs, or run browser QA.

Provider details:

- Shopify: versioned GraphQL Admin API; normalize HTTP-level errors, GraphQL errors, `userErrors`, cursors, GIDs, query cost/throttle, bulk async state; no orders/customers; theme writes disabled; ShopifyQL only through SearchBridge.
- Webflow: Data API v2; token kind; staged/live state; staged writes are ACT; item/page/site publish separated; schedule unsupported; one-publish-per-minute and full-site blast radius.
- Vercel: exact team/project; deployment/preview/protection/log bounds; promotion/rollback scope and plan limits; no secret/DNS/firewall/general platform admin.
- Cloudflare: exact account/zone/project; separate edge and Pages roles; URL/tag/all cache purge are distinct; rule precedence; analytics through SearchBridge; no WAF/DNS/general Cloudflare control panel.
- Generic static: bounded repository/build artifacts, routes/assets/source hints/local preview; framework profiles/detectors only; deployment separate.

## Security rules

Credentials never appear in profiles or persisted artifacts. Resolve a referenced secret immediately before invocation and redact structurally before persistence. Prefer least-privilege resource-scoped read tokens. Platform OAuth shells own consent/refresh/rotation and remain optional; local custom-token paths must work.

Before ACT, the host verifies run permission, role maximum, Ability effect/version/digest, installed adapter, declared+verified resource identity, exact domains/resources, credential scope, payload-bound approval, budgets, idempotency, and recovery. Recheck identity immediately before the effect. A changed target/input invalidates approval. Never blindly retry an uncertain mutation.

Rollback is a structured object with mode, coverage, exclusions, target reference, approval requirement, and recovery instructions. Do not promise provider-native rollback for content or external state. Cache full purge is disabled by default. Webhooks never directly mutate; verified events may enqueue Dispatch.

MCP projects only selected Abilities through the same resolver/gateway/receipt path. Default exposure is OBSERVE and at most 12 tools. WebMCP remains same-origin, public, published-only, bounded, read-only.

## Testing

Build the adapter and bundle conformance described in `12-testing-and-conformance.md`. Normal CI is offline. Required fixtures cover identity match/mismatch, empty/pagination, auth/scope, 429/query cost, provider 5xx, contract drift, async/partial, mutation success/validation/uncertainty, redaction, and webhook trust/replay where supported. Capability-specific tests run only when advertised; no advertised mutation may lack mutation/recovery tests.

Add typed workflow inputs for published resource, content target, finding ID, query suite, previous/baseline, and deployment receipt. Assert actual invocation and provenance, not only a successful final receipt. Existing fixture/resume/stable-ID/dashboard tests and release gates must remain green.

## Performance and context budgets

Use `13-performance-token-budget.md` as the initial budget. In particular: resolver p95 <= 50 ms for 20 instances/50 Abilities; profile/detection plan p95 <= 100 ms without build/network; startup overhead <= 150 ms and <= 5% of baseline median; default <= 12 active skills and <= 12 MCP tools; adapter manifest <= 32 KiB; agent-visible adapter metadata <= 4 KiB/provider/run. Measure before revising.

## Packaging and onboarding

Use one repository and generated/ref-based support bundles. A bundle references adapters, profile templates, detectors, existing workflows/presets, selected skills/roles, SearchBridge defaults, fixtures, docs, and compatibility versions. Near-term delivery is source/Kujo workflow pack/Kennel local or static index plus strict ecosystem release manifest. Do not claim public Kennel registry/remote install capability that does not exist.

Provide namespaced `init`, `detect`, `doctor`, `run`, and `list` through the audited workflow-pack mechanism or a safer equivalent. `init` proposes a v2 profile; `doctor` works credential-free in fixture mode; neither grants ACT. External workflow-pack `--allow-all` is not acceptable for platform mutations—fix/wrap that boundary before ACT release.

## Clean-machine and release criteria

From a tracked archive and exact pinned release manifest, install to a temporary user-owned prefix, run bundle install, doctor, offline generic/static and each provider fixture workflow, validate artifacts, deactivate/uninstall, and prove no undeclared sibling checkout/cache is required. Preserve profiles/evidence on uninstall. Live smoke is optional, read-only by default, and separately reported.

The release is complete only when `ACCEPTANCE_CRITERIA.md` passes, JSON/schema/doc links validate, existing and new gates pass, performance/context budgets are measured, and the working tree is clean. State limitations and distribution channel status precisely.

## Absolute exclusion

Do not research, design, scaffold, document, prioritize, or preserve platform-specific architecture for WordPress or Wix. They may appear only in the required exclusion statement:

> **WordPress and Wix are intentionally excluded from Kujo's platform-specific WebOps strategy.**
