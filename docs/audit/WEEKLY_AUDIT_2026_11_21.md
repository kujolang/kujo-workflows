# Weekly Kujo Workflows Audit - 2026-11-21

Audit ID: `kujo-workflows-audit-2026-11-21`
Captured: `2026-11-21T16:00:00Z`

## Scope and disposition

The catalog was compared with sibling repositories changed since the 2026-11-07
audit, prioritizing Kujo Skills, SiteKit, AI SDK, RAG, Howl, Lens, Kujo Agents,
Kujo, and the recent provider/collaboration repositories. The requested
`$kujo-workflow-auditor` skill remains unavailable in the installed skill paths;
the repository instructions, workflow source, sibling contracts, and local
validators were used instead.

| Repository | Evidence | Disposition |
| --- | --- | --- |
| `kujo-skills` | `2067b47` | Refreshed the canonical skill support pin. AI SDK/RAG provider-registry guidance and SiteKit 1.2 routing are repo-backed; existing workflow relationships remain compatible. |
| `ai-sdk` | `4316452` | Provider registry/setup and certification guidance changed, but the two existing fixture workflows still use their documented entry points and keep live-provider behavior gated. |
| `rag` | `befd4cb` | External embedding/reranking adapters are documented and fixture-tested in the sibling repository; the existing RAG workflow remains offline hash-embedding based and under-tested for external providers. |
| `site-kit` | `74cff7b` | SiteKit 1.2 and optional documentation recipes are repo-backed. No catalog workflow consumes the optional recipe or upgrade-CLI surfaces, so no new relationship was promoted. |
| `howl` | `caf57b3` | Campaign/tool-card refresh remains sibling-local; the existing deterministic Howl content factory contract is current. |
| `kujo`, `kujo-agents` | `f4a9f7f`, `b7551d3` | Current collaboration/release evidence does not establish a new workflow contract. Publishing House support pins were advanced to clean current checkouts. |
| `lens`, `kujolang-mcp`, `docs.kujolang.ai`, `source` | current Nov 10-20 heads | Browser hardening, catalog/docs, and Source release work remain external or sibling-local; existing deferred boundaries were preserved. |

## Updated records

- Advanced the catalog, skill matrix, and tool matrix audit IDs to 2026-11-21.
- Advanced skill evidence to `kujo-skills` `2067b47`.
- Refreshed tool evidence for Kujo `f4a9f7f`, AI SDK `4316452`, and Howl
  `caf57b3`.
- Refreshed Publishing House install and compatibility pins for Kujo, Kujo
  Agents, and Kujo Skills.
- No workflow implementation, contract schema, fixture, routing record, or
  deferred-opportunity record changed.

## Compatibility disposition

Added: none. Changed: support evidence only for Kujo, Kujo Agents, Kujo Skills,
AI SDK, and Howl. Preserved: AI SDK/Watchdog, RAG, WebOps, Publishing House,
VideoOps, Workcell, Relay, and Tribunal relationships. Deferred: external AI
SDK provider certification, RAG external embedding/reranking execution,
SiteKit recipe consumption, live providers, authenticated browser capture,
hosted runners, publication, and separate-machine proof. Removed: none.

## Validation

Passed: catalog validation (`44` workflows), contract validation (`19` schemas,
`16` examples, `314` required-field negatives), AI SDK/Watchdog showcase,
AI SDK/Muzzle fixture benchmark, RAG fixture workflow, Howl fixture workflow,
Tribunal gate, Relay gate, JSON/path checks, and shell checks for the changed
workflow entry points.

Failed or partial: the full unit suite ran `28` tests with `8` failures and
`2` skips because the local Publishing House fixture could not load the pinned
`kujo-agents` and `kujo-skills` capabilities in the uninstalled test context.
The clean-install Publishing House proof was started with the current sibling
checkouts but exceeded the bounded 75-second local execution window while
running the eleven-workflow fixture; no install success was claimed. Workcell
validation was blocked before execution because the configured local Docker
socket was unavailable. No live provider,
authenticated browser, Hermes/Slack completion, external RAG adapter, or
SiteKit recipe integration was claimed.

## Next watch list

- Re-run the clean Publishing House install/fixture proof with current Kujo,
  Kujo Agents, and Kujo Skills pins; investigate the missing-capability unit
  failures if they persist outside the uninstalled context.
- Add a dedicated fixture contract before promoting AI SDK provider registry
  setup or RAG external embedding/reranking adapters into workflow support.
- Watch SiteKit 1.2 consumer adoption and the vendored WebOps dashboard artifact
  version separately from the core WebOps workflow contract.
- Re-run Workcell when the Docker socket and pinned local image are available;
  keep live-provider, authenticated-browser, hosted-runner, publication, and
  separate-machine boundaries explicit.
