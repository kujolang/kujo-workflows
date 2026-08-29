# Publishing House validation record

Captured on 2026-08-29 from the `main` branch. Generated run directories were
kept outside the repository or under ignored paths.

| Command | Exit | Result |
| --- | ---: | --- |
| `python3 scripts/validate_catalog.py --json` | 0 | 38 workflows; no catalog errors |
| `python3 scripts/validate_contracts.py` | 0 | 19 schemas, 16 examples, 314 required-field negative checks |
| `python3 scripts/validate_docs.py` | 0 | 137 Markdown files and 10 release files |
| `bash scripts/run-publishing-house-fixture.sh --out <temporary-directory>` | 0 | 11 workflows, 46 resolved record references, 34 exact tool-contract preflights, 38 contract-loaded agent receipts, matching approval/publication checksum; timed direct run completed in 431.24 seconds |
| `bash tests/publishing-house-install.sh` | not run | Separate clean-install proof remains covered by the 2026-08-22 record until rerun |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | 0 | 24 tests passed in 667.352 seconds after stale Publishing House fixture timeout was raised to 600 seconds |
| `bash tests/release-readiness.sh` | not run | Full release-readiness gate is outside this weekly drift slice |

The 2026-08-29 refresh advanced the locked `kujo`, Dispatch, Agents SDK,
`kujo-agents`, and `kujo-skills` checkouts after Agent Project, router,
conversion-metadata, provider-neutral adapter, and skill-audit commits;
`kujo-publishing-house-workflows` itself was not changed by those sibling
commits. Every Agents SDK receipt from the fixture proof proves that the
canonical house contracts, role contract, role skill, and Publishing House
workflow skill were loaded by matching the instruction checksum returned by
the runner. Fixture execution is offline and credential-free. PressWire
performs only the bounded local fixture copy; live external provider and
destination adapters remain operator-owned and must pass separate review before
use.
