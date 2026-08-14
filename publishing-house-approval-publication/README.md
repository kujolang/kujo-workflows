# Publishing House Approval and Publication

Freeze the exact package, pause for human approval, bind the decision to its checksum, and permit only an authorized PressWire action.

## Boundary

A real VersionSeal decision is required in live mode; fixture approval is explicitly labeled and authorizes only the bounded local fixture destination. Record ownership remains with galleypack, versionseal, presswire, storydesk; this workflow stores references and orchestration receipts only.

## Run the deterministic fixture

```bash
(cd publishing-house-approval-publication && bash bin/run --request fixtures/request.fixture.json --json)
```

The first command pauses. Resume the same run with:

```bash
(cd publishing-house-approval-publication && bash bin/run --request fixtures/request.fixture.json --out .runs/run-fixture-approval-publication --resume --fixture-approval "$(cd .. && pwd)/fixtures/publishing-house/fixture-approval.fixture.json" --json)
```

Fixture mode is offline, credential-free, deterministic, and cannot target a live destination. Live mode must be explicit and fails closed until compatible adapters are configured; it never falls back to fixture behavior.

## Inputs and outputs

The request supplies portable House, Brand, and Audience profiles, permission, capabilities, correlation IDs, and tool record references. Outputs include capability, agent-step, tool, Dispatch, summary, blocker or completion receipts under the selected run directory.

## State and recovery

state.json records running, paused, blocked, failed, and completed states. Repeating a completed run is an idempotent read. Retries are bounded at two attempts. Resume is accepted only from a paused approval run.

Primary roles: Production Editor, Publishing Operations Director. Required tools: galleypack, versionseal, presswire, storydesk, dispatch, agents-sdk. Default permission: PROPOSE. Readiness: installable and verified for the locked offline fixture contract; catalog status remains Limited because real human approval and operator-specific live publication adapters are not included.
