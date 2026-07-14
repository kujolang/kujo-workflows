# Deferred Opportunities

## Tribunal decision stage — P2

- Opportunity: optional adversarial review for high-impact feature, security, release, and architecture cards.
- Not implemented because: current cards have no stable docket schema, participant/threshold contract, dissent representation, human override, or verified resume adapter.
- Evidence needed: mock hearing plus `tribunal audit --trust-policy ... --require-signature --json`, decision packet schema mapping, and a paused-workflow resume test.
- Next action: define a versioned `decision-request/v1` artifact and make Tribunal advisory until an explicit approval policy binds it.

## Relay mission adapter — P2

- Opportunity: replace direct agent/shell execution with bounded mission state, event-chain evidence, typed tool results, and repair/resume.
- Not implemented because: Relay is hardened local alpha; no workflow owns a Relay mission schema, and authenticated service mode, durable concurrent storage, full Workcell recovery, and release gates remain open.
- Evidence needed: fixture mission pause/resume, `runs verify`, valid/partial export checks, approval denial, integrity tamper rejection, and a RunLedger handoff contract.
- Next action: add a dedicated adapter only after the mission package and ownership boundaries are approved.

## Workcell execution backend — P2

- Opportunity: execute agent work in a disposable container with declared resources, artifact export, immutable receipt, verification, and labeled cleanup.
- Not implemented because: Workcell is a local Docker MVP and its repository documents trusted host/daemon assumptions; Relay and Workcell do not yet provide a complete shared recovery contract.
- Evidence needed: definition validation/inspection, offline test suite, receipt verification, cleanup failure handling, and Docker/Podman backend evidence where available.
- Next action: define a Workcell-backed workflow package with explicit repo cleanliness, network, image provenance, resource, artifact, and cleanup policy.

## “Workso” naming — P3

- No repository, manifest, or skill named `Workso` was found. The current repository is `workcell`, with skill `kujo-workcell-workflows`.
- Do not create a compatibility alias until the product owner confirms whether Workso is a rename, a separate tool, or a prompt typo.

## Additional under-tested relationships — P2

- Agency Runner, DocsGen, and RAG workflows are cataloged as compatible but under-tested because their current scripts have fixture/manual coverage rather than a repository-wide contract suite.
- Next action: add deterministic negative fixtures for missing binaries, malformed outputs, absent artifacts, and redaction leakage before changing readiness to production-ready.
