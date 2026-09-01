# 12 — Testing and Conformance

## Adapter conformance

Every adapter must pass a provider-independent suite:

1. manifest/schema/namespace/version validation;
2. deterministic identity inspection and domain/resource match/mismatch;
3. advertised Ability definition/schema/effect compatibility;
4. auth reference resolution without secret persistence;
5. OBSERVE result normalization, bounded output, provenance, empty data;
6. pagination completeness/partial results and stable ordering;
7. rate-limit/query-cost handling and bounded retry;
8. normalized provider errors, timeouts, async/uncertain effects;
9. secret/PII redaction in logs, errors, receipts, and fixtures;
10. ACT denial in OBSERVE/PROPOSE and without approval;
11. ACT exact target/input digest/idempotency receipt when advertised;
12. rollback descriptor accuracy;
13. offline-only test execution and fixture-source metadata;
14. third-party install/discovery without core edits.

Capability-specific tests run only when the manifest advertises that Ability. An adapter cannot ship an untested advertised mutation.

## Required fixture set

```text
identity-success.json
identity-domain-mismatch.json
read-empty.json
read-page-1.json
read-page-2.json
auth-401.json
scope-403.json
rate-429.json
provider-5xx.json
contract-drift.json
async-accepted.json
async-succeeded.json
mutation-success.json
mutation-validation-error.json
mutation-uncertain.json
webhook-valid.json
webhook-invalid-or-unsupported.json
```

Provider-specific additions include Shopify GraphQL `errors`/`userErrors`/throttle cost, Webflow staged/live and publish limit, Vercel/Netlify/Pages preview and rollback, Cloudflare granular/full purge, and optimistic concurrency/version conflicts for content providers.

## Support-bundle conformance

A bundle separately proves:

- local/source installation from a tracked archive;
- lock/manifest compatibility and artifact digest;
- detector output and v1-to-v2 profile proposal;
- doctor result with no credentials and fixture credentials;
- outcome-scoped skill/role activation;
- adapter resolution, ambiguity failure, and explicit binding;
- unchanged workflow execution through semantic Abilities;
- evidence packet import into the dashboard;
- fixture-only no-network run;
- deactivation/removal leaves profiles/evidence intact and removes executable contributions;
- clean-machine proof with only declared dependencies.

## Core workflow tests

Add typed workflow input schemas. The current shared CLI is insufficient for item-specific workflows. At minimum:

- post-publish: published resource/URL and optional deployment receipt;
- content-refresh: finding/content resource and proposed source target;
- finding-to-fix: finding ID and exact target;
- AI visibility: query-suite reference;
- recurring workflows: previous/baseline selection.

Tests must assert not only `success` but actual tool/Ability invocation, evidence schema, permission denial, degradation, and RunLedger correlation. Synthesized placeholder receipts must be explicitly labeled until replaced.

## Live smoke policy

Normal CI is offline. Scheduled opt-in smoke tests:

- use dedicated least-privilege test accounts/resources;
- default to identity and read operations;
- pin provider/API versions and record deprecation headers;
- use disposable resources for authorized mutation tests;
- cap calls, output, duration, and cost;
- never fail normal fixture CI solely because a live provider is unavailable;
- produce drift proposals, not automatic compatibility claims.

## Clean-machine proof

Archive tracked files, install from the exact release manifest, use a temporary user-owned prefix, run bundle install/doctor/offline workflow/JSON validation/uninstall, verify no undeclared sibling checkout or developer cache is required, and retain a bounded receipt. Live-provider proof remains a separate optional phase.
