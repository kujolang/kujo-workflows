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

## Independent negative fixtures for nine under-tested relationships — P2

- The strict Agency packet, DocsGen packet, and RAG packet now provide stronger
  positive/operational evidence, but Agency's optional phases still share one
  composite runner and its PatchBrief/ChangeBucket/ShipCheck calls are blocked
  by the current Kujo `cli` module-resolution issue.
- Next action: add per-skill missing-binary, malformed-output, absent-artifact,
  and redaction-leak fixtures before promoting any of the nine relationships to
  fully compatible.
