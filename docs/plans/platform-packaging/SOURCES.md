# Official Source and Claim Ledger

Research date: 2026-09-01. Provider capability, authentication, rate-limit, rollback, and distribution claims are based on first-party documentation. Repository findings are tied to the local paths below. If a provider fact changes, the machine matrices and the relevant deep dive must change together.

## Kujo repository evidence

| Claim area | Primary repository evidence |
|---|---|
| Ten workflow wrappers share one harness; current live evidence tools are SiteProbe, SearchBridge, ContentGraph, and optional Lens | `webops/workflows/*/run.py`; `scripts/webops_workflow.py` |
| Profile v1 has a scalar platform field and credential references | `contracts/webops/site-profile.v1.schema.json`; `contracts/webops/README.md` |
| WebOps effects and role/skill catalog | `kujo-agents/webops/00-capability-integration-map.md`; `kujo-agents/webops/roles/`; `kujo-agents/webops/skills/` |
| Dashboard launch and profile behavior | `webops/dashboard/` |
| Workflow contracts, stage/evidence schemas, fixtures, and release checks | `webops/workflows/*/workflow.yaml`; `contracts/webops/`; `fixtures/webops/`; `tests/`; `ecosystem-release.json` |
| SearchBridge normalized provider measurements | sibling `searchbridge/README.md`, provider contracts, fixtures, and tests |
| SiteProbe public crawl/metadata/header/link ownership | sibling `siteprobe/README.md`, schemas, fixtures, and tests |
| ContentGraph normalized corpus relationships | sibling `contentgraph/README.md`, schemas, fixtures, and tests |
| Lens visual/browser verification | sibling `lens/README.md`, CLI/contracts, fixtures, and tests |
| Spec, Eval, Dispatch, RunLedger, and Howl ownership | sibling repositories `spec/`, `eval/`, `dispatch/`, `runledger/`, and `howl/` |
| Existing Ability/projection/approval patterns | sibling `agents-sdk/` and `cms/` contracts/examples |
| MCP Ability projection and public read-only WebMCP precedent | sibling `mcp/` and `cms/` MCP/WebMCP code/contracts |
| Local workflow-pack discovery and permissions | sibling `kujo/` workflow-pack code, docs, and tests |
| Kennel local/source/static-index packaging paths | sibling `kennel/` documentation, manifests, and tests |

## Hosted commerce, visual CMS, and content platforms

