# Dependency-Ordered Implementation Plan

## Phase 0 — Baseline and executable-truth correction

**Goal:** preserve an immutable current proof and stop overstating placeholder tool execution.
**Files:** current workflow manifests/generator, harness tests, baseline evidence under a reviewed plan fixture location.
**Reuse:** existing ten workflows, fixture site, state/findings/receipts, release gates.
**New:** baseline manifest with digests/timings/bytes; explicit `execution_kind: invoked|synthesized` in step receipts.
**Tests:** current fixture/resume/no-live-substitution/dashboard imports; baseline comparison.
**Security:** no live provider; no changed effects.
**Benchmarks:** current startup/evidence/skill footprint.
**Exit:** all existing gates pass and every receipt truthfully states whether a tool ran.

## Phase 1 — Site profile v2 and migration

**Goal:** represent compositional sites without breaking v1.
**Files:** `contracts/webops/site-profile.v2.schema.json`, profile examples/migrator/validator, dashboard migration/import view, skills/docs.
**Reuse:** v1 identity/integrations/permissions/credential references and Agency mapping rule.
**New:** typed composition instances, bindings, provenance/detection, structured credential references, policies.
**Tests/fixtures:** zero-layer generic, Shopify+Vercel+Cloudflare, Sanity+Next.js+Vercel, split-route, ambiguous, invalid secret, v1 migration.
**Security:** detected never authorizes; no secret values; safe repository paths.
**Benchmarks:** parse/migrate/detect plan <= budgets.
**Exit:** v1/v2 accepted, round-trips deterministic, dashboard imports both, original v1 remains unchanged by default.

## Phase 2 — Ability catalog, adapter manifest, resolver, receipts

**Goal:** create the semantic/provider boundary.
**Files:** `webops/core/abilities`, adapter/profile/binding/receipt schemas, resolver, CLI JSON outputs.
**Reuse:** canonical Ability package, Agents SDK projection/gateway patterns, current capability receipt, SearchBridge adapter/error patterns.
**New:** approved WebOps Ability catalog, adapter manifest v1, availability receipt v2, invocation/ACT/recovery receipts, deterministic conflict rules.
**Tests:** schema/definition digests, zero/one/multiple binding, explicit preference, route conflict, version incompatibility.
**Security:** policy/binding/credentials separate; effect classes preserved.
**Benchmarks:** 20 instances/50 Abilities resolution <= 50 ms p95.
**Exit:** a fixture adapter binds existing Abilities and resolves without provider-specific core code.

## Phase 3 — Fixture-first conformance and credential providers

**Goal:** make third-party adapters safe and testable offline.
**Files:** `webops/conformance`, fixture schemas/runner, credential-reference interface, redaction/error modules.
**Reuse:** current Python unittest/release gates, SearchBridge fixtures, Ability/Agents SDK validation.
**New:** conformance CLI/suite, env and bounded command credential providers, fixture provenance, async/idempotency harness.
**Tests:** full list in `12-testing-and-conformance.md`; malicious adapters/fixtures.
**Security:** no code execution during discovery/install; exact endpoint allowlist; output/call/time budgets.
**Benchmarks:** adapter discovery and fixture suite duration/bytes.
**Exit:** reference and intentionally broken third-party adapters produce deterministic pass/fail reports.

## Phase 4 — Generic static-site base

**Goal:** prove useful zero-account WebOps and framework-neutral reuse.
**Files:** `adapters/generic-static`, detectors/framework profiles, bundle/static, fixture sites.
**Reuse:** SiteProbe, ContentGraph source adapters, Lens, SSG output validation, repository tooling.
**New:** bounded route/asset/build-output inventory, source-location hints, preview/local-server contract, generic static bundle/doctor.
**Tests:** plain HTML, Astro, Hugo, Eleventy, Jekyll, Docusaurus, Next/Nuxt/Svelte static outputs; no repo path traversal; optional build denied/allowed.
**Security:** builds/processes require explicit host effects; source patches are PROPOSE until approved.
**Benchmarks:** small/medium/large trees and workflow overhead.
**Exit:** unchanged weekly-site-health/post-publish preflight runs through generic semantic bindings with no platform name branch.

## Phase 5 — Shopify hosted commerce/content adapter

**Goal:** validate versioned GraphQL, scopes, pagination/cost, hosted content, and public-distribution potential.
**Files:** adapter/bundle/profile/detector/fixtures/docs; optional SearchBridge ShopifyQL provider separately.
**Reuse:** Ability/resolver/conformance, SearchBridge normalized measurement boundary.
**New:** identity; product/collection/page/article/redirect reads; theme/preview metadata where safe; ACT handlers only after read proof.
**Tests:** GraphQL errors/userErrors/cursors/throttle/version drift/scope denial/async bulk; wrong shop; theme-scope disabled.
**Security:** minimum scopes; no orders/customers; theme writes off; resource-bound approvals.
**Benchmarks:** records/calls/query cost/output.
**Exit:** fixture and least-privilege optional read smoke pass; content ACT remains feature-gated until mutation/recovery acceptance passes.

