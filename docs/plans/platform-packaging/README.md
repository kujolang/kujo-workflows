# Kujo WebOps Platform Packaging

Status: architecture and implementation handoff, researched 2026-09-01
Audience: Kujo maintainers and the implementation agent
Decision horizon: batch 1 and batch 2 of platform-aware WebOps packaging

> **WordPress and Wix are intentionally excluded from Kujo's platform-specific WebOps strategy.**

## Executive decision

Kujo WebOps should not become a family of duplicated platform workflows. It should become a platform-neutral WebOps core with:

1. an additive, compositional `webops.site-profile/v2`;
2. WebOps semantic operations expressed as existing `kujo.ability/v1` definitions;
3. thin provider bindings called **platform adapters**;
4. deterministic detection and binding resolution;
5. user-facing **platform support bundles** that install only the adapter, detector/profile template, fixtures, narrow skills, workflow presets, and documentation needed for the selected outcome.

The runtime path is:

```text
WebOps workflow
  -> required semantic Ability
  -> site-profile binding resolver
  -> one explicitly selected platform adapter
  -> provider API or local repository/build artifact
```

The product path is:

```text
"Kujo WebOps for Shopify"
  -> Shopify support bundle
  -> Shopify commerce/content adapter + profile detector + fixtures
  -> unchanged WebOps workflows
```

`PROPOSE` does not call provider mutations. Any provider-side change, including creating a remote draft, is `ACT`. A profile or credential never grants authority.

## Recommended batches

Batch 1 proves the architecture with five integrations:

1. **Generic static sites** — first and canonical fallback; validates no-account, repository/build-output, and unknown-host operation.
2. **Shopify** — hosted commerce/CMS, OAuth/scopes, versioned GraphQL, rich content, redirects, webhooks, and high distribution value.
3. **Webflow** — hosted visual CMS, staged/live publishing, page metadata, OAuth/site tokens, and high agency value.
4. **Vercel** — deployment/preview/log/rollback adapter with a strong developer distribution path.
5. **Cloudflare** — edge/cache/analytics plus Pages deployment; validates composition with a separate edge provider.

Netlify is Tier 1 but should be the first batch-2 implementation if batch 1 is capped at five. Sanity and Contentful follow as composable headless-content providers. Astro receives a thin framework profile/integration, not a second workflow implementation.

## What the package contains

- [Current architecture](01-current-webops-architecture.md)
- [Neutral versus specific behavior](02-platform-neutral-vs-specific.md)
- [Platform landscape](03-platform-landscape.md)
- [Taxonomy](04-platform-taxonomy.md)
- [Site composition model](05-site-composition-model.md)
- [Capability/Ability model](06-capability-model.md)
- [Adapter contract](07-platform-adapter-contract.md)
- [Packaging architecture](08-packaging-architecture.md)
- [Platform deep dives](09-platform-deep-dives.md)
- [Security and effects](10-security-and-effects.md)
- [Agent, MCP, and WebMCP](11-agent-mcp-integration.md)
- [Testing and conformance](12-testing-and-conformance.md)
- [Performance and token budget](13-performance-token-budget.md)
- [Distribution analysis](14-distribution-analysis.md)
- [Platform priorities](15-platform-priorities.md)
- [Risk register](RISK_REGISTER.md)
- [Acceptance criteria](ACCEPTANCE_CRITERIA.md)
- [Dependency-ordered implementation plan](IMPLEMENTATION_PLAN.md)
- [Implementation-agent prompt](IMPLEMENTATION_PROMPT.md)
- Machine-readable [platform matrix](PLATFORM_MATRIX.json), [capability matrix](CAPABILITY_MATRIX.json), [adapter proposal](PLATFORM_ADAPTER_CONTRACT_PROPOSAL.json), and [site profile proposal](SITE_PROFILE_PROPOSAL.json)
- [Source ledger](SOURCES.md)

## Smallest architecture proof

Implement `webops.site-profile/v2`, the resolver, seven read-only static-site Abilities, a `generic-static` local adapter, detector provenance, offline fixtures, and one unchanged `webops-weekly-site-health` fixture run. The proof passes only if the same workflow runs with no platform-name branch and emits a v2 binding receipt. Then add one Shopify read-only fixture binding to prove third-party extensibility without editing the workflow.

## Governing non-goals

WebOps is not a provider control panel, deployment orchestrator, generic CMS SDK, all-in-one SEO SaaS, or mandatory hosted service. Platform support is an enhancement; generic WebOps remains first-class when no adapter exists.