| Claim | Official sources |
|---|---|
| Shopify uses a versioned GraphQL Admin API; REST Admin is legacy; limits are calculated by query cost | [GraphQL Admin API](https://shopify.dev/docs/api/admin-graphql/latest), [API limits](https://shopify.dev/docs/api/usage/limits), [API versioning](https://shopify.dev/docs/api/usage/versioning) |
| Shopify auth/scopes/tokens and public distribution impose distinct security and product obligations | [Authentication and authorization](https://shopify.dev/docs/apps/build/authentication-authorization), [access tokens](https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens), [access scopes](https://shopify.dev/docs/apps/build/authentication-authorization/app-installation/manage-access-scopes), [distribution](https://shopify.dev/docs/apps/launch/distribution), [App Store requirements](https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements) |
| Shopify exposes redirect and webhook surfaces; theme editing/version control has separate constraints | [URL redirect object](https://shopify.dev/docs/api/admin-graphql/latest/objects/urlredirect), [webhooks](https://shopify.dev/docs/apps/build/webhooks), [theme code editor](https://shopify.dev/docs/storefronts/themes/tools/code-editor), [theme version control](https://shopify.dev/docs/storefronts/themes/best-practices/version-control) |
| Webflow v2 supports scoped authentication, CMS staging/live publication, site publication, metadata, webhooks, and plan-sensitive limits | [Authentication](https://developers.webflow.com/data/reference/authentication), [scopes](https://developers.webflow.com/data/reference/scopes), [CMS publishing](https://developers.webflow.com/data/docs/working-with-the-cms/publishing), [page metadata](https://developers.webflow.com/data/reference/pages-and-components/pages/get-metadata), [site publishing](https://developers.webflow.com/data/reference/sites/publish/), [webhooks](https://developers.webflow.com/data/docs/working-with-webhooks), [rate limits](https://developers.webflow.com/data/reference/rate-limits) |
| Webflow offers an app Marketplace path | [Marketplace overview](https://developers.webflow.com/data-beta/docs/marketplace/overview) |
| Squarespace's general Website API is read-only and the documented API family is commerce-centered | [Website API overview](https://developers.squarespace.com/commerce-apis/website-overview), [products](https://developers.squarespace.com/commerce-apis/products), [authentication](https://developers.squarespace.com/commerce-apis/authentication-and-permissions), [OAuth](https://developers.squarespace.com/commerce-apis/oauth), [rate limits](https://developers.squarespace.com/commerce-apis/rate-limits) |
| Sanity offers scoped HTTP auth, date-based API versions, and perspective-aware reads | [HTTP auth](https://www.sanity.io/docs/content-lake/http-auth), [API versioning](https://www.sanity.io/docs/content-lake/api-versioning), [perspectives](https://www.sanity.io/docs/content-lake/perspectives) |
| Contentful separates delivery/preview/management APIs and auth modes | [Authentication](https://www.contentful.com/developers/docs/references/authentication/), [API basics](https://www.contentful.com/developers/docs/concepts/apis/), [Content Management API](https://www.contentful.com/developers/docs/references/content-management-api/) |
| Storyblok, DatoCMS, and Ghost expose content-management APIs suitable for later thin adapters | [Storyblok Management API](https://www.storyblok.com/docs/api/management), [Storyblok Content Delivery API](https://www.storyblok.com/docs/api/content-delivery), [DatoCMS Content Management API](https://www.datocms.com/docs/content-management-api), [DatoCMS authentication](https://www.datocms.com/docs/content-management-api/authentication), [Ghost Admin API](https://docs.ghost.org/admin-api), [Ghost webhooks](https://docs.ghost.org/admin-api/webhooks/overview) |
| Prismic's cited write surface is migration-oriented and Framer's Server API is open beta | [Prismic migration](https://prismic.io/features/migration), [Framer Server API introduction](https://www.framer.com/developers/server-api-introduction) |

## Edge and deployment platforms

| Claim | Official sources |
|---|---|
| Cloudflare supports scoped tokens, cache purge, Pages previews/rollbacks, URL forwarding, and GraphQL analytics with explicit limits | [API overview](https://developers.cloudflare.com/api/overview/), [cache purge](https://developers.cloudflare.com/api/resources/cache/methods/purge/), [Pages previews](https://developers.cloudflare.com/pages/configuration/preview-deployments/), [Pages rollbacks](https://developers.cloudflare.com/pages/configuration/rollbacks/), [URL forwarding](https://developers.cloudflare.com/rules/url-forwarding/), [GraphQL Analytics](https://developers.cloudflare.com/analytics/graphql-api/), [GraphQL limits](https://developers.cloudflare.com/analytics/graphql-api/limits/) |
| Vercel supports deployment/preview inspection, rollback, webhooks, integrations, and a reviewed public listing path | [REST API](https://vercel.com/docs/rest-api), [deployments](https://vercel.com/docs/deployments/overview), [rollback](https://vercel.com/docs/deployments/rollback-production-deployment), [webhooks](https://vercel.com/docs/webhooks), [create an integration](https://vercel.com/docs/integrations/create-integration), [submit an integration](https://vercel.com/docs/integrations/submit-integration) |
| Netlify supports authenticated APIs, deploy previews/creation, and distributable Build Plugins | [API start/auth/rate limits](https://docs.netlify.com/api-and-cli-guides/api-guides/get-started-with-api/), [Deploy Previews](https://docs.netlify.com/deploy/deploy-types/deploy-previews/), [create deploys](https://docs.netlify.com/deploy/create-deploys/), [Build Plugins](https://docs.netlify.com/extend/develop-and-share/develop-build-plugins/) |
| GitHub Pages supports custom Actions workflows and a Pages REST API | [Custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [Pages REST API](https://docs.github.com/en/rest/pages/pages) |
| Later deployment candidates have official automation surfaces but lower initial strategic fit | [Firebase Hosting REST deploy](https://firebase.google.com/docs/hosting/api-deploy), [AWS Amplify pull-request previews](https://docs.aws.amazon.com/amplify/latest/userguide/pr-previews.html), [Render API](https://api-docs.render.com/reference/introduction), [Railway public API](https://docs.railway.com/reference/public-api), [Fly Machines API](https://fly.io/docs/machines/api/) |

## Framework and static-site evidence

| Claim | Official sources |
|---|---|
| Astro has a public integration surface/catalog and sitemap integration | [Astro integration catalog](https://astro.build/integrations/), [sitemap integration](https://docs.astro.build/en/guides/integrations-guide/sitemap/) |
| Next.js exposes static export, metadata, and adapter conventions that can be detected without a remote provider adapter | [Static exports](https://nextjs.org/docs/pages/guides/static-exports), [metadata](https://nextjs.org/docs/app/getting-started/metadata-and-og-images), [deployment adapters](https://nextjs.org/docs/app/api-reference/adapters) |
| Nuxt, SvelteKit, Hugo, Eleventy, Jekyll, and Docusaurus can use generic output/repository inspection with thin detection profiles | [Nuxt deployment](https://nuxt.com/docs/4.x/getting-started/deployment), [Svelte packages](https://svelte.dev/packages), [Hugo deploy](https://gohugo.io/host-and-deploy/), [Eleventy](https://www.11ty.dev/), [Jekyll plugins](https://jekyllrb.com/docs/plugins/installation/), [Docusaurus deployment](https://www.docusaurus.io/docs/deployment) |

## Inferences and confidence boundaries

- Priority tiers, package composition, and ownership boundaries are Kujo architecture recommendations inferred from repository evidence plus official provider capabilities; they are not provider claims.
- A listed distribution channel means an official directory, integration mechanism, package/catalog surface, or documented community path exists. It does not imply a partnership, acceptance, endorsement, or guaranteed listing.
- Where official documentation did not establish a stable general capability—particularly Squarespace general content mutation, Webflow redirect mutation, Netlify analytics/log API access, and open Cloudflare marketplace submission—the matrix declines to advertise it.
- Provider API facts must be revalidated before each adapter implementation and release. The research package is a dated architecture baseline, not a perpetual guarantee.
