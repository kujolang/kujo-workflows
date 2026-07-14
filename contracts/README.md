# Cross-tool contracts

These JSON contracts are the workflow-facing boundary for Tribunal, Relay, and
Workcell. They are intentionally additive: consumers must ignore unknown
properties, while producers must preserve the required identifiers,
provenance, redaction, idempotency, and error fields.

The contracts describe the evidence exchanged by the workflows. They do not
upgrade a tool's operational guarantees. In particular:

- Tribunal receipts may be unsigned in local mock mode; signature verification
  is a separate gate.
- Relay records local durable state and bounded retries, but does not claim
  remote exactly-once delivery.
- Workcell receipts describe a bounded Docker/Podman attempt; they do not imply
  microVM or hosted isolation.

Validate the schemas and examples with:

```bash
python3 scripts/validate_contracts.py
```

Contract IDs are stable within the `v1` family. Additive fields are preferred;
breaking changes require a new contract version and a migration note.
