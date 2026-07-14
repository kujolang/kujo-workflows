# Tribunal decision gate

This reusable fixture workflow runs Tribunal's credential-free mock review,
verifies the persisted run, and maps the verified artifact set into the
workflow-facing `kujo.tribunal.decision-receipt/v1` contract.

The receipt is advisory and unsigned in mock mode. A production caller must
require signature/trust-policy verification before treating the decision as a
binding approval.

Run:

```bash
KUJO_BIN=/path/to/kujo tribunal-decision-gate/scripts/run.sh
```