## Phase 6 — Webflow hosted visual CMS adapter

**Goal:** validate staged/live state, page metadata, narrow publish, and agency onboarding.
**Files:** adapter/bundle/profile/fixtures/docs.
**Reuse:** same content/metadata/publish Abilities and Lens preview path.
**New:** token-type identity, CMS/page reads, staged write and item/page/site publish bindings, webhook declaration.
**Tests:** pagination, 60/120 rpm and publish 1/min, staging, unsupported schedule, site-wide blast-radius preflight, no rollback claim.
**Security:** staged writes ACT; full-site publish stronger approval.
**Benchmarks:** serialized rate-limited reads and evidence size.
**Exit:** same content-refresh/post-publish workflows operate through Webflow bindings without copies.

## Phase 7 — Vercel and Cloudflare composition

**Goal:** prove deployment + edge adapters on the same site.
**Files:** two adapters/bundles, shared deployment/cache receipts, SearchBridge Cloudflare measurement binding, preview-to-Lens integration.
**Reuse:** Dispatch, Lens, Eval, SearchBridge, resolver.
**New:** Vercel project/deploy/preview/log/rollback; Cloudflare zone/Pages/preview/cache/redirect reads and gated writes.
**Tests:** multi-team/zone mismatch, protected preview, async deploy, plan-limited rollback, next auto-deploy, granular/full purge, rule precedence.
**Security:** secrets excluded, exact domain/project/zone, full purge separate.
**Benchmarks:** bounded logs/analytics/calls.
**Exit:** Sanity/Next-like fixture composition can select Vercel preview and Cloudflare cache independently, with explicit conflict behavior.

## Phase 8 — Workflow, Dispatch, Eval, RunLedger integration

**Goal:** replace semantic placeholders with real governed steps.
**Files:** typed workflow input schemas, generator/manifests, Dispatch workflow definitions, dashboard, run receipt correlations.
**Reuse:** all current workflow identities/artifacts/finding history.
**New:** resource inputs, capability requirements, real tool/Ability calls, approval/resume/verification/compensation, RunLedger refs.
**Tests:** all ten workflows; permission matrix; interruption/resume; failure/unknown/rollback; dashboard import.
**Security:** no hidden ACT; payload-bound approvals.
**Benchmarks:** startup and packet budgets against baseline.
**Exit:** every declared executable step either runs or explicitly degrades; no synthesized success masquerades as tool proof.

## Phase 9 — Bundles, agents, skills, MCP/WebMCP

**Goal:** deliver simple platform/outcome onboarding with small context.
**Files:** support-bundle manifests/generator, workflow pack commands, selected skill/role manifests, MCP projection filters, docs.
**Reuse:** Kujo workflow packs, Kennel/source locks, Agent packages, Ability MCP projection, CMS/SSG WebMCP precedent.
**New:** `init/detect/doctor/run/list`, activation manifests, filtered agent/MCP registry.
**Tests:** install/deactivate/uninstall, default <=12 skills/tools, write-MCP denial, WebMCP public-only.
**Security:** external workflow-pack `--allow-all` must be fixed or commands wrapped in a least-privilege host before ACT release.
**Benchmarks:** token/tool/metadata footprints and five-bundle startup.
**Exit:** platform user reaches first fixture health result without knowing internal repositories.

## Phase 10 — Clean machine and release/distribution

**Goal:** prove the supported local product and prepare external channels.
**Files:** exact release manifest, installer/doctor docs, clean-machine harness, API drift automation, release metadata, channel-specific shells only after proof.
**Reuse:** ecosystem installer strict refs, clean-checkout/release-readiness gates.
**New:** support-bundle release catalog/static index, compatibility matrix, opt-in smoke workflow, distribution checklists.
**Tests:** tracked archive, temporary prefix, offline first run, deactivation/uninstall, unsupported API warnings.
**Security:** checksums/digests, no live credentials in CI, read-only smoke default.
**Benchmarks:** install size/time, doctor time, first-run/context/packet size.
**Exit:** pinned clean-machine proof passes; release claims remain limited to verified channels; no mandatory hosted service.

## Phase 11 — Batch 2

Implement Netlify, Sanity, Contentful, Astro thin integration, and GitHub Pages Action or Firebase Hosting in that order. Each reuses existing Abilities; any proposed new Ability must demonstrate a workflow consumer and pass architecture review.
