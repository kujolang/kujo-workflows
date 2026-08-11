# webops-weekly-search-intelligence

Compare measured search evidence, keyword opportunities, and decay signals with capability-level degradation.

## Sequence

`SearchBridge → Search Performance Analyst → Keyword Opportunity Analyst → Content Decay Analyst → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-weekly-search-intelligence && bash scripts/run.sh --fixture)
```

Use `--site-profile ../fixtures/webops/site-profile.fixture.json`, `--out`,
`--permission OBSERVE|PROPOSE|ACT`, and `--resume` as needed. Fixture mode is
offline, deterministic, and never requires paid credentials. Live mode uses
the same profile and capability preflight but never expands authority.

## Evidence and recovery

The run packet contains state, capability receipt, step receipts, stable
findings, quiet report, and run receipt. Completed steps are resumable. A
missing optional capability records `skipped-degraded`; an ACT boundary records
`approval-required` rather than pretending the action occurred.

## Approval boundary

Provider cost and property access; fixture mode is credential-free.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
