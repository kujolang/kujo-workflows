# 10 — Security, Effects, and Recovery

## Core rule

Credentials prove API access; they do not grant WebOps authority. Profiles describe targets; they do not authorize action. Abilities declare effects; they do not approve an invocation.

## OBSERVE / PROPOSE / ACT enforcement

| Mode | Allowed | Forbidden |
| --- | --- | --- |
| OBSERVE | bounded API reads, crawl, identity verification, local run artifacts | provider/repository mutation |
| PROPOSE | OBSERVE plus local specs, patches, mutation payload previews, recovery plan | any provider mutation, including remote drafts |
| ACT | only payload-bound, role-bounded, target-verified approved Abilities | undeclared/broader effects, implicit follow-on actions |

Dispatch should create one approval gate per materially distinct action group. Approvals contain Ability/version/digest, adapter, provider resources, exact target set, input digest, effect summary, expiry, approver identity, and maximum count/bytes/cost. A changed payload or target invalidates approval.

## Credential policy

- store only references in profiles and artifacts;
- resolve secrets immediately before the adapter call;
- prefer resource-scoped tokens and read-only scopes for OBSERVE;
- separate read and write credential references when providers allow it;
- never include tokens, build-hook URLs, OAuth codes, client secrets, signed preview bypasses, or full authorization headers in logs/receipts;
- let platform-native OAuth shells own consent, refresh, rotation, and revocation;
- redact structured fields and secret-shaped strings before persistence;
- test 401/403/missing-scope/expired-token paths offline.

## Primary threats and controls

| Threat | Control |
| --- | --- |
| Wrong store/project/zone | declared + verified identity; domain/resource cross-check; approval binds IDs |
| SSRF or malicious provider URL | adapter manifest allowlists exact HTTPS hosts; SiteProbe retains private-network controls |
| Cross-site mutation | route/domain ownership and provider resource identity checked immediately before ACT |
| Unbounded content/redirect changes | exact resource list/count/byte budgets; chunk receipts; no wildcard by default |
| Cache purge blast radius | separate URL/tag/all Abilities; full purge disabled unless explicitly allowed |
| Redirect abuse/open redirect | source host/route ownership, target scheme/host policy, loop simulation, SiteProbe verification |
| Hidden publication | remote drafts are ACT; publish/promotion is a separate ACT |
| Webhook forgery/replay | provider-defined signature verification, timestamp/replay ID, bounded body, idempotency; unsupported trust fails closed |
| Rate/cost amplification | call/query-cost/output budgets, `Retry-After`, bounded retries, no blind polling |
| Async duplicate action | provider/idempotency key and reconciliation before retry; uncertain effect recorded `unknown` |
| Secret leakage | out-of-band injection, structural redaction, adversarial fixtures, bounded provider payload retention |
| Adapter supply chain | pinned source/digest, manifest schema, conformance, reserved namespace, no code on install |
| Approval bypass via MCP/agent | projections preserve effects; runtime policy remains authoritative; no mutation exposure by default |

## Normalized ACT receipt

Required fields:

- schema, invocation/run/step IDs;
- site/profile digest;
- Ability ID/version/definition digest;
- adapter ID/version/provider/API version;
- provider account/project/site/store/zone and bounded resource IDs;
- operation/effect and input digest;
- approval ID/digest/approver/expiry reference;
- status and provider request/idempotency IDs;
- before/after evidence references and digests;
- timestamps/duration/call count/rate state;
- rollback descriptor;
- redaction summary and warnings.

## Rollback model

Rollback is an object, never a boolean:

```json
{
  "mode": "provider_native|compensating_write|git_revert|manual|unavailable",
  "ability": "deployment.rollback",
  "target_reference": "dpl_previous",
  "covers": ["deployment_artifact", "domain_routing"],
  "excludes": ["database", "secrets", "current_provider_configuration"],
  "deadline": null,
  "requires_approval": true,
  "instructions_reference": "evidence://recovery-plan.json"
}
```

Never say “rollback supported” without enumerating covered and excluded state. Shopify/Webflow content typically needs compensating write/manual recovery; Vercel/Netlify/Cloudflare Pages deployment rollback is provider-native but does not restore external state; Git recovery applies only to versioned repository content.

## Webhook receive boundary

`webhook.register` is ACT. Receiving and validating a delivery is OBSERVE but still network-exposed. Use a narrow local/optional ingress component with signature policy, timestamp/replay protection, size/content-type bounds, provider/site identity matching, event allowlist, dead-letter evidence, and no direct mutation. A verified event may enqueue Dispatch; it cannot bypass approval.

