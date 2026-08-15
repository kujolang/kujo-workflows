# How to run Publishing House Format Production

1. Read `README.md` and `workflow.json`.
2. Run `bash bin/run --request fixtures/request.fixture.json --json`.
3. Reuse `--out <path>` to inspect idempotent completion; never overwrite unrelated paths.
4. Inspect `capability-receipt.json`, `agent-contracts/`, `agent-receipts/`, `tool-receipts/`, `dispatch/`, `run-summary.json`, and `completion-receipt.json`.
5. Run `bash scripts/test.sh` after changes.
