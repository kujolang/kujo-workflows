# 15 — Platform Priorities

## Scoring method

Scores are research judgments on a 1–5 scale using official API/distribution evidence and current Kujo fit. They guide sequencing, not permanent product commitments.

Dimensions: adoption/audience, API quality, WebOps depth, distribution, architecture diversity, fixture/testability, maintenance cost (5 = lower cost), and strategic fit.

## Tier 1

| Platform | Adopt | API | Depth | Dist. | Diversity | Test | Cost | Fit | Total / 40 | Sequence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Generic static | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 39 | Batch 1 #1 |
| Shopify | 5 | 5 | 5 | 5 | 5 | 5 | 3 | 5 | 38 | Batch 1 #2 |
| Webflow | 4 | 4 | 5 | 5 | 5 | 5 | 4 | 5 | 37 | Batch 1 #3 |
| Vercel | 5 | 5 | 5 | 4 | 5 | 5 | 4 | 5 | 38 | Batch 1 #4 |
| Cloudflare | 5 | 5 | 5 | 3 | 5 | 5 | 3 | 5 | 36 | Batch 1 #5 |
| Netlify | 4 | 5 | 5 | 5 | 3 | 5 | 4 | 5 | 36 | Batch 2 #1 |

Netlify belongs in Tier 1 but not in a five-item batch 1 because Vercel already validates deployment/preview/rollback and Cloudflare adds the more distinct edge/cache layer.

## Tier 2

| Platform | Rationale | Sequence |
| --- | --- | --- |
| Sanity | strong content API, version/perspective model, plugin distribution | Batch 2 #2 |
| Contentful | mature delivery/preview/management separation and enterprise adoption | Batch 2 #3 |
| Astro (thin) | best framework catalog/discovery; generic core behavior | Batch 2 #4 |
| GitHub Pages/Action | portable static CI/distribution; limited provider semantics | Batch 2 #5 |
| Firebase Hosting | preview, REST/CLI deploy, rollback, emulator ecosystem | Batch 2/3 |
| Storyblok | strong content/visual preview and agency audience | Batch 3 |
| DatoCMS | excellent version/restore/test contract, smaller channel | Batch 3 |
| Render | useful deployment/recovery semantics and explicit rollback limits | Batch 3 |

## Tier 3 / wait

- Ghost: capable content API, weaker open discovery.
- AWS Amplify: good API/preview surface, higher IAM/onboarding cost and rollback gap.
- Framer: promising but Server API is open beta and distribution guidance is changing.
- Prismic: read/preview useful; routine general write contract not established beyond migration API.
- Squarespace: generic WebOps plus possible later commerce augmentation; insufficient general site automation.
- Nuxt/SvelteKit/Next.js profiles: implement detection/helpers as needed, not independent platform packages.
- Hugo/Eleventy/Jekyll/Docusaurus: generic-static only.
- Railway/Fly.io: broad application infrastructure, weak early WebOps-specific distribution.
- Remix: generic framework detection later.

## Do not build

- Any duplicated platform workflow directories.
- General Shopify, Webflow, Cloudflare, Vercel, Netlify, or CMS administration surfaces.
- A raw provider-API MCP server marketed as WebOps.
- A mandatory Kujo-hosted OAuth/control plane.
- A separate repository per adapter by default.
- WordPress or Wix platform-specific integration, documentation, scaffold, prioritization, or compatibility architecture.

## First proof and per-adapter cost target

The smallest proof is v2 profile + resolver + generic-static + one read-only Shopify fixture binding running the same weekly-site-health/post-publish preflight without platform branches. After shared contracts exist, a typical read-only adapter should require approximately:

- one manifest;
- 1 identity handler;
- 2–6 Ability bindings;
- 12–20 fixtures;
- conformance declarations/tests;
- one profile template/detector;
- one setup/limitations document;
- one bundle entry.

Expect roughly 1,000–2,500 lines of provider-specific implementation/tests for a narrow read adapter and 2,500–5,000 when safe mutations, OAuth-specific integration, webhooks, and rollback are included. These are planning ranges to validate during batch 1, not quotas.

