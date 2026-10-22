# Workflows 0.6.2 release evidence

Verified on 2026-10-22 on the development macOS host, with Node 26.12.1.
This is a support/distribution technical preview; it does not certify hosted
execution or live providers.

## Passing checks

- Portable release-readiness and tracked clean-checkout gates pass. The full
  checkout runs 28 Python tests with two skips and 17 Codebase Cleanup tests.
  The standalone archive reports its documented missing-sibling skips.
- Full catalog resolves all 44 workflows; skill relationship contracts pass.
- Locked Publishing House clean installation and its all-eleven offline first
  run pass after aligning both compatibility and install-lock Skills references
  with the published 0.7.1 source, f972b6719104e279a42ee55a4beeee6bb0daaa62.
- VideoOps release gate passes real rendering, media inspection, contract gates,
  and bounded fail/repair/pass evaluation. Temporary outputs are cleaned on exit.
- Tribunal decision and Relay lifecycle handoff proofs pass.
- `KEEP_WORK=1 PORT=0 agency-runner/bin/agency-loop demo-verified-loop --strict`
  passes 34 stages, with one expected pre-fix failure, one warning for the
  deliberately unused live PackWrite route, and zero failed stages. The fixture
  includes real browser checks before and after its deterministic fix.

Additional current fixture checks pass: Dispatch approval routing, MCP guarded
scaffold generation, CaseFile evidence capture, Howl artifacts, Loop Engineering,
AI SDK with Watchdog, and AI SDK with Muzzle. The AI SDK checks explicitly remove
provider keys and use offline fixtures; Muzzle reports nine passing stages and
zero failures. Their temporary run roots are removed after preserving summaries.

## Current Workcell host blocker

`bash workcell-execution-gate/scripts/run.sh` exits 3 because the rootful Docker
host lacks required AppArmor support. Workcell run
`wc-7970bc291f684c588e9b1f3498612e29` records the blocked attempt and completed
cleanup. The work-package and completion contracts pass. The portable,
clean-install, Tribunal, Relay, and real-browser checks above are the closest
passing proofs; none substitutes for container isolation verification.

AGENTS.md explicitly permits a documented Docker/host blocker receipt with the
closest equivalent proof for this support-distribution launch. Historical
Workcell success is not claimed as a fresh 0.6.2 isolation result. No daemon
security requirements, tests, or release protections were weakened.

Detailed command logs are retained in the maintainer report collection
`~/.codex/reports/final-ten-releases-20261022`; they are local evidence, not
files promised to consumers of the source archive. Separate-machine,
live-provider, and hosted-runner qualification remains outside this preview.
