# 05 — Site Composition Model

## Decision

Extend `webops.site-profile/v1` to `webops.site-profile/v2`. Do not introduce a competing profile. The v2 schema replaces scalar `site.platform` with typed composition instances while preserving `site.id`, `site.url`, optional repository, high-level evidence capabilities, integrations, permission default, and credential references.

## Shape

```text
site
  id, url, domains[], repository?
composition
  framework[]
  content[]
  commerce[]
  deployment[]
  edge[]
  analytics[]
  search[]
bindings
  ability -> instance/resource selector
detection
  declared + detected + verified evidence
policies
  permission default, mutation allowlist, provider preferences
credential_references
  secret-provider references only
```

Each composition instance has a stable local `id`, provider `type`, adapter ID/version constraint, bounded resource identifiers, optional routes it owns, status, and provenance. Resource IDs are not secrets. A profile may omit every layer and still run generic WebOps against `site.url`.

## Example

```json
{
  "schema": "webops.site-profile/v2",
  "site": {
    "id": "acme-storefront",
    "url": "https://www.acme.example",
    "domains": ["www.acme.example"],
    "repository": {"path": ".", "remote": "https://github.com/acme/storefront"}
  },
  "composition": {
    "framework": [{"id": "app", "type": "nextjs", "mode": "server", "status": "verified"}],
    "content": [{"id": "editorial", "type": "sanity", "adapter": "webops-sanity", "resources": {"project_id": "p1", "dataset": "production"}}],
    "commerce": [{"id": "store", "type": "shopify", "adapter": "webops-shopify", "resources": {"shop_domain": "acme.myshopify.com"}}],
    "deployment": [{"id": "frontend", "type": "vercel", "adapter": "webops-vercel", "resources": {"team_id": "team_1", "project_id": "prj_1"}}],
    "edge": [{"id": "edge", "type": "cloudflare", "adapter": "webops-cloudflare", "resources": {"zone_id": "zone_1"}}],
    "analytics": [{"id": "web", "type": "ga4", "integration": "searchbridge", "resources": {"property_id": "123"}}],
    "search": [{"id": "google", "type": "gsc", "integration": "searchbridge", "resources": {"property": "sc-domain:acme.example"}}]
  },
  "bindings": {
    "content.read": {"instance": "editorial"},
    "commerce.content.read": {"instance": "store"},
    "deployment.preview.resolve": {"instance": "frontend"},
    "cache.purge.urls": {"instance": "edge"}
  }
}
```

## Declared, detected, verified

Detection never silently becomes configuration.

1. **Declared**: operator-selected provider and resource identity.
2. **Detected**: heuristic evidence from files, manifests, DNS, headers, HTML markers, or provider config.
3. **Verified**: exact adapter identity call or deterministic local contract confirms the resource and its relationship to an authorized domain/repository.

Every observation records detector ID/version, source, value, confidence, timestamp, and evidence digest. A detected provider may enable a setup suggestion or read-only local profile. Remote reads require a verified binding. ACT requires declared and verified identity.

## Detection order

1. Read existing v2 profile.
2. Inspect repository markers: `package.json`, lockfiles, framework configs, `vercel.json`, `netlify.toml`, Wrangler/Pages config, `_redirects`, `_headers`, SSG configs, CMS SDK/config identifiers.
3. Inspect build output and route manifests if present.
4. Inspect live headers, DNS, and HTML markers with bounded same-origin/network policy.
5. Match configured adapter resources through identity-only API calls.
6. Present conflicts; require an explicit choice for remote bindings.

Heuristics are evidence, not authority. Do not infer a Cloudflare edge binding solely from a response header or a Shopify Admin resource from storefront markup.

## Conflict resolution

- A binding explicitly naming an instance wins if the adapter is installed, identity verifies, and policy permits the effect.
- A single verified provider may satisfy an unbound OBSERVE Ability.
- Multiple verified providers for a mutation are an error until `bindings` selects one.
- Multiple measurement providers are not collapsed; SearchBridge returns provider-labeled normalized results and the workflow selects or compares them.
- Route ownership may narrow a binding (`/shop/*` to Shopify, `/docs/*` to Sanity/static), but overlapping write routes fail closed.
- No implicit priority is derived from array order, discovery order, marketplace, or credentials present.

## v1 migration

`webops.site-profile/v1` remains readable. Migration maps `site.platform` to a detected legacy hint, retains all existing fields, maps current SearchBridge integration keys to `analytics`/`search` instances, and emits a v2 profile requiring verification before ACT. The original file is never overwritten without explicit `--write` authorization; default init produces a proposal/diff.

