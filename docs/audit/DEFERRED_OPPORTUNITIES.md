# Deferred Opportunities

## Feature card → Tribunal binding policy — P2

- Opportunity: bind Tribunal review to high-impact feature, security, release,
  and architecture cards.
- Not implemented because: the advisory decision receipt exists, but authority
  for participants, threshold, dissent handling, human override, and paused
  workflow resume is still a product/governance decision.
- Next action: define a signed decision-request contract and a binding policy;
  keep the current gate advisory until then.

## Relay external provider delivery — P2

- Opportunity: deliver workflow handoffs across repositories or external
  providers with acknowledgements and dead-letter recovery.
- Not implemented because: the inspected Relay guarantees cover local durable
  state, bounded retries/repair, and operator resume; strict remote delivery
  semantics are not established by the current implementation.
- Next action: add a provider adapter only after sender/recipient
  authorization, acknowledgment, deduplication, dead-letter, and callback
  contracts are implemented and tested.

## Relay smoke cleanup and fixture setup — P1

- Opportunity: make Relay aggregate acceptance and provider-tool smoke fully
  exit-clean after printing their PASS evidence.
- Not implemented because: the 2026-07-25 audit was scoped to workflow-catalog
  drift and found this in the sibling Relay repository, not in a workflow
  artifact. `relay_provider_tool_smoke.sh` still printed PASS but did not
  exit cleanly before interruption, and `relay_lock_stress_smoke.sh` failed
  before lock assertions because `examples/fixture-mission.json` references a
  missing `/tmp/relay-fixture-workspace`.
- Next action: fix the sibling Relay smoke fixture setup and process cleanup,
  then rerun `tests/relay_acceptance.sh` before promoting any Relay acceptance
  claim beyond partial verification.

## Workcell scheduling and reassignment — P2

- Opportunity: parallel workcells with worker ownership, cancellation,
  reassignment, and conflict prevention.
- Not implemented because: Workcell is a local bounded Docker/Podman executor;
  no scheduler or safe reassignment contract was found.
- Next action: keep orchestration in Dispatch/Relay and add a Workcell adapter
  only when lifecycle ownership and workspace conflict policy are explicit.

## “Workso” naming — P3

- No repository, manifest, or skill named `Workso` was found. The canonical
  implementation is `workcell`, with skill `kujo-workcell-workflows`.
- Do not create an alias without product confirmation.

## Promotion of nine under-tested relationships — P2

- Positive and negative boundary fixtures now cover Spec, Scout, Scent, Lens,
  CaseFile, PackWrite, RunLedger, DocsGen, and RAG in
  `tests/skill_relationship_contracts.sh`. The relationships remain
  under-tested because the fixture suite does not prove live provider behavior,
  authenticated browser execution through every Agency Runner phase, or
  production artifact consumers.
- Next action: add provider-backed, authenticated-browser, and consumer-level
  receipts before promoting any relationship to fully compatible.
