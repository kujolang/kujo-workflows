# Publishing House Editorial Review and Revision

Review an exact GalleyPack version, preserve independent findings, route bounded changes, and recommend an exact package for approval.

## Boundary

BluePencil verdicts and editorial recommendations do not constitute human publication approval. Record ownership remains with bluepencil, dossier, galleypack, storydesk; this workflow stores references and orchestration receipts only.

## Run the deterministic fixture

```bash
(cd publishing-house-editorial-review && bash bin/run --request fixtures/request.fixture.json --json)
```

Fixture mode is offline, credential-free, deterministic, and cannot target a live destination. Live mode must be explicit and fails closed until compatible adapters are configured; it never falls back to fixture behavior.

## Inputs and outputs

The request supplies portable House, Brand, and Audience profiles, permission, capabilities, correlation IDs, and tool record references. Outputs include capability, agent-step, tool, Dispatch, summary, blocker or completion receipts under the selected run directory.

## State and recovery

state.json records running, paused, blocked, failed, and completed states. Repeating a completed run is an idempotent read. Retries are bounded at two attempts. Resume is accepted only from a paused approval run.

Primary roles: Developmental Editor, Standards & Evidence Editor, Brand Strategy Director, Copy Chief, Editor-in-Chief. Required tools: bluepencil, dossier, galleypack, storydesk, dispatch, agents-sdk. Default permission: PROPOSE. Readiness: Limited technical preview; fixture evidence is verified locally, while live adapters and live-provider execution remain environment-specific.

