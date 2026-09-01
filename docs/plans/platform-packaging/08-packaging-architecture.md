# 08 — Packaging Architecture

## One repository, generated support bundles

Keep core contracts, adapters, bundle manifests, fixtures, tests, and documentation in `kujo-workflows` for batch 1. Do not create one repository per platform. Extract a provider adapter only when it needs a distinct release cadence, language/runtime, marketplace shell, or ownership boundary.

Proposed layout:

```text
webops/
  core/
    abilities/
    profiles/
    resolver/
    receipts/
  adapters/
    generic-static/
    shopify/
    webflow/
    vercel/
    cloudflare/
  bundles/
    static/
    shopify/
    webflow/
    vercel/
    cloudflare/
  fixtures/
  conformance/
  commands/
```

Existing workflow directories remain unchanged except for additive semantic requirements/presets. The current `scripts/webops_workflow.py` migrates toward a core runner/Dispatch bridge rather than acquiring provider-name branches.

## Support-bundle composition

A support bundle contains references, not copies:

- adapter package/version;
- profile template and detector IDs;
- relevant existing workflow IDs and default presets;
- selected WebOps skills and role packages;
- SearchBridge defaults/provider hints;
- fixtures and conformance declarations;
- doctor checks and setup docs;
- version compatibility constraints.

Example Shopify bundle activates site profile/preflight/reporting, technical SEO, search performance, content decay, schema/metadata, post-publish, content refresh, and finding-to-fix guidance. It does not activate all 27 domain skills or duplicate workflows.

## Delivery mechanisms

### Near term

1. A source-distributed bundle in `kujo-workflows` with a `kujo-pack.yaml` exposing namespaced `init`, `doctor`, `detect`, `run`, and `list` commands through `kujo pack run webops ...`.
2. A strict ecosystem release manifest pinning `kujo-workflows` and required sibling tool commits.
3. Kennel local/source/static-index packages for adapter modules and lockfiles.
4. Agent Skills-compatible copied/generated bundles containing only selected skills.
5. GitHub Action/npm/plugin shells only where a platform distribution channel warrants them.

Do not claim a public Kennel registry or remote `kujo pack add`; current Kujo/Kennel contracts do not provide those production channels.

### Later marketplace shells

Shopify/Webflow/Vercel OAuth apps or integrations should provision local profile/credential references and installation metadata. They must not become a mandatory Kujo control plane. If a platform requires a hosted OAuth callback, that optional shell owns only consent/token custody/rotation and can export a local binding; local custom-token paths remain supported.

## Onboarding

Target experience, contingent on auditing/adding the commands:

```text
install Kujo with the operating/quality components required by selected outcomes
install/copy the chosen WebOps support bundle
kujo pack run webops init --bundle shopify --site https://example.com
kujo pack run webops doctor --profile .webops/profile.json
kujo pack run webops run weekly-site-health
```

`init` defaults to detection plus a proposed v2 profile. It does not write secrets or grant ACT. `doctor` verifies installed versions, adapter fixtures, profile schema, resource identity, credential reference presence, provider scopes without revealing values, and workflow readiness.

## Progressive installation

Outcome presets select dependencies:

- `site-health`: SiteProbe, optional Lens/SearchBridge performance, 7–9 skills.
- `search-intelligence`: SearchBridge, optional ContentGraph, 5–7 skills.
- `content-intelligence`: ContentGraph/SiteProbe, optional RAG/SearchBridge, 7–10 skills.
- `post-publish`: SiteProbe/Lens/Eval, optional submission/Howl, 8–12 skills.
- `full`: all workflows, but skills are still activated per run.

## Version ownership

| Artifact | Owner | Version rule |
| --- | --- | --- |
| WebOps core/workflows | `kujo-workflows` | SemVer release |
| `kujo.ability/v1` | Ability package | independent canonical schema/version |
| WebOps Ability catalog | `kujo-workflows` | independent additive catalog version |
| Adapter manifest contract | `kujo-workflows` | major on breaking machine contract |
| Provider adapter | adapter owner | independent SemVer + supported API range |
| Site profile | `kujo-workflows` | schema version, migrator retained |
| Support bundle | `kujo-workflows` initially | independent SemVer + compatibility constraints |
| Fixtures | adapter | fixture schema + provider/API capture metadata |

Bundles pin compatible ranges; they do not force all adapters to release with core.

## Drift strategy

- capture provider API version/date and source URL in every fixture;
- scheduled doc/changelog checks produce proposals, not automatic contract edits;
- normal CI uses offline fixtures;
- opt-in provider smoke jobs use least-privilege test resources and read-only Abilities by default;
- mutation smoke tests run only in disposable resources with explicit authorization;
- adapters warn before version expiry and fail closed after an unsupported version;
- capability drift changes runtime availability rather than silently changing behavior.

