# Risk Register

| ID | Risk | Likelihood | Impact | Control / evidence required | Owner | Release gate |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | Profile composition becomes a second competing config | Medium | High | additive v1 migrator; one v2 canonical schema; dashboard/Agency mapping | WebOps core | v1 fixture round-trip and no duplicate profile file |
| R-02 | “Capability” collides with Kujo host authority | High | High | semantic operations use `kujo.ability/v1`; capability receipt means resolved availability | architecture | schema/docs terminology test |
| R-03 | Platform-name conditionals leak into workflows | High | High | workflow requests Ability IDs; static check forbids provider names in core runner paths | WebOps core | architecture conformance |
| R-04 | Installed credential becomes implicit ACT | Medium | Critical | run/role/policy/approval/target checks outside adapter; negative tests | Dispatch/security | all mutation denial tests pass |
| R-05 | Wrong store/project/zone mutation | Medium | Critical | declared+verified identity and approval target digest; immediate pre-ACT recheck | adapters | cross-account mismatch fixtures |
| R-06 | Secrets enter profiles/logs/receipts | Medium | Critical | references only; out-of-band injection; structural/pattern redaction; adversarial fixtures | adapters/security | credential scan and golden receipts |
| R-07 | Adapter becomes broad provider admin SDK | High | High | only cataloged WebOps Abilities; workflow consumer required; non-goals review | adapter maintainers | manifest Ability allowlist |
| R-08 | Provider API drift silently changes results | High | High | pinned API versions, fixture source metadata, scheduled smoke/deprecation report, fail closed | adapters | unsupported-version fixture |
| R-09 | Rate/cost amplification | Medium | High | per-call/query/output budgets, Retry-After, bounded retries, webhook preference | adapters | 429/query-cost tests |
| R-10 | Retry duplicates an uncertain mutation | Medium | Critical | idempotency contract and reconciliation; unknown status; no blind retry | adapters/Dispatch | async/timeout mutation fixtures |
| R-11 | Rollback promise excludes critical state | High | High | structured scope/exclusions/mode, approval, recovery test | adapters | receipt schema + provider fixture |
| R-12 | Cache purge has excessive blast radius | Medium | Critical | separate URL/tag/all Abilities; full purge disabled by default | Cloudflare adapter | permission matrix tests |
| R-13 | Redirect mutation creates loop/open redirect | Medium | High | source/target validation, route simulation, preview and SiteProbe verification | route adapters | loop/external target fixtures |
| R-14 | Webhook forgery/replay triggers workflow | Medium | High | provider-defined signature/replay/size/event checks; no direct mutation | ingress | invalid/duplicate fixture tests |
| R-15 | Detection heuristic authorizes wrong provider | Medium | Critical | detected is non-authoritative; ACT needs declared+verified | profile/resolver | heuristic-only ACT denial |
| R-16 | Multiple adapters silently conflict | High | High | explicit binding or fail closed; provider-labeled measurements | resolver | ambiguity fixtures |
| R-17 | Framework fragmentation creates packages/workflows | Medium | Medium | framework profiles + generic static; package only for proven catalog channel | packaging | bundle inventory review |
| R-18 | Support bundles activate excessive context | High | Medium | outcome-scoped skill/tool sets and byte/count budgets | agent integration | token footprint snapshot |
| R-19 | MCP bypasses effect policy | Medium | Critical | same gateway/resolver/receipts; OBSERVE default; write exposure explicit | MCP/security | cross-transport denial parity |
| R-20 | WebMCP leaks drafts/private content or mutates | Low | Critical | same-origin, published-only, bounded, read-only allowlist | site/CMS | public fixture privacy tests |
| R-21 | OAuth requirement creates mandatory Kujo service | Medium | High | local custom-token path; optional provider-owned shell; exportable local binding | product | offline/local onboarding proof |
| R-22 | Workflow manifests still overstate executable tools | High | Medium | label synthesized steps; incrementally replace with real Dispatch/tool invocations | workflow core | evidence provenance assertions |
| R-23 | Clean-machine proof relies on sibling checkout/cache | High | High | tracked archive + exact release manifest + temporary prefix | release | clean-machine gate |
| R-24 | Marketplace plan is fabricated/outdated | Medium | Medium | classify official/partner/community/speculative with current source date | distribution | reverify before submission |
| R-25 | Repository expands into one repo per platform | Medium | Medium | one repo/generated bundles until independent ownership/runtime justifies extraction | maintainers | architecture review |
| R-26 | Generic WebOps degrades without adapters | Medium | High | no-adapter fixture/doctor/workflows remain release gates | WebOps core | generic URL/static suite |
| R-27 | Platform package accidentally includes excluded ecosystems | Low | Critical | exact exclusion phrase and validation blocking excluded IDs/names in bundle matrices | release | exclusion scanner |

## Residual risks

Provider plan differences and marketplace approval remain external. Live smoke tests can show compatibility with controlled resources but cannot certify all plans/accounts. The implementation must disclose those limits in capability receipts rather than weakening offline conformance.
