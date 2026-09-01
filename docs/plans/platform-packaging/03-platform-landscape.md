# 03 — Platform Landscape

## Landscape conclusion

The modern website is a stack, not a platform. The evaluated ecosystem separates into hosted commerce/CMS, visual CMS, headless content, frameworks, deployment/static hosting, edge/network, and generic output classes. A single site may bind one provider in each layer.

## Evaluated classes

| Class | Strong examples | WebOps integration depth | Architecture treatment |
| --- | --- | --- | --- |
| Hosted commerce/CMS | Shopify | Deep content/redirect/publish/webhook API | commerce + content adapter |
| Hosted visual CMS | Webflow | Deep CMS/staged publish/page metadata API | content adapter with site publish boundary |
| Limited hosted builder | Squarespace | Commerce-centric API; weak general site/content control | generic crawl plus optional commerce augmentation; wait |
| Headless CMS | Sanity, Contentful, Storyblok, DatoCMS | Strong content, preview, publish, webhooks | composable content adapters, batch 2 |
| Publishing CMS | Ghost | Strong content API, weaker open distribution | later content adapter |
| Emerging visual builder | Framer | Rich Server API but open beta/policy drift | experimental later adapter |
| Deployment platform | Vercel, Netlify, Render | Deployments, previews, logs, rollback, hooks | deployment adapters |
| Edge/network | Cloudflare | cache, edge analytics, redirects, Pages | edge adapter plus optional deployment binding |
| Static hosting | GitHub Pages, Firebase Hosting, Cloudflare Pages, Netlify static | artifact deployment and config | generic-static + deployment adapter |
| Full-stack framework | Next.js, Nuxt, SvelteKit, Remix | multiple output/runtime modes | framework profile/detector, not provider adapter |
| Static framework | Astro, Hugo, Eleventy, Jekyll, Docusaurus | portable build output | generic-static profile; thin distribution helpers only |
| General application host | Railway, Fly.io | broad infrastructure controls | wait; poor early WebOps specificity |
| Cloud deployment suite | AWS Amplify, Firebase Hosting | useful preview/deploy API, higher auth complexity | batch 2 |
| Generic/unknown | plain HTML, S3/bare metal/custom server | live URL and optional repository | first-class generic WebOps |

## Additional candidates

- **Sanity and Contentful** are the strongest headless-CMS additions after batch 1 because they validate delivery/preview/management separation, revision handling, and high-value composition with Next.js/Vercel/Cloudflare.
- **Storyblok** is close behind, especially for visual editing and agency audiences.
- **DatoCMS** has an excellent machine contract and true record-version restore, but a smaller distribution surface.
- **Firebase Hosting** is a strong static-host batch-2 candidate because it has preview channels, REST/CLI deployment, rollback, and an emulator-oriented Google ecosystem.
- **Render** is useful after the core proof because its rollback exclusions force precise recovery receipts.
- **Prismic** should not be presented as general ACT content management until an official general-purpose management API is verified; its current documented write surface is migration-oriented.

## Competitive position

Adjacent products already provide deep crawls, predefined SEO issues, keyword/backlink datasets, continuous Lighthouse gates, cloud monitoring, or content optimization. Kujo should not compete on the number of checks. Its distinct product is a local-first, agent-native, evidence-linked operating workflow that composes provider-neutral measurements, separates recommendation from action, and can verify a platform change through preview and post-deploy evidence without requiring a Kujo service.

The defensible boundary is:

- platform-neutral workflows instead of provider dashboards;
- source-to-outcome evidence and receipts instead of isolated scores;
- explicit OBSERVE/PROPOSE/ACT effects;
- composable site layers rather than one vendor identity;
- offline fixtures and third-party adapter conformance;
- narrow agent context rather than raw provider API exposure.

## Research limitations

Official API surfaces and distribution policies change. Netlify analytics/log export, AWS Amplify rollback, Cloudflare integration-directory submission, and current framework-catalog review requirements require re-verification during implementation. Absence of a documented capability is represented as unsupported, not inferred from a provider UI.
