# Weekly Kujo Workflows Audit - 2026-11-07

Audit ID: `kujo-workflows-audit-2026-11-07`
Captured: `2026-11-07T11:06:44Z`

## Scope and disposition

The catalog was compared with sibling repositories changed since the prior
2026-10-31 audit, prioritizing Kujo, Kujo Skills, AI Chat, Watchdog, and the
recent Hermes and WordPress Migrator repositories. `$kujo-workflow-auditor`
was unavailable in the installed skill paths, so repository instructions,
workflow source, sibling documentation, and local validators were used.

| Repository | Evidence | Disposition |
| --- | --- | --- |
| `kujo` | `7a13207` | Current runtime checkout changed after the previous support pin; the existing workflow commands and contracts remain compatible, so only support evidence advanced. |
| `kujo-skills` | `76c2496` | Release-readiness and 136-skill validation passed. Existing skill identities remain resolvable; the Publishing House support pin and skill matrix advanced. |
| `kujo-agents` | `a7e9d02` | Current clean checkout differed from the locked support baseline; the Publishing House support pin advanced after doctor/test evidence. |
| `ai-chat` | `b59b6e6` | Hermes catalog maintenance is repository-local. The existing AI SDK/Watchdog showcase remains the only supported workflow relationship; its tool matrix evidence advanced. |
| `watchdog` | `7a0bd9a` | Pricing-catalog maintenance is repository-local. The existing fixture/live telemetry boundary remains unchanged; its tool matrix evidence advanced. |
| `kujo-hermes`, `hermes-kujo-discord-agents`, `wordpress-migrator` | current local heads | Recent work is product/demo or platform-local and does not establish a validated shared workflow contract. Existing deferred boundaries were preserved. |

## Updated records

- Advanced `workflow-catalog.json`, `skill-compatibility-matrix.json`, and
  `tool-integration-matrix.json` to the new audit ID and current matrix heads.
- Refreshed Publishing House `install-lock.json` and
  `compatibility-matrix.json` to clean current support checkouts: Kujo
  `7a13207`, Kujo Agents `a7e9d02`, and Kujo Skills `76c2496`.
- No workflow implementation, fixture, contract schema, compatibility
  relationship, routing record, or deferred-opportunity record changed.

## Compatibility disposition

Added: none. Changed: support evidence only for Kujo, Kujo Agents, and Kujo
Skills, plus observed matrix heads for AI Chat and Watchdog. Preserved: AI
SDK/Watchdog, Publishing House, Workcell, Relay, Tribunal, WebOps, and VideoOps
relationships. Deferred: live providers, authenticated browser capture,
external assets, cloud rendering, publication, hosted runners, separate-machine
proof, and unsupported Hermes/WordPress integrations.

## Validation

Passed: catalog validation (`44` workflows), contract validation (`19` schemas,
`16` examples, `314` required-field negatives), documentation validation,
Kujo Skills release-readiness (`136` skills; 12 + 23 tests), and JSON/path
resolution checks. Publishing House doctor passed after the support pins were
updated; the full workflow fixture suite was not rerun to completion before
this record was written.

Partial or unresolved: AI Chat verification reported sibling-local failures in
Sunday scheduling, automation-close/persistence, ChatGPT connection routes,
durable action receipts, and approval/checkpoint suites. Watchdog verification
reported `73` passes, `2` failures (`rate_limit_controls_check.js` and
`runtime_measurements_adapter_check.js`), and `1` skip. Kujo workspace tests
were blocked during dependency compilation by `No space left on device`.
The Workcell gate remains host-dependent and was not claimed as a successful
container execution. No live provider, Hermes completion, or WordPress
integration was claimed.

## Next watch list

- Free disk space, then rerun the Kujo workspace tests and the full Publishing
  House fixture suite against the refreshed clean support pins.
- AI Chat's failing persistence, ChatGPT connection, approval, and scheduling
  suites; Watchdog's rate-limit and runtime-measurement checks.
- Kujo Skills maintenance-agent and Hermes guidance for executable contract or
  fixture changes before any new workflow relationship is considered.
- Workcell image/socket availability and the existing live-provider,
  authenticated-browser, publication, and separate-machine boundaries.
