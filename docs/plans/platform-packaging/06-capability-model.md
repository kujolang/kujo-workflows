# 06 — Capability and Ability Model

## Decision: reuse Abilities; retain capability receipts

Kujo already uses “capability” for native host-effect permission and current WebOps uses it for evidence availability. The portable semantic operation should therefore use the existing `kujo.ability/v1` contract. A platform adapter binds Abilities. The WebOps resolver emits a `webops.capability-receipt/v2` reporting whether an Ability is installed, configured, verified, authorized, and available for this run.

This avoids a third semantic system while preserving familiar capability-driven workflow language: a workflow asks whether `content.publish` is available, and the resolver answers with an Ability binding receipt.

## Minimal Ability families

| Family | Operations | Why WebOps needs it |
| --- | --- | --- |
| identity | `platform.identity.inspect` | prove account/site/project/domain binding |
| content | `content.list`, `content.read`, `content.write`, `content.publish`, `content.unpublish`, `content.version.list` | authoritative source and publication |
| commerce | `commerce.content.list`, `commerce.content.read`, `commerce.content.write` | product/collection/article WebOps content without general admin |
| metadata | `metadata.read`, `metadata.write` | authoritative provider metadata when HTML/repository is insufficient |
| routes | `route.list`, `redirect.list`, `redirect.write` | migration and canonical path control |
| deployment | `deployment.list`, `deployment.inspect`, `deployment.trigger`, `deployment.promote`, `deployment.rollback` | preview-to-production verification and recovery |
| preview | `preview.resolve` | supply Lens/SiteProbe with a bounded preview URL and access metadata |
| environment | `environment.inspect` | build/runtime identity without secret values |
| cache | `cache.purge.urls`, `cache.purge.tags`, `cache.purge.all` | post-deploy invalidation with explicit blast radius |
| configuration | `headers.read`, `headers.write`, `robots.source.read`, `robots.source.write`, `sitemap.source.read`, `sitemap.source.write` | authoritative source config, not live inspection |
| assets | `asset.list`, `asset.read` | image/alt/size inventory where source API adds value |
| events | `webhook.register`, `webhook.remove`, `webhook.delivery.verify` | event-driven post-publish/deploy workflows |
| measurement | `measurement.native.read` | provider-native commerce/edge data routed through SearchBridge |

Do not add arbitrary provider CRUD. New Abilities require at least one existing WebOps workflow consumer and an effect/receipt/test design.

## Effects mapping

- **OBSERVE:** provider GET/query/list operations, identity inspection, preview resolution, version listing, and webhook delivery verification.
- **PROPOSE:** no provider API operation. PROPOSE creates local specs, patches, diffs, action plans, or provider mutation payloads as artifacts.
- **ACT:** every provider mutation, including creating/updating a remote draft, registering a webhook, triggering a build, promoting a preview, changing metadata/redirects/headers, purging cache, or rolling back.

An Ability definition declares effects but does not grant permission. The run permission, role maximum, adapter policy, exact target, and approval must all allow invocation.

## Ownership boundaries

- **SearchBridge:** `search.performance`, `analytics`, PageSpeed, CrUX, backlinks, keyword data, URL inspection, search submission, and normalized provider-native measurement. Platform adapters may implement a narrow provider reader behind SearchBridge; workflows do not consume raw Shopify/Cloudflare/Vercel analytics.
- **SiteProbe:** live HTTP crawl, links, redirects observed in responses, headers, metadata, structured data, robots, sitemap, status, and site structure.
- **ContentGraph:** normalized content relationships, clusters, overlaps, orphans, and link opportunities. Adapters supply records; they do not score relationships.
- **Lens:** browser/render/visual/accessibility verification. `preview.resolve` supplies a URL/access contract.
- **Dispatch:** multi-step orchestration, approval, resume, retries, compensation routing, and action state.
- **RunLedger:** correlated run/action receipts and usage; adapter receipts are referenced, not copied into a new ledger.
- **Eval:** acceptance checks for preview/deployment/content outcomes.
- **Howl:** post-publish assets and distribution packages; no platform adapter duplicates generation.

## Availability receipt

For each requested Ability, record:

```json
{
  "ability": "deployment.preview.resolve",
  "definition_version": "1.0.0",
  "status": "available",
  "binding": "frontend",
  "adapter": "webops-vercel@0.1.0",
  "identity": "verified",
  "authentication": "reference-present",
  "permission": "OBSERVE",
  "source": "declared+verified",
  "limitations": ["preview may require protection bypass"],
  "evidence": ["adapter://webops-vercel/identity/sha256:..."]
}
```

Statuses: `available`, `unconfigured`, `unverified`, `unauthorized`, `unsupported`, `degraded`, `ambiguous`, and `adapter-missing`. Missing capability remains explicit and never becomes false data.

## Retry and idempotency

Ability definitions use existing idempotency modes. Reads may be retry-safe within budgets. Mutations are either keyed, provider-idempotent, compensating-only, or never automatically retried. An asynchronous `202` or provider request ID is not success; the final receipt distinguishes `accepted`, `in_progress`, `succeeded`, `failed`, and `unknown`.

