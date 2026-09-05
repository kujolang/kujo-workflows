# Publishing House validation record

Captured on 2026-09-05 from the `main` branch. Generated run directories were
kept outside the repository or under ignored paths.

| Command | Exit | Result |
| --- | ---: | --- |
| `python3 scripts/validate_catalog.py --json` | 0 | 44 workflows; no catalog errors |
| `python3 scripts/validate_contracts.py` | 0 | 19 schemas, 16 examples, 314 required-field negative checks |
| `python3 scripts/validate_docs.py` | 0 | 181 Markdown files and 10 release files |
| `bash scripts/run-publishing-house-fixture.sh --out <temporary-directory>` | 0 | Covered through `python3 -m unittest discover -s tests -p 'test_*.py'`; initial pass exposed a stale `kujo-skills` lock, and the refreshed lock passed |
| `bash tests/publishing-house-install.sh` | not run | Separate clean-install proof remains covered by the 2026-08-22 record until rerun |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 0 | 24 tests passed in 347.645 seconds after the stale `kujo-skills` support-lock commit was advanced to `0d41ab4` |
| `bash tests/release-readiness.sh` | 0 | Release-readiness validation passed, including static validation, structure-only catalog validation, contract validation, unit tests, Codebase Cleanup Kujo tests, and `git diff --check` |

The 2026-09-05 refresh advanced the locked `kujo-skills` checkout from the
VideoOps skill-pack commit to the clean weekly skill-drift commit; the
Publishing House workflow skill itself remained available and compatible. Every
Agents SDK receipt from the fixture proof proves that the
canonical house contracts, role contract, role skill, and Publishing House
workflow skill were loaded by matching the instruction checksum returned by
the runner. Fixture execution is offline and credential-free. PressWire
performs only the bounded local fixture copy; live external provider and
destination adapters remain operator-owned and must pass separate review before
use.
