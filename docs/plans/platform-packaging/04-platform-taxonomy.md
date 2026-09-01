# 04 — Platform Taxonomy

## Canonical layers

```text
site identity (URL/domain + repository)
  ├── framework[]    build/render/runtime semantics
  ├── content[]      source records, drafts, versions, publication
  ├── commerce[]     products/collections/commerce-native content
  ├── deployment[]   projects, builds, previews, promotion, rollback
  ├── edge[]         cache, edge routing/headers, edge traffic evidence
  ├── analytics[]    normalized measurement providers
  └── search[]       normalized search/indexing providers
```

Arrays are required because migrations, multi-brand sites, multiple analytics sources, or split subtrees may use more than one provider in a layer.

## Terms and responsibilities

| Term | Meaning | Owns behavior? |
| --- | --- | --- |
| Site profile | Declared, detected, and verified composition plus policy references | identity and binding intent, not execution |
| Ability | Portable semantic operation (`content.read`, `deployment.inspect`) with schemas/effects/idempotency | meaning only |
| Platform adapter | Thin binding from Ability to provider API/local artifact | provider translation only |
| Binding resolver | Deterministically selects an adapter instance for an Ability | conflict/precedence and availability |
| Platform support bundle | Install/distribution unit containing selected adapter/profile/detector/fixtures/docs/skills | onboarding, not workflow logic |
| Workflow preset | Outcome-oriented defaults for existing workflows | configuration only |
| Workflow | Multi-step WebOps orchestration and reasoning | WebOps core/Dispatch |

## Why not one generic platform adapter

One universal adapter would either expose an unbounded cloud/CMS API or collapse different effect semantics. `content.publish`, `deployment.promote`, and `cache.purge.urls` have different targets, authorization, retry, and recovery rules. Reuse the same adapter manifest and conformance protocol, but bind small provider-specific handlers by layer.

## Why not platform profiles alone

Profiles solve configuration and discovery but cannot normalize API errors, pagination, rate limits, receipts, or effects. They must point to adapter bindings.

## Why not platform packs as the architecture

Kujo already uses “workflow pack” for CLI extension packaging. A monolithic Shopify pack would conflate product installation, semantic operations, provider bindings, skills, and workflows. The architecture is abilities + adapters + composition; the user-facing installation artifact is a support bundle that may use a Kujo workflow pack as one delivery mechanism.

## Framework taxonomy

- **Static-output frameworks:** Astro static, Hugo, Eleventy, Jekyll, Docusaurus, and static modes of Next.js/Nuxt/SvelteKit use the generic-static base.
- **Multi-runtime frameworks:** Next.js, Nuxt, SvelteKit, Remix require a detected output/runtime profile because route and deployment behavior changes by mode.
- **Provider deployment adapters:** “adapter” already has framework-specific meanings in Astro/Next.js/SvelteKit. Documentation should say “Kujo framework profile” to avoid collision.

## Platform-specific workflow exception rule

A distinct workflow is allowed only when the sequence, approvals, and evidence are intrinsically provider-specific and cannot be expressed as optional Ability steps. No batch-1 case meets that threshold. Shopify theme review and Webflow full-site publishing are adapter/preset concerns, not new workflow families.
