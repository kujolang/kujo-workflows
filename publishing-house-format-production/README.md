# Publishing House Format Production

Produce reviewable newsletter, social, case-study, and video/audio packages from approved source lineage.

## Boundary

Format production creates proposals and packages only; it cannot publish, infer consent, or expand claims beyond approved evidence.

## Run the deterministic fixture

```bash
(cd publishing-house-format-production && bash bin/run --request fixtures/request.fixture.json --json)
```

Fixture mode is offline, deterministic, credential-free, and cannot target a live destination. Live mode must be explicit and fails closed until compatible operator adapters are configured; it never falls back to fixture behavior.

## Inputs and outputs

The request supplies portable House, Brand, and Audience profiles, permission, capabilities, correlation IDs, and tool record references. Outputs include capability, contract-loaded agent-step, tool, Dispatch, summary, blocker, or completion receipts under the selected run directory.

Primary roles: Newsletter Editor, Social & Community Editor, Case Study Editor, Video & Audio Producer, Production Editor. Required tools: storydesk, dossier, galleypack, bluepencil, assetworks, dispatch, agents-sdk. Default permission: PROPOSE.
