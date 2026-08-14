# Publishing House validation record

Captured on 2026-08-14 from
`codex/publishing-house-core-workflows`. Generated run directories were kept
outside the repository or under ignored `.runs/` paths.

| Command | Exit | Result |
| --- | ---: | --- |
| `python3 scripts/validate_catalog.py --json` | 0 | 34 workflows; no catalog errors |
| `python3 scripts/validate_contracts.py` | 0 | 19 schemas, 16 examples, 314 required-field negative checks |
| `python3 scripts/validate_docs.py` | 0 | 123 Markdown files and 10 release files |
| `bash scripts/run-publishing-house-fixture.sh --out <temporary-directory>` | 0 | 8 workflows, 36 resolved record references, 22 exact 0.2.0 tool-contract preflights, 26 agent receipts, matching approval/publication checksum |
| `bash tests/publishing-house-install.sh` | 0 | tracked-only workflow archive installed with ten clean locked dependency checkouts; Kujo-native doctor and all-eight fixture passed from the final install path with resolvable references |
| `bash publishing-house-approval-publication/scripts/test.sh` | 0 | pause, fixture approval resume, bounded local effect, repeated resume/idempotent read |
| Dispatch `sdk_adapter_tests`, `policy_precedence_tests`, and `dispatch_tests` | 0 | 8 + 3 + 99 tests passed against commit in compatibility matrix |
| Agents SDK runner, integration adapter, no-network, example, and CI no-network suites | 0 | selected suites and all 23 no-network enforcement fixtures passed |
| `bash tribunal-decision-gate/scripts/run.sh` | 0 | decision receipt passed |
| `bash relay-lifecycle-handoff/scripts/run.sh` | 0 | message and delivery receipts passed |
| `bash workcell-execution-gate/scripts/run.sh` | 0 | bounded Docker execution passed through Colima/Docker 29.5.2 |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 0 | 23 tests passed against clean worktrees at the exact compatibility-matrix commits |
| `git diff --check` | 0 | no whitespace errors |

Agency Runner now preserves operator-selected evaluation suggestions without
emitting the retired `manual_or_project_command` check type, so strict current
Spec validation passes. No sibling repository was modified. Clean detached
worktrees were used for the eight tools because unrelated changes were present
in two sibling working trees; the tested commits and versions are recorded in
the compatibility matrix.
