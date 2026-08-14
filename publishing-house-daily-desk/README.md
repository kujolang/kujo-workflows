# Publishing House Daily Desk

Validate a daily editorial packet, inspect queue state, and route each actionable item to the narrowest child workflow.

## Boundary

No publication authority; routing may occur under PROPOSE. Record ownership remains with storydesk; this workflow stores references and orchestration receipts only.

## Run the deterministic fixture

```bash
(cd publishing-house-daily-desk && bash bin/run --request fixtures/request.fixture.json --json)
```

Fixture mode is offline, credential-free, deterministic, and cannot target a live destination. Live mode must be explicit and fails closed until compatible adapters are configured; it never falls back to fixture behavior.

## Inputs and outputs

The request supplies portable House, Brand, and Audience profiles, permission, capabilities, correlation IDs, and tool record references. Outputs include capability, agent-step, tool, Dispatch, summary, blocker or completion receipts under the selected run directory.

## State and recovery

state.json records running, paused, blocked, failed, and completed states. Repeating a completed run is an idempotent read. Retries are bounded at two attempts. Resume is accepted only from a paused approval run.

Primary roles: Managing Editor, Commissioning Editor, Production Editor. Required tools: storydesk, dispatch, agents-sdk. Default permission: PROPOSE. Readiness: Limited technical preview; fixture evidence is verified locally, while live adapters and live-provider execution remain environment-specific.

