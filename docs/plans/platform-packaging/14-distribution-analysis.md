# 14 — Distribution Analysis

## Principle

Technical compatibility is not enough. Each support bundle needs a credible adoption surface that does not require Kujo SaaS.

| Integration | Initial channel | Official directory/marketplace opportunity | Recommendation |
| --- | --- | --- | --- |
| Generic static | GitHub Action, source bundle, Kennel static index, Agent Skills, MCP catalog | GitHub Marketplace for Actions | launch first; broadest portable funnel |
| Shopify | GitHub/source/custom-app setup, agency tutorials | Shopify App Store after full app/compliance review | strong long-term official marketplace; do not block local release on app review |
| Webflow | GitHub/source/site-token setup, agency community | Webflow Marketplace via OAuth/review | strong agency/discoverability route; public app later |
| Vercel | source/OAuth connectable integration, deploy-button docs | Community integration first; public listing after install/review threshold | strong dev channel; marketplace listing is not immediate |
| Cloudflare | GitHub template, Wrangler guide, framework recipes | current open marketplace route unverified | use templates/community; do not claim official listing |
| Netlify | npm Build Plugin, GitHub/source bundle | Build Plugin UI/catalog | high-quality distribution surface; first batch 2 |
| Astro | npm integration and `astro add` | Astro integrations catalog/community submission | thin framework integration creates discovery without workflow duplication |
| GitHub Pages | reusable Action/workflow template | GitHub Marketplace | strong generic-static distribution shell |
| Sanity | npm/Studio plugin, Exchange | Sanity Exchange/plugins | strong batch-2 content audience |
| Contentful | App Framework/source | marketplace is gated/select partner path | pursue after product proof; do not assume acceptance |
| Storyblok | plugin/source/community | official open submission not verified | community/plugin opportunity |
| DatoCMS | npm/source | no verified broad marketplace path | technical value over distribution |
| Ghost | source/integration docs | curated directory not open to submissions | community only; lower priority |
| Framer | plugin/Marketplace | official but policy currently in flux | reverify after API exits beta |
| Squarespace | source commerce augmentation | OAuth/partner process evolving | wait; limited WebOps depth |

## Marketplace sequencing

1. Prove local fixture/read-only adapter and clean install.
2. Publish source/docs and collect real setup evidence.
3. Add platform-native OAuth only when multi-user distribution requires it.
4. Build an embedded UI/native marketplace product only if the platform requires it and the adoption case justifies hosted operational responsibility.
5. Keep the marketplace shell thin: consent, installation metadata, local export/bootstrap, optional webhook relay. It does not become the workflow engine.

## Framework distribution without fragmentation

One `@kujolang/webops` package may expose framework setup entrypoints or generated configs. Publish separate npm names only when a framework catalog requires it. Astro can have a thin integration package; Next.js/Nuxt/SvelteKit support should begin as profiles/detectors in the main package. Hugo/Eleventy/Jekyll/Docusaurus need recipes and generic-static CI, not packages.

## Discovery messages

Platform-facing documentation leads with outcomes:

- Shopify: audit storefront health, find decaying product/editorial content, verify theme/content previews, and publish only approved bounded changes.
- Webflow: inspect CMS/site health, prepare metadata/content updates, verify staging, and gate publication.
- Vercel/Netlify/Cloudflare: verify previews/deployments, correlate site findings to deployment evidence, and recover with explicit scope.
- Static: add local/CI site health and post-publish verification to any generated output.

Internal tool names appear in architecture/reference docs, not onboarding headlines.

