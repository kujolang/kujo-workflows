# Verification

Captured during the audit on 2026-07-13 local time.

## Passed automatically

- `python3 scripts/validate_catalog.py --json` — PASS; 12 workflows, no errors.
- `python3 -m unittest discover -s tests -p 'test_*.py'` — PASS; 3 tests.
- `bash tests/validate_catalog.sh` — PASS.
- `python3 -m json.tool docs/audit/*.json` — PASS for all audit JSON files.
- `bash -n` over every tracked `*.sh` in this repository — PASS.
- `git diff --check` — PASS.
- Six catalog workflow runners — PASS: enterprise Dispatch approval router, MCP gateway review, RAG knowledge gate, CaseFile evidence packet, Howl content factory, and DocsGen contract runner. Each wrote a timestamped `.runs/<timestamp>/` packet and completed with exit code 0.
- Workcell `KUJO=<checkout>/kujo/target/release/kujo ./tests/run.sh --check-only` — PASS; all listed Kujo source and contract files checked.
- Tribunal doctor, docket validation, mock review, and unsigned integrity verification — PASS. Mock run `2026-07-14-product-decision-md-8737` verified 21 artifacts with no mismatches; signature was absent as expected for the unsigned fixture.
- Relay contract suite — PASS when run directly with the pinned Kujo runtime; the suite emitted its contract PASS cases and returned 0.

## Partially verified or blocked

- Relay aggregate `bash tests/relay_acceptance.sh` — NOT CLAIMED PASS. The aggregate returned exit 1 in this environment after individual contract/smoke output; concurrent or generated `.relay` state was present during repeated probes, so no Relay workflow integration was based on that result. Re-run from a clean isolated Relay checkout and preserve the first failing smoke log.
- `STRICT=1 bash agency-verified-fix-loop/scripts/run-loop.sh` — PARTIAL. Preflight, Spec, Scout, Scent, PackWrite dry-run, RunLedger, and PHP server stages passed before the long-running browser stage exceeded the command window; no full completion claim is made.
- Docker/Podman Workcell runtime execution — NOT RUN; only source/contract checks were run. No Docker host certification is implied.
- Live provider paths for AI SDK, Watchdog, Relay, PackWrite, and Tribunal — NOT RUN; credentials and provider cost were intentionally not used.
