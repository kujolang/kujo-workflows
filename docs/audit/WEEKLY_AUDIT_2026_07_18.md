# Weekly Kujo Workflows Audit - 2026-07-18

Audit ID: `kujo-workflows-audit-2026-07-18`
Captured: `2026-07-18T06:01:14-04:00` / `2026-07-18T10:01:14Z`
Automation ID: `weekly-kujo-worklflows-audit`

## Scope

This refresh audited the workflow catalog against sibling Kujo repositories under `/Users/robertdevore/2026/Kujolang/kujo-repos`, prioritizing repositories changed during the last 7-10 days.

Recent repository evidence inspected:

| Repository | Branch | HEAD | Disposition |
| --- | --- | --- | --- |
| ai-chat | `main` | `d5cecb0` | Current showcase relationship preserved; new pane benchmark and provider-neutral tool surfaces deferred from catalog promotion until a dedicated workflow contract exists. |
| kujo-skills | `weekly-kujo-skills-audit-2026-07-04` | `6a1e012` | Skill source pointer updated in the compatibility matrix; 45 existing workflow-skill relationships still validate. |
| watchdog | `main` | `5f9fea6` | Current Watchdog showcase relationship preserved; named upstreams and agent-insights dashboard are compatible additions, not catalog-breaking drift. |
| relay | `main` | `66228c2` | Relay lifecycle workflow preserved; matrix risk/tests now mention provider-generated tool planning and typed tool-result evidence while retaining local-alpha boundaries. |
| cms | `codex/cms-experience-entry-privacy` | `a1a4d01` | No active workflow catalog entry references CMS; `kujo-cms-workflows` remains a skill-only sibling surface. |
| cms-experience | `main` | `756eab2` | No active workflow catalog entry references CMS Experience; no workflow artifact changed. |
| July 15 hygiene sweep | multiple | multiple | Added `.github` Kujo tool-artifact hygiene guards across many sibling repos; no workflow contract drift found. |

## Workflow Records Updated

- `docs/audit/workflow-catalog.json`: audit ID refreshed to `kujo-workflows-audit-2026-07-18`.
- `docs/audit/skill-compatibility-matrix.json`: audit ID refreshed and `kujo-skills` source commit updated from `84bd74a0ff82b7fb99e9e6d2c7d940847e27a95a` to `6a1e012229171cbf310d69b4c35264f756028d56`.
- `docs/audit/tool-integration-matrix.json`: audit ID refreshed; AI SDK, AI Chat, and Watchdog records added; Relay risk/evidence updated for provider-generated tool planning while preserving the local-alpha limitation.
- `docs/audit/README.md` and `docs/audit/VERIFICATION.md`: weekly audit scope, evidence, and verification boundaries added.

## Workflows Confirmed Current

- `agency-runner`
- `agency-verified-fix-loop`
- `ai-sdk-muzzle-benchmark`
- `ai-sdk-watchdog-showcase`
- `casefile-incident-evidence-packet`
- `docsgen-repo-contract-runner`
- `enterprise-dispatch-approval-router`
- `feature-card-workflow`
- `howl-content-factory`
- `loop-engineering`
- `mcp-agent-gateway-review`
- `rag-enterprise-knowledge-gate`
- `tribunal-decision-gate`
- `relay-lifecycle-handoff`
- `workcell-execution-gate`

## Compatibility Disposition

- Added: tool-matrix records for `ai-sdk`, `ai-chat`, and `watchdog`.
- Changed: `relay` tool-matrix record now names provider-generated tool planning and `relay_provider_tool_smoke.sh` as repo-backed evidence, without expanding Relay beyond local-alpha semantics.
- Preserved: 45 workflow-to-skill relationships; validator still reports 36 compatible and 9 compatible-but-under-tested.
- Deferred: AI Chat pane-profile benchmark runner, browser tools, and Web Search are not promoted into new workflow catalog entries because the workflow repository has no dedicated contract/fixture yet.
- Deferred: CMS and CMS Experience remain outside the active workflow catalog until a workflow kit exists.
- Removed: none.

## Validation

Passed:

- `python3 scripts/validate_catalog.py --json`
- `python3 scripts/validate_contracts.py`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `bash tests/validate_catalog.sh`
- JSON validation over tracked `*.json` files
- `bash -n` over repository `*.sh` files
- `git diff --check`
- Sibling AI Chat `npm test` (107 tests)
- Sibling Watchdog proxy/API/frontend focused checks with explicit `KUJO_BIN`

## Partial Verification Boundaries

- AI Chat live benchmark execution was not run because it requires a running AI Chat server, API auth token, selected pane profile, and provider credentials.
- AI Chat browser and Web Search surfaces were repository- and skill-evidence reviewed; live browser/Web Search smoke remains configuration-gated.
- Watchdog named upstreams and agent insights were repository-evidence reviewed; no live upstream credentials were used.
- Relay provider-generated tools were checked against current Relay repo docs, skill evidence, and the focused provider-tool smoke. The smoke printed `PASS relay provider tool smoke`, but did not exit cleanly before it was interrupted after 90 seconds, so the provider-tool result remains partial rather than fully passed. The workflow audit did not rerun the sibling Relay aggregate acceptance suite.

## Next Watch List

- Promote an AI Chat benchmark/tools workflow only after adding a dedicated workflow runner, fixtures, validation contract, and live/mock boundary record.
- Watch Watchdog named-upstream, auth/rate-limit, and agent-insights changes for impact on `ai-sdk-watchdog-showcase`.
- Watch Relay provider-tool and Watchdog-route changes for any shift from local-alpha proof to external delivery or service-mode claims.
- Keep CMS/CMS Experience deferred until a workflow kit references their delivery, auth, or content-publication contracts.
- Keep the nine under-tested relationships under-tested until provider-backed, authenticated-browser, and consumer-level evidence is available.
