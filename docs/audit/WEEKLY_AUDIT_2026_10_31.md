# Weekly Kujo Workflows Audit - 2026-10-31

Audit ID: `kujo-workflows-audit-2026-10-31`
Captured: `2026-10-31T10:12:07Z`

## Scope and disposition

This audit compared the catalog against sibling checkouts changed since the
2026-10-24 window, prioritizing Kujo, Kujo Skills, Watchdog, Intake, and the
workflow-adjacent repositories with recent commits. `$kujo-workflow-auditor`
was unavailable, so repository instructions and local validators were used.

| Repository | Evidence | Disposition |
| --- | --- | --- |
| `kujo` | `e5394ca` | Kujo is now `1.9.0`; runtime and performance work does not add a workflow or broaden existing boundaries. The Publishing House clean support lock was refreshed. |
| `kujo-skills` | `c1267f8` | Maintenance-agent and authenticated Hermes guidance is repo-backed. Existing Agents SDK and Watchdog skill relationships remain compatible; the support lock and skill matrix advanced. |
| `watchdog` | `b0a682a` | Hermes OAuth-proxy routing documentation clarifies a live operational route and verification boundary; it does not create a new catalog workflow. Watchdog tool evidence advanced. |
| `dispatch`, `agents-sdk`, Publishing House tool repositories | current clean heads | Ecosystem alignment commits changed support checkouts, so the locked offline fixture pins and compatibility matrix were refreshed. Contracts and workflow entries remain unchanged. |
| `intake`, `wordpress-migrator`, `workcell`, `kujo-videoops`, other recent siblings | current local evidence | Changes remain repository-local or experimental and do not establish a validated shared workflow contract. Existing relationships and deferred boundaries were preserved. |

## Updated records

- Advanced `workflow-catalog.json`, `skill-compatibility-matrix.json`, and `tool-integration-matrix.json` to this audit.
- Refreshed Publishing House `install-lock.json` and `compatibility-matrix.json` to clean current support checkouts: Kujo `1.9.0`, Dispatch `18b5c73`, Agents SDK `70cd1fb`, Kujo Skills `c1267f8`, StoryDesk `31b4d29`, Dossier `670def8`, GalleyPack `f829584`, BluePencil `88df35c`, VersionSeal `f005374`, PressWire `2f8bd70`, and AssetWorks `ea5e034`. Kujo Agents and ReaderSignal were already current.
- No workflow implementation, fixture, contract schema, routing relationship, or deferred-opportunity record changed.

## Confirmed current and compatibility disposition

The 44 active workflows remain inventoried and resolve to existing skills, tools,
documentation, inputs, outputs, and acceptance boundaries. Added: none.
Changed: support evidence and audit metadata only. Preserved: AI SDK/Watchdog,
Publishing House, Workcell, Relay, Tribunal, WebOps, and VideoOps relationships.
Deferred: live provider execution, authenticated browser capture, external asset
search, cloud rendering, publication, hosted runners, separate-machine proof,
and any Workcell/Relay/Tribunal composition.

## Validation

Directly verified: catalog validation, contract validation, JSON parsing, and
the full unit suite after the support-lock refresh. The first unit run exposed
stale locked checkouts; the refreshed lock is the corrective evidence. Required
host gates remain bounded by their local dependencies; Workcell execution still
requires the local image and Docker/Colima runtime. No live provider or Hermes
completion was claimed.

## Next watch list

- Kujo 1.9.x runtime changes and the next clean support baseline.
- Kujo Skills maintenance-agent/Hermes documentation and any corresponding
  executable contract or fixture.
- Watchdog authenticated Hermes completion evidence, token separation, and
  provider error handling.
- Workcell image availability and host execution receipts.
- Intake outreach approval/receipt contracts and WordPress Migrator browser,
  asset, and fidelity boundaries before considering new workflow integration.
