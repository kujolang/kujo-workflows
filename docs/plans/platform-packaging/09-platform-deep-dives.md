# 09 — Platform Deep Dives

## Shopify

Official evidence: [GraphQL Admin API](https://shopify.dev/docs/api/admin-graphql/latest), [API limits](https://shopify.dev/docs/api/usage/limits), [API versioning](https://shopify.dev/docs/api/usage/versioning), [authentication and authorization](https://shopify.dev/docs/apps/build/authentication-authorization), [app distribution](https://shopify.dev/docs/apps/launch/distribution), and [App Store requirements](https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements).

Use the versioned GraphQL Admin API; REST Admin is legacy and new public apps must use GraphQL. Pin the quarterly API version in the binding and every receipt. Normalize GraphQL HTTP-success errors, mutation `userErrors`, connection pagination, query cost/throttle state, GIDs, bulk-operation async state, and the 25,000-count ceiling.

WebOps scope:

- OBSERVE products, collections, pages, blogs/articles, metafields relevant to presentation, redirects, theme identity/files only when specifically authorized, publication state, and webhooks.
- ACT bounded content/SEO field writes, redirect changes, publication, and webhooks. Theme-file writes default off; public App Store apps face protected scope/exemption and should prefer theme app extensions.
- Keep orders, customers, discounts, inventory, general store administration, and broad theme administration out of core WebOps.
- Treat ShopifyQL as optional commerce-native measurement routed through SearchBridge; it is not generic analytics and may require `read_reports` and protected-data approval.

Authentication supports merchant-approved scopes, token exchange/auth-code grant, online/offline/delegate tokens, and organization-owned client credentials. Initial local support should accept a custom/offline token reference with least scopes. Public App Store distribution is a later shell because review, embedded UI, compliance webhooks, token lifecycle, and ongoing quality requirements materially expand scope.

Robots and sitemaps are largely platform-generated constraints; inspect live output through SiteProbe and propose supported theme/config changes only. Theme preview URLs can feed Lens. Rollback is resource-specific: theme/version/Git paths may help, but content mutations use captured before-state and compensating writes.

## Webflow

Official evidence: [Data API authentication](https://developers.webflow.com/data/reference/authentication), [CMS publishing](https://developers.webflow.com/data/docs/working-with-the-cms/publishing), [site publishing](https://developers.webflow.com/data/reference/sites/publish/), [rate limits](https://developers.webflow.com/data/reference/rate-limits), [webhooks](https://developers.webflow.com/data/docs/working-with-webhooks), and [Marketplace overview](https://developers.webflow.com/data-beta/docs/marketplace/overview).

Use Data API v2 only; beta capabilities are explicitly experimental. Support single-site tokens for local/internal use, read-only workspace tokens for audits, and OAuth for public/multi-site integration. Record token type and site/workspace identity.

WebOps scope:

- OBSERVE sites/domains, pages, page SEO/OpenGraph metadata, static page content, collections/items, staged/live state, assets, publish history, and supported webhooks.
- ACT CMS draft/staged writes, item publish/unpublish, page/site publish, page metadata/content writes where officially supported, and webhook registration.
- Scheduled publishing is unsupported through the CMS API; do not claim it.
- Staged writes are ACT because they mutate provider state even before public publication.

General limits are plan-dependent (commonly 60 or 120 requests/minute) and publish is limited to one successful queue per minute. Respect `Retry-After`; prefer webhooks to polling. Site-wide publish can release multiple staged changes and therefore requires a preflight inventory plus a stronger, payload-bound approval. Lens should use Webflow staging/page preview when identity and access are verified. No general provider-native rollback was established; use unpublish/compensating write/manual recovery honestly.

## Cloudflare

Official evidence: [API token guidance](https://developers.cloudflare.com/api/overview/), [cache purge API](https://developers.cloudflare.com/api/resources/cache/methods/purge/), [Pages previews](https://developers.cloudflare.com/pages/configuration/preview-deployments/), [Pages rollbacks](https://developers.cloudflare.com/pages/configuration/rollbacks/), [GraphQL Analytics API](https://developers.cloudflare.com/analytics/graphql-api/), and [URL forwarding](https://developers.cloudflare.com/rules/url-forwarding/).

Model Cloudflare primarily as an edge layer and optionally as a Pages deployment layer. Use resource-scoped API tokens rather than global keys.

WebOps scope:

- OBSERVE zone/project identity, Pages deployments/aliases, preview URLs, build state, relevant edge routing/header configuration, and aggregated HTTP/Web Analytics via SearchBridge.
- ACT Pages deployment trigger/promotion/rollback where the API/CLI supports it, bounded redirect/header rules, and cache purge.
- Split `cache.purge.urls`, `cache.purge.tags`, and `cache.purge.all`; never allow URL purge authority to imply full-zone purge.
- Do not expose DNS, WAF, Zero Trust, Workers administration, bot management, load balancing, or general infrastructure controls as WebOps.

Pages preview deployments have stable URLs and default `X-Robots-Tag: noindex`, which should be verified before Lens runs. Pages rollback supports successful production deployments, not preview targets. Edge redirects have product execution-order/precedence and plan limits; adapter receipts must capture rule product, phase, list/ruleset, and ordering impact. Cloudflare GraphQL analytics belongs behind a SearchBridge provider binding. Current official distribution favors templates, GitHub, Wrangler, and framework guides; an open integration marketplace submission path is not established.

## Vercel

Official evidence: [REST API](https://vercel.com/docs/rest-api), [deployments](https://vercel.com/docs/deployments/overview), [production rollback](https://vercel.com/docs/deployments/rollback-production-deployment), [webhooks](https://vercel.com/docs/webhooks), [integration creation](https://vercel.com/docs/integrations/create-integration), and [public listing requirements](https://vercel.com/docs/integrations/submit-integration).

Use bearer/OAuth integration tokens with exact team/project identity. The REST API exposes projects, deployments/events, domains, routes, bulk redirects, cache, webhooks, and related resources, with rate state in response headers.

WebOps scope:

- OBSERVE projects/domains, deployments, commit/source metadata, preview URLs/protection, build/runtime logs within budget, routes/redirects, and environment names without secret values.
- ACT deployment trigger, preview promotion, deployment rollback, bounded project-level redirect/route changes, and webhooks/checks.
- Keep general environment-secret management, DNS, firewall, billing, storage provisioning, and marketplace resource administration out of WebOps.

Every deployment has a unique URL; this is a high-value `preview.resolve` source for Lens/Eval. Rollback repoints traffic without a rebuild, but plan limits differ and rollback does not imply database/config/secret recovery. Receipts enumerate scope. A connectable-account integration is a plausible later channel, but community integrations are shareable before public marketplace listing; current documentation requires substantial active installs and review for public listing.

## Netlify

Official evidence: [API authentication and rate limits](https://docs.netlify.com/api-and-cli-guides/api-guides/get-started-with-api/), [Deploy Previews](https://docs.netlify.com/deploy/deploy-types/deploy-previews/), [deploy creation](https://docs.netlify.com/deploy/create-deploys/), and [Build Plugin development/distribution](https://docs.netlify.com/extend/develop-and-share/develop-build-plugins/).

Netlify qualifies as Tier 1, sequenced immediately after the capped five-integration first wave. PATs suit local scripts; OAuth2 is required for public integrations. General documented rate limits and stricter deploy limits make call budgets mandatory.

Support deploy/project identity, deploy list/inspect, draft/Deploy Preview resolution, build hooks, atomic rollback, normalized redirect/header configuration, and webhooks. Build-hook URLs are secrets. Old/preview deploys use `noindex` protections that WebOps should verify. Rollback republishes a previous deploy but may be overwritten by later Git auto-publish. Netlify Build Plugins offer an excellent optional npm/UI distribution shell, but adapter semantics stay local/API-driven. Do not advertise analytics/log reads until exact API and plan boundaries are verified.

## Squarespace

Official evidence: [read-only Website API scope](https://developers.squarespace.com/commerce-apis/website-overview), [authentication and permissions](https://developers.squarespace.com/commerce-apis/authentication-and-permissions), [OAuth](https://developers.squarespace.com/commerce-apis/oauth), and [rate limits](https://developers.squarespace.com/commerce-apis/rate-limits).

Do not build a dedicated full WebOps adapter in batch 1 or 2. Official APIs are commerce-centric. The Website API is read-only and does not expose general non-commerce page layout/design configuration; commerce APIs cover products, inventory, orders, contacts, discounts, transactions, and webhooks.

Generic SiteProbe/Lens/SearchBridge WebOps already provides site health. A later optional `squarespace-commerce` content augmentation could read product SEO fields and, with explicit ACT, make bounded product updates. OAuth token rotation increases local unattended complexity. No verified general content publish, redirects, preview, performance, site rollback, or general metadata API should be claimed.

## Generic static sites

This is a profile/local adapter, not a remote provider adapter. It reads a bounded repository/build output, enumerates routes/assets, locates sitemap/robots/header/redirect sources, maps source-to-output where known, runs the configured build under explicit host-effect policy, and supplies local/preview URLs to SiteProbe/Lens.

It supports plain HTML, Kujo SSG, Astro, Hugo, Eleventy, Jekyll, Docusaurus, and static modes of Next.js/Nuxt/SvelteKit. Deployment remains a separate adapter. Mutations are source patches or generated proposals; workflow ACT uses the repository engineering boundary and Git receipts. Git revert is a recovery option only for committed source changes, not external deployment/runtime state.

## Framework support

Official evidence: [Astro integrations](https://astro.build/integrations/), [Next.js static exports](https://nextjs.org/docs/pages/guides/static-exports), [Next.js metadata](https://nextjs.org/docs/app/getting-started/metadata-and-og-images), [Nuxt deployment](https://nuxt.com/docs/4.x/getting-started/deployment), [Svelte packages](https://svelte.dev/packages), [Hugo deployment](https://gohugo.io/host-and-deploy/), [Jekyll plugins](https://jekyllrb.com/docs/plugins/installation/), and [Docusaurus deployment](https://www.docusaurus.io/docs/deployment).

- **Astro:** thin profile/integration is justified for `astro add`/catalog discovery, configuration detection, output directory, routes, and sitemap setup. Core checks stay generic.
- **Next.js:** richer framework profile detects App/Pages router, static export versus server output, metadata conventions, route manifests, redirects/headers, and deployment adapter. Avoid the term “Kujo Next.js adapter,” which collides with Next.js deployment adapters.
- **Nuxt:** detect Nuxt major, rendering mode, Nitro preset, prerender routes, and output directory. No separate workflows.
- **SvelteKit:** detect selected official deployment adapter and compose its provider; static mode uses generic-static.
- **Hugo, Eleventy, Jekyll, Docusaurus:** detector/config helpers only. Generic output, repository, SiteProbe, and Lens cover WebOps behavior.
- **Remix:** wait; framework/runtime detection can be added when a user or distribution path justifies it.

## Headless CMS

Official evidence: [Sanity HTTP authentication](https://www.sanity.io/docs/content-lake/http-auth), [Sanity API versioning](https://www.sanity.io/docs/content-lake/api-versioning), [Contentful authentication](https://www.contentful.com/developers/docs/references/authentication/), [Contentful Content Management API](https://www.contentful.com/developers/docs/references/content-management-api/), [Storyblok Management API](https://www.storyblok.com/docs/api/management), [DatoCMS Content Management API](https://www.datocms.com/docs/content-management-api), [Ghost Admin API](https://docs.ghost.org/admin-api), [Prismic migration surface](https://prismic.io/features/migration), and [Framer Server API beta](https://www.framer.com/developers/server-api-introduction).

- **Sanity:** high-value batch 2. Pin date-based API version; separate public/published, draft/private, mutation, perspective/release, and webhook capabilities. Release rollback is plan-dependent.
- **Contentful:** high-value batch 2. Keep CDA, CPA, and CMA credentials/Abilities distinct; honor optimistic concurrency. Environments and snapshots aid preview/evidence but snapshots are not universal restore.
- **Storyblok:** strong batch 2/3 content adapter with public/preview delivery tokens, Management API, visual preview, and webhooks.
- **DatoCMS:** strong conformance candidate with granular tokens, versioned API, environments, record versions, and a genuine restore endpoint.
- **Ghost:** technically straightforward later content adapter; curated/non-open integration directory limits distribution.
- **Prismic:** read/preview support may be useful, but its documented Migration API should not become routine content ACT.
- **Framer:** experimental only until Server API leaves open beta and auth/rate/distribution contracts stabilize.
