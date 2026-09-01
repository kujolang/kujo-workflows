# 07 — Platform Adapter Contract

## Boundary

A platform adapter is a collection of thin Ability bindings plus identity/auth/error metadata. It translates between a WebOps semantic input/output and one provider. It does not reason about SEO, choose content strategy, orchestrate workflows, evaluate outcomes, generate reports, build graphs, run browser QA, or own run history.

## Required adapter surface

1. **Manifest:** ID, provider, layer categories, adapter/contract versions, supported API versions, Abilities, auth references, resource schema, fixture catalog, and entrypoints.
2. **Identity inspect:** return provider account/project/site/store identifiers, declared domains, and verification evidence without secrets.
3. **Ability bindings:** one handler per advertised Ability with input/output schema compatibility.
4. **Error normalization:** stable category, retryability, HTTP/provider code, request ID, bounded message, and redacted details.
5. **Pagination/rate metadata:** cursor/page state, partial-result flag, rate headers, retry-after, query cost where applicable.
6. **Receipts:** normalized invocation identity, provider request identity, target, effect, status, result/evidence references, and recovery contract.
7. **Fixtures:** identity, happy path, empty, pagination, auth denial, missing scope, rate limit, partial/async response, provider errors, and every advertised mutation.

## Authentication declaration

The adapter declares accepted credential kinds and minimum scopes per Ability. Profiles contain references such as environment variable, OS keychain entry, external secret command, or platform-native CLI session identifier—never values. OAuth installation/refresh remains owned by the platform integration shell or credential broker. The adapter receives a short-lived resolved secret at invocation and must not persist or echo it.

Recommended initial credential sources:

- `env` for local/custom-token use;
- `command` for a bounded platform CLI token exchange returning one value on stdout;
- `keychain` when a Kujo credential provider exists;
- `oauth-session` only through a platform-owned integration shell.

The contract never asks a provider adapter to implement a universal OAuth server.

## Input envelope

Every call contains exact site/binding/Ability identity, definition digest, adapter version, provider resources, run/step/invocation IDs, permission, approval reference when required, idempotency key when required, bounded input, deadline, and output budget. Authentication is injected out-of-band.

## Output envelope

Every result contains:

- success/error status and normalized result;
- adapter/API version and fixture/live mode;
- verified resource identity and affected resources;
- pagination/completeness and rate-limit state;
- provider request ID when supplied;
- redacted evidence references and digests;
- effect receipt for ACT;
- rollback/recovery descriptor;
- warnings/limitations and elapsed time.

Provider payloads are stored only as bounded, redacted evidence when necessary. Normal results expose the smallest schema the workflow needs.

## Mutation preconditions

Before ACT, the host—not the handler—validates:

1. run permission and role maximum;
2. Ability effect classification;
3. installed adapter definition digest;
4. declared and verified provider identity;
5. exact domain/account/project/resource target;
6. credential reference and required scopes;
7. request-bound approval matching payload digest and target;
8. output/call/time/cost budgets;
9. idempotency/retry policy;
10. recovery descriptor and pre-change evidence where feasible.

Adapters must fail closed if provider identity changes after approval.

## Error categories

`authentication_required`, `authentication_expired`, `authorization_denied`, `scope_missing`, `identity_mismatch`, `resource_not_found`, `conflict`, `stale_version`, `validation_failed`, `rate_limited`, `quota_exhausted`, `provider_unavailable`, `timeout`, `partial_result`, `async_pending`, `unsupported_api_version`, `provider_contract_changed`, and `unknown_provider_error`.

## Third-party extensibility

A third party adds an adapter by publishing a directory/package containing the manifest, Ability bindings, fixtures, source metadata, and conformance declaration. Core changes are unnecessary when:

- all Ability IDs already exist;
- the manifest schema validates;
- adapter and advertised capability tests pass;
- the support-bundle registry/static index can reference the artifact;
- no reserved first-party namespace is claimed.

A new semantic Ability requires core review; a new provider binding does not.

## Provider examples

- Shopify binding converts GraphQL edges, `userErrors`, throttle cost, GIDs, and API-version headers into normalized records.
- Webflow binding preserves staged/live state and treats staged writes as ACT.
- Vercel binding resolves project/deployment IDs and returns preview protection metadata.
- Cloudflare binding separates zone Pages, cache, rules, and analytics scopes and never exposes `purge_everything` under URL purge authority.

