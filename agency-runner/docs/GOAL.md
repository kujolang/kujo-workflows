# Goal

Agency Runner turns Kujo primitives into a real agency workflow:

```text
Human starts task
Agent performs the middle loop
Human reviews proof packet
Human sends handoff
```

It reuses the verified-fix-loop ideas:

- Spec for task contracts.
- Scout and Scent for context.
- Lens and CaseFile for browser proof and failure capture.
- Eval for deterministic checks.
- PatchBrief, ChangeBucket, and ShipCheck for review gates.
- RunLedger for audit trail.

The prototype proves the command shape and artifact contract before becoming a native `kujo agency` command.