## Explicit answers to the 45 final questions

1. WebOps today is ten local fixture-first evidence/governance workflows plus tools, skills, roles, dashboard, and receipts.
2. Crawl/health/search normalization/content relationships/browser QA/evaluation/reporting/history are neutral.
3. Source access, one platform scalar, previews, publication, deployment, redirects, cache, credentials, and rollback are specific/hidden.
4. Use compositional profiles + semantic Abilities + adapters; distribute support bundles.
5. Yes, multiple simultaneous adapters are required.
6. Canonical composition layers are framework/content/commerce/deployment/edge/analytics/search.
7. Reuse `kujo.ability/v1`; capability receipt v2 resolves availability.
8. Identity, authoritative source records, previews/deployments, bounded mutations, provider normalization belong in adapters.
9. Search/analytics/performance/backlinks/keywords/indexing normalization remain SearchBridge.
10. Live crawl/headers/metadata/schema/links/site structure remain SiteProbe.
11. Content relationships and recommendations remain ContentGraph.
12. Browser/visual/accessibility verification remains Lens.
13. Orchestration/approval/resume/retry remains Dispatch.
14. Reads are OBSERVE; proposals are local; any provider mutation is ACT.
15. Profiles reference env/keychain/command/OAuth sessions; OAuth remains platform-shell-owned; no secret persistence.
16. Use declared + detected + verified evidence with provenance; heuristics never authorize.
17. Yes, generic static is the base/fallback profile.
18. Astro may need a thin integration; Next.js/Nuxt/SvelteKit need richer profiles/mode detection.
19. Hugo, Eleventy, Jekyll, Docusaurus and static outputs rely on generic support.
20. Shopify uses a narrow versioned GraphQL commerce/content adapter; default reads, scoped ACT, theme writes off.
21. Webflow uses Data API v2 with staged/live distinction and strong publish gates.
22. Cloudflare is edge + optional Pages; granular cache/redirect/deployment; analytics via SearchBridge.
23. Vercel is deployment/preview/log/rollback; not a site inspection replacement.
24. Netlify is Tier 1, first in batch 2 if batch 1 is capped at five.
25. Squarespace should not receive dedicated full support now.
26. Add Sanity and Contentful first, then Storyblok/DatoCMS.
27. Explicit binding wins; ambiguity fails; measurements remain provider-labeled.
28. Dispatch uses payload/target/effect-bound approvals.
29. Rollback is structured mode/scope/exclusions, never a boolean.
30. Adapters use recorded, versioned offline fixtures for all paths.
31. Core conformance plus Ability-specific tests run only when advertised.
32. Use source/Kujo workflow pack/Kennel static packages plus platform-native shells where justified.
33. Agent Plugin exposes outcome semantics and activates only selected skills/tools.
34. MCP projects the same selected Abilities; no duplicate raw capability system.
35. WebMCP remains public, bounded, same-origin, published-only, read-only.
36. Scope skills/MCP tools/metadata by outcome/site and lazy-load mutation schemas.
37. Shopify, Webflow, Vercel, Netlify, Astro/GitHub Actions create the strongest channels; Cloudflare is community/template-led.
38. Batch 1: generic static, Shopify, Webflow, Vercel, Cloudflare.
39. Batch 2: Netlify, Sanity, Contentful, Astro thin integration, GitHub Pages/Action or Firebase.
40. Never build duplicated workflows, general admin/control panels, mandatory SaaS, WordPress, or Wix support.
41. Smallest proof: profile v2/resolver/generic static plus one Shopify read fixture on an unchanged workflow.
42. Target 1k–2.5k lines narrow read adapter, 2.5k–5k safe full adapter; measure after batch 1.
43. Yes, if existing Abilities suffice and conformance/static index accept the adapter.
44. Keep one repo initially, generated/ref-based bundles, independent versions, extraction only for real ownership/distribution need.
45. With no adapter, live URL + optional repo/build output still supports the full generic evidence workflow set.

> **WordPress and Wix are intentionally excluded from Kujo's platform-specific WebOps strategy.**
