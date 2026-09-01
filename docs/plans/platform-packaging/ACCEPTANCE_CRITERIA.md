# Acceptance Criteria

## Architecture

- [ ] One canonical `webops.site-profile/v2` composes zero or more framework/content/commerce/deployment/edge/analytics/search instances.
- [ ] v1 profiles remain readable and migrate to a proposal without overwriting source by default.
- [ ] Semantic platform operations validate as canonical `kujo.ability/v1` definitions.
- [ ] Adapter bindings, policy, credentials, exposure, and transport remain outside Ability definitions.
- [ ] Existing workflows request semantic Abilities and contain no provider-name conditionals.
- [ ] Multiple adapters per site are supported; ambiguous mutations fail closed.
- [ ] Generic URL/static operation passes with zero remote adapter.

## Effects and security

- [ ] Provider reads are OBSERVE; local change plans are PROPOSE; every provider mutation is ACT.
- [ ] Remote draft creation/update is ACT.
- [ ] Credentials and profiles never authorize ACT.
- [ ] ACT requires exact target, payload digest, non-expired approval, role/run permission, scope, and identity recheck.
- [ ] Secret values never appear in profile, manifests, logs, errors, evidence, receipts, fixtures, or dashboard DB.
- [ ] SSRF, wrong-target, scope denial, rate limit, timeout, uncertain mutation, redirect loop, and cache-blast-radius tests pass.
- [ ] Rollback is structured with mode/covers/excludes and never represented as a universal boolean.

## Ownership

- [ ] SearchBridge remains the normalized search/analytics/performance/backlink/indexing boundary.
- [ ] SiteProbe remains the live crawl/HTML/header/metadata/schema/link boundary.
- [ ] ContentGraph remains relationship/scoring owner.
- [ ] Lens receives preview URLs and remains visual/browser verification owner.
- [ ] Dispatch owns orchestration, approvals, retry/resume, and compensation.
- [ ] RunLedger correlates runs/actions; adapters do not create a competing ledger.
- [ ] Eval verifies outcomes; Howl remains asset/distribution generation owner.

## Adapter conformance

- [ ] Manifest, identity, Ability mapping, auth reference, pagination, rate, error, redaction, output bounds, receipts, fixtures, and versions pass core conformance.
- [ ] Every advertised mutation has permission-denial, approval, idempotency, success, failure, uncertainty, and recovery fixtures.
- [ ] Capability-specific tests run only when advertised.
- [ ] A third-party fixture adapter installs and passes without core source changes.

## Support-bundle conformance

- [ ] Bundle installation, detection, profile proposal, doctor, workflow compatibility, skill selection, evidence output, deactivation, and removal pass from a tracked archive.
- [ ] Removal preserves user profiles and evidence unless explicitly asked to delete them.
- [ ] Outcome presets activate at most 12 skills and 12 MCP tools by default.
- [ ] Installing five bundles stays within startup/context/evidence budgets.
- [ ] No support bundle copies an existing WebOps workflow directory.

## Batch 1

- [ ] Generic static supports plain HTML and at least Astro/Hugo/Eleventy/Jekyll/Docusaurus fixture outputs plus static modes of Next.js/Nuxt/SvelteKit.
- [ ] Shopify supports verified identity and bounded fixture reads for products/collections/pages/articles/redirects; mutations remain off until ACT conformance passes.
- [ ] Webflow supports identity, CMS/page metadata reads, staged/live distinction, and safe publish preflight fixtures.
- [ ] Vercel supports project/deployment/preview inspection and rollback scope fixtures.
- [ ] Cloudflare supports zone/Pages inspection and granular cache-purge permission fixtures; analytics routes through SearchBridge.

## Verification and release

- [ ] All JSON validates and examples match schemas.
- [ ] Existing WebOps fixture/resume/stable-ID/dashboard tests still pass.
- [ ] Repository release-readiness and clean-checkout gates pass.
- [ ] Clean-machine install/doctor/offline run/uninstall proof passes from exact pinned artifacts.
- [ ] Live provider tests are optional, separately reported, least-privilege, bounded, and never prerequisites for fixture CI.
- [ ] API version/deprecation capture and scheduled drift workflow are documented and tested with fixtures.
- [ ] The final release states: “WordPress and Wix are intentionally excluded from Kujo's platform-specific WebOps strategy.”
