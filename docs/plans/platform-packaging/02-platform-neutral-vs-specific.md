# 02 — Platform-Neutral Versus Platform-Specific

## Classification

| Class | Current behavior | Platform knowledge needed? | Owner |
| --- | --- | --- | --- |
| Universal WebOps | crawl, links, live headers/metadata/schema, accessibility, visual QA, finding history, reporting, evaluation | No | SiteProbe, Lens, Eval, WebOps |
| Search-provider-specific | search performance, URL inspection/submission, keyword/backlink data, PageSpeed/CrUX | Provider-specific but not site-platform-specific | SearchBridge |
| Analytics-provider-specific | GA4 and provider-native traffic/RUM | Yes, normalized as measurements | SearchBridge |
| Content-source-specific | list/read normalized source records | Yes | thin adapter retrieves; ContentGraph relates |
| CMS-specific | draft/version/publish/unpublish, CMS metadata mutation | Yes | CMS/content adapter via Abilities |
| Commerce-specific | product/collection/article content and commerce-native metrics | Yes | commerce adapter; measurement normalization as applicable |
| Framework-specific | output mode, route/build artifact discovery, metadata source locations | Sometimes | detector/profile helper, not workflow copy |
| Deployment-specific | deployments, previews, logs, promote/rollback, build hooks | Yes | deployment adapter |
| Edge-specific | cache purge, edge redirects/headers, edge analytics | Yes | edge adapter; analytics through SearchBridge |
| Repository-specific | source patch, build command, Git receipt/revert | Yes, but not provider API | local repository binding and existing engineering tools |

## Workflows that are already neutral

`weekly-site-health`, `monthly-seo-review`, `ai-visibility-benchmark`, and most of `weekly-search-intelligence` are platform-neutral once a live URL and optional SearchBridge providers exist. `site-bootstrap`, `weekly-content-intelligence`, and `quarterly-content-portfolio` are neutral for crawl/local-corpus inputs but benefit from content-source adapters. `post-publish`, `content-refresh`, and `finding-to-fix` have neutral reasoning and verification but need bound mutation/preview/deploy Abilities for provider-aware ACT.

No workflow needs a Shopify, Webflow, Vercel, or Cloudflare copy.

## Hidden assumptions

- **Filesystem/repository:** bootstrap, refresh, and finding-to-fix imply source access without expressing whether the source is local Markdown, generated output, theme code, or remote CMS.
- **One platform:** `site.platform` assumes a singular identity.
- **HTML is authoritative:** crawl evidence sees rendered/public output, but not drafts, unpublished content, deployment configuration, or provider metadata.
- **Publishing means one thing:** current stages do not distinguish remote draft creation, publish, unpublish, promotion, deployment, or edge activation.
- **Redirect ownership:** redirects may live in CMS, framework config, deployment config, or edge rules. Live crawl cannot identify the authoritative control plane.
- **Preview availability:** Lens accepts a URL but no contract resolves a safe preview URL or its authentication requirements.
- **Credential availability:** environment-variable references are validated syntactically but not bound to provider, scope, site, or expiry.
- **Mutation target:** current workflow permission records a mode, not an exact provider account/project/store/resource set.
- **Rollback:** current workflow receipts do not model provider-native, compensating, Git, manual, or unavailable rollback.

## Do not abstract what is already generic

- Do not add `site.read` to mean an HTTP crawl; SiteProbe already owns it.
- Do not add `metadata.read` when live HTML is sufficient; use platform metadata only to explain or mutate the authoritative source.
- Do not reimplement PageSpeed, CrUX, GSC, GA4, backlinks, or keyword APIs in platform adapters.
- Do not use a framework adapter to parse final HTML; inspect the build output or live site generically.
- Do not treat a deployment provider's dashboard metrics as a replacement for SiteProbe or SearchBridge.

## Extension rule

Add a platform Ability only when it unlocks one of four outcomes unavailable from generic HTTP/repository evidence:

1. authoritative unpublished/source content;
2. provider-native preview/deployment state;
3. a bounded provider mutation needed by a WebOps workflow;
4. provider-native measurements that SearchBridge can normalize and label.

