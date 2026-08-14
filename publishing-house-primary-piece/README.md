# Publishing House Primary Piece Production

Create the authoritative source artifact from an Editorial Brief and evidence-ready Dossier packet.

## Boundary

Drafting and developmental revision remain proposals; new claims return to Dossier. Record ownership remains with storydesk, dossier, galleypack; this workflow stores references and orchestration receipts only.

## Run the deterministic fixture

```bash
(cd publishing-house-primary-piece && bash bin/run --request fixtures/request.fixture.json --json)
```

Fixture mode is offline, credential-free, deterministic, and cannot target a live destination. Live mode must be explicit and fails closed until compatible adapters are configured; it never falls back to fixture behavior.

## Inputs and outputs

The request supplies portable House, Brand, and Audience profiles, permission, capabilities, correlation IDs, and tool record references. Outputs include capability, agent-step, tool, Dispatch, summary, blocker or completion receipts under the selected run directory.

## State and recovery

state.json records running, paused, blocked, failed, and completed states. Repeating a completed run is an idempotent read. Retries are bounded at two attempts. Resume is accepted only from a paused approval run.

Writer routing is profile-specific: `flagship-feature` and `problem-solution`
use Features Writer; `technical-walkthrough` and
`feature-update-explanation` use Technical Editor & Writer; `campaign-copy`
uses Campaign Copywriter. Creative Director and Developmental Editor bound the
selected writer stage.

Required tools: storydesk, dossier, galleypack, dispatch, agents-sdk. Default permission: PROPOSE. Readiness: installable and verified for the locked offline fixture contract; catalog status remains Limited because operator-specific live adapters are not included.
