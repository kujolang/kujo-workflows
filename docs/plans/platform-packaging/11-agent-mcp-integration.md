# 11 — Agent, MCP, and WebMCP Integration

## Agent experience

Agents should discover outcome verbs, not repository names:

- inspect site and platform composition;
- review site health;
- analyze a search decline;
- prepare a content refresh;
- resolve a preview and verify it;
- verify publication/deployment;
- propose or execute an approved bounded change.

The Agent Project/Plugin reads the selected support-bundle manifest and workflow preset, then activates only the relevant roles, skills, and Ability projections. Internal tool ownership remains inspectable in receipts and a `--verbose`/doctor view.

## Skill selection

Current 27 WebOps domain skills total 42,253 bytes/5,347 words; activating all is avoidable context. Bundle manifests should list skill groups by outcome. At run time load:

1. site profile + capability preflight + reporting;
2. the selected workflow's domain skills;
3. the chosen adapter's compact setup/limitations reference;
4. tool skills only when their tool runs.

Do not generate one large provider skill containing API documentation. Adapter schemas and provider metadata remain machine-side; agent instructions describe only semantic operations, effects, limitations, and stop conditions.

## MCP

MCP is an optional transport/projection of the same selected `kujo.ability/v1` registry. It should not expose raw adapter methods or create a second capability catalog.

- default exposure: selected OBSERVE Abilities only;
- write/external effects: disabled unless an explicit MCP exposure policy and runtime approval provider allow them;
- tool names are projections; canonical Ability ID/version/digest remains metadata;
- handlers call the same resolver/gateway and return the same receipts;
- list-tools output is filtered by site, workflow, permission, installed binding, and outcome to limit context;
- credentials remain server/local host-side and never enter tool definitions or model-visible payloads.

Useful first MCP tools are `webops_site_inspect`, `webops_capabilities`, `webops_run_health`, `webops_preview_resolve`, and report/finding queries. Do not expose hundreds of Shopify Admin or Cloudflare API operations.

## WebMCP

WebMCP is appropriate only for bounded public observation semantics supplied by a site, such as site information, public content listing/search, and exact published record retrieval. Existing CMS/SSG precedent is correct: same-origin, published-only, bounded, sanitized, read-only, and opt-out.

WebMCP must not:

- carry platform credentials;
- expose draft/private content;
- mutate CMS, deployment, edge, or commerce state;
- imply that a public website authorizes platform API calls;
- replace adapter identity verification.

A future public site's WebMCP hints may improve discovery, but remain untrusted declared evidence until verified.

## Dispatch integration

Dispatch owns the workflow DAG. Each platform action is a tool/Ability step with:

- preflight/identity receipt;
- proposed input artifact;
- approval gate;
- idempotency and retry policy;
- action receipt;
- Eval/SiteProbe/Lens verification;
- recovery hint or compensation step;
- RunLedger correlation.

Adapters never resume workflows or choose the next step.
