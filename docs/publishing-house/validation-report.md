# Publishing House validation record

Captured on 2026-08-14 from
`codex/publishing-house-core-workflows`. Generated run directories were kept
outside the repository or under ignored `.runs/` paths.

| Command | Exit | Result |
| --- | ---: | --- |
| `python3 scripts/validate_catalog.py --json` | 0 | 34 workflows; no catalog errors |
| `python3 scripts/validate_contracts.py` | 0 | 19 schemas, 16 examples, 314 required-field negative checks |
| `python3 scripts/validate_docs.py` | 0 | 123 Markdown files and 10 release files |
| `bash scripts/run-publishing-house-fixture.sh --out <temporary-directory>` | 0 | 8 workflows, 36 resolved record references, 26 agent receipts, matching approval/publication checksum |
| `bash publishing-house-approval-publication/scripts/test.sh` | 0 | pause, fixture approval resume, bounded local effect, repeated resume/idempotent read |
| Dispatch `sdk_adapter_tests`, `policy_precedence_tests`, and `dispatch_tests` | 0 | 8 + 3 + 99 tests passed against commit in compatibility matrix |
| Agents SDK runner, integration adapter, no-network, example, and CI no-network suites | 0 | selected suites and all 23 no-network enforcement fixtures passed |
| `bash tribunal-decision-gate/scripts/run.sh` | 0 | decision receipt passed |
| `bash relay-lifecycle-handoff/scripts/run.sh` | 0 | message and delivery receipts passed |
| `bash workcell-execution-gate/scripts/run.sh` | 1 | host blocker: Docker API socket unavailable; validate and inspect passed and `.runs/workcell-execution-gate/run-result.json` records the failed preparing boundary |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 1 | 21 of 22 passed; one pre-existing cross-repository Spec compatibility test remains blocked because Spec rejects `manual_or_project_command` emitted by Agency Runner |
| `git diff --check` | 0 | no whitespace errors |

The Workcell result is a host-capability blocker, not Publishing House success.
The Agency Runner/Spec mismatch reproduced before Publishing House changes and
is outside this workflow implementation. No sibling repository was modified.
All Publishing House-specific tests and the all-eight fixture pass after the
record-reference fix.
