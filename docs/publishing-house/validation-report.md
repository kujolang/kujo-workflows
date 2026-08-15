# Publishing House validation record

Captured on 2026-08-14 from the `main` branch. Generated run directories were
kept outside the repository or under ignored paths.

| Command | Exit | Result |
| --- | ---: | --- |
| `python3 scripts/validate_catalog.py --json` | 0 | 37 workflows; no catalog errors |
| `python3 scripts/validate_contracts.py` | 0 | 19 schemas, 16 examples, 314 required-field negative checks |
| `python3 scripts/validate_docs.py` | 0 | 131 Markdown files and 10 release files |
| `bash scripts/run-publishing-house-fixture.sh --out <temporary-directory>` | 0 | 11 workflows, 46 resolved record references, 34 exact tool-contract preflights, 38 contract-loaded agent receipts, matching approval/publication checksum |
| `bash tests/publishing-house-install.sh` | 0 | tracked-only archive installed with twelve clean locked dependency checkouts; Kujo-native doctor and all-eleven fixture passed from the final install path |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 0 | 24 tests passed against the exact compatibility-matrix commits |
| `bash tests/release-readiness.sh` | 0 | documentation, static, catalog, contract, unit, codebase-cleanup, artifact, and whitespace gates passed |

Every Agents SDK receipt proves that the canonical house contracts, role
contract, role skill, and Publishing House workflow skill were loaded by
matching the instruction checksum returned by the runner. Fixture execution is
offline and credential-free. PressWire performs only the bounded local fixture
copy; live external provider and destination adapters remain operator-owned and
must pass separate review before use.
