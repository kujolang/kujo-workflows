# Publishing House Governance

Set a bounded house mandate, portfolio decision, operating priorities, and accountable handoffs without replacing human approval.

## Boundary

Governance may commission, defer, revise, or decline work under PROPOSE; it cannot approve or publish artifacts.

## Run the deterministic fixture

```bash
(cd publishing-house-governance && bash bin/run --request fixtures/request.fixture.json --json)
```

Fixture mode is offline, deterministic, credential-free, and cannot target a live destination. Live mode must be explicit and fails closed until compatible operator adapters are configured; it never falls back to fixture behavior.

## Inputs and outputs

The request supplies portable House, Brand, and Audience profiles, permission, capabilities, correlation IDs, and tool record references. Outputs include capability, contract-loaded agent-step, tool, Dispatch, summary, blocker, or completion receipts under the selected run directory.

Primary roles: Publisher, Editor-in-Chief, Managing Editor. Required tools: storydesk, dossier, dispatch, agents-sdk. Default permission: PROPOSE.
