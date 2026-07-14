# Phase 2 evidence — 2026-07-14

## Relay aggregate acceptance

Reproduction before the fix:

```text
KUJO=../kujo/target/release/kujo bash relay/tests/relay_acceptance.sh
first failure: relay_agents_tool_smoke.sh (exit 1)
```

The direct contract suite passed. Tracing the failing smoke test showed that
the script accepted an explicit absolute `KUJO` path but did not export the
same value as `KUJO_BIN`. The Agents SDK bridge therefore compared the payload
runtime with its relative trusted default and rejected the call with:
`Agents SDK worker binary must match trusted KUJO_BIN`.

Fix: Relay commit `7ead89a` exports `KUJO_BIN="$KUJO"` in
`tests/relay_agents_tool_smoke.sh`. Direct absolute-path smoke and the complete
25-script aggregate then passed. The fix was pushed to Relay `main`.

## Browser loop

`PORT=0 STRICT=1 bash agency-verified-fix-loop/scripts/run-loop.sh` produced
run packet `.runs/20260714T023325Z` with:

- 27 passed stages, one expected failure, one warning, and seven explicitly
  failed external-tool stages.
- The pre-fix Lens flow exited 1 as expected after the loop began using a free
  port. Previously a stale PHP process on port 8099 served a fixed fixture and
  made the expected failure report exit 0.
- Eval, Eval manifest verification, Lens check, inspect, and recorded proof
  passed. Proof: `.runs/20260714T023325Z/lens/proof/walkthrough.html`.
- PatchBrief, ChangeBucket, and ShipCheck remain blocked by the checked-out
  Kujo runtime's `cli` module resolution (`Module not found: cli` and
  `Circular import detected: cli -> cli`). The loop records these as failures;
  it does not convert them to warnings or claim a complete tool packet.

The agency runner strict demo repeated the browser result in
`.runs/20260714T023639Z/summary.md`.

## Under-tested skill relationships

The following nine relationships received stronger fixture evidence while
remaining under-tested rather than being promoted without independent
negative coverage:

- Agency Runner → Spec, Scout, Scent, Lens, CaseFile, PackWrite, RunLedger:
  strict demo packet `.runs/20260714T023639Z/summary.md`, with CaseFile and
  RunLedger receipts preserved. PackWrite remains a warning; the optional
  external tool failures are recorded.
- DocsGen → `kujo-docgen-agent-readable`: successful packet
  `.runs/20260714T023826Z/SUMMARY.md`.
- RAG gate → `kujo-rag-workflows`: successful packet
  `.runs/20260714T023826Z/SUMMARY.md`.

## Contract and integration evidence

`python3 scripts/validate_contracts.py` validates five schemas and five
examples, including required-field negative checks and additive-field
forward-compatibility checks. The three new gates validate their generated
instances against those schemas. Tribunal, Relay, and Workcell all have a
dedicated, non-placeholder integration workflow.

Workcell executed successfully in the local Docker backend during this phase;
the earlier mapped-user permission failure was reproduced during diagnosis,
but the final gate used the platform temp root and produced a verified
completion receipt. This does not expand Workcell's documented isolation or
recovery guarantees.
