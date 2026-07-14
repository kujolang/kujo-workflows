# Tribunal, Relay, and Workcell Review

## Tribunal

Repository evidence: `README.md`, `docs/OPERATIONS.md`, `docs/ENTERPRISE_READINESS.md`, `docs/THREAT_MODEL.md`, `tribunal.kujo`, `schemas/*.json`, and test/gate inventories. Tribunal v0.7.0 is a local-first adversarial hearing engine with specialist testimony, cross-examination, fatal-flaw pass, ruling, decision packet, sealed manifests, optional signatures, trust-policy audit, immutable run artifacts, and stopped-hearing resume. The contract is advisory or binding only as the consuming workflow policy defines; the tool does not supply a generic workflow approval quorum or hosted multi-tenant service. The current posture is operator-controlled local use; deployment certification remains separate.

Disposition: the dedicated `tribunal-decision-gate` now proves a safe advisory integration and validates `contracts/tribunal/decision-receipt.v1.schema.json`. Existing feature/release workflows remain unchanged until a signed docket, participant authority, binding policy, and resume contract are approved.

## Relay

Repository evidence: `README.md`, `docs/command-reference.md`, `docs/integration-matrix.md`, `main.kujo`, `src/`, `schemas/`, and `tests/relay_*`. Relay v0.1.0 is a hardened local alpha composition/execution layer. It provides bounded missions, PackWrite packet manifests, JSONL events, sealed receipts, RunLedger/ChangeBucket/Eval reports, pause/resume/cancel, bounded repairs, direct-argv policy, redaction, correlation IDs, run-index integrity, and verified export. It does not prove exactly-once remote delivery; its current contract is local mission evidence, not a provider-neutral message broker. Authenticated service mode, durable concurrent storage, full Workcell isolation/recovery, and release gates remain open.

Disposition: the dedicated `relay-lifecycle-handoff` proves a worktree mission pause/resume, integrity-checked export, correlated message envelope, delivery receipt, and cleanup. It is intentionally local and optional; it does not replace existing handoffs or claim remote exactly-once delivery.

## Workcell (the actual tool found for “Workso”)

Repository evidence: `README.md`, `docs/security-model.md`, `docs/workcell-definition.md`, `docs/runtime-lifecycle.md`, `main.kujo`, `src/`, `workcell.json`, and `tests/`. Workcell v0.1.0 creates disposable Git worktrees, runs declared commands in Docker/Podman with bounded resources and restrictive defaults, exports declared artifacts, writes receipts/manifests, verifies evidence, and cleans labeled resources. It rejects dirty source trees, does not provide microVM isolation, and trusts the host Docker daemon/kernel. Cleanup and completion outcomes are distinct in the receipt.

Disposition: the dedicated `workcell-execution-gate` validates a clean fixture, inspects the security policy, runs Docker, and validates versioned package/completion receipts. It is an optional execution backend, not a drop-in replacement or scheduler; no “Workso” tool was found.
