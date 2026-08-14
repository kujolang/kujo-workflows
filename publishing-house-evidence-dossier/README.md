# Publishing House Evidence Dossier

Build and independently review claims, sources, captured evidence, freshness, rights, consent, and conflicts before drafting.

## Boundary

Unsupported material claims block or narrow drafting. Record ownership remains with dossier, storydesk; this workflow stores references and orchestration receipts only.

## Run the deterministic fixture

```bash
(cd publishing-house-evidence-dossier && bash bin/run --request fixtures/request.fixture.json --json)
```

Fixture mode is offline, credential-free, deterministic, and cannot target a live destination. Live mode must be explicit and fails closed until compatible adapters are configured; it never falls back to fixture behavior.

## Inputs and outputs

The request supplies portable House, Brand, and Audience profiles, permission, capabilities, correlation IDs, and tool record references. Outputs include capability, agent-step, tool, Dispatch, summary, blocker or completion receipts under the selected run directory.

## State and recovery

state.json records running, paused, blocked, failed, and completed states. Repeating a completed run is an idempotent read. Retries are bounded at two attempts. Resume is accepted only from a paused approval run.

Primary roles: Director of Editorial Intelligence, Standards & Evidence Editor. Required tools: dossier, storydesk, dispatch, agents-sdk. Default permission: PROPOSE. Readiness: installable and verified for the locked offline fixture contract; catalog status remains Limited because operator-specific live adapters are not included.
