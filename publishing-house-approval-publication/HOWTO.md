# How to operate Publishing House Approval and Publication

1. Copy fixtures/request.fixture.json and replace profile and input references with portable operator-owned files.
2. Declare every required capability honestly and select fixture or live mode explicitly.
3. Run bash bin/run --request REQUEST.json --out RUN_DIRECTORY --json.
4. Inspect capability-receipt.json, agent-receipts/, tool-receipts/, dispatch/, run-summary.json, and completion-receipt.json.
5. If blocked, correct the named capability, authority, reference, or checksum; do not edit consequential history.
6. At the pause, review approval-pause.json. Resume only with an exact VersionSeal decision. The checked-in approval file is fixture data, not live human approval.

Copyable Kujo command:

```bash
(cd publishing-house-approval-publication && KUJO_MODULE_PATH=.. KUJO_BIN=../kujo/target/release/kujo ../kujo/target/release/kujo run workflow.kujo -- --request fixtures/request.fixture.json --json)
```

Failures are classified as unavailable, unsupported, blocked, rejected, skipped, failed, or completed. Unsafe paths, secret-shaped fields, incompatible schemas, missing capabilities, permission broadening, and checksum drift fail closed.

