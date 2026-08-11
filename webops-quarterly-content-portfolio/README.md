# webops-quarterly-content-portfolio

Classify the content portfolio from graph, search, analytics, decay, pruning, and information-architecture evidence.

## Sequence

`ContentGraph → Search Performance Analyst → Analytics Analyst → Content Decay Analyst → Content Portfolio Manager → Content Pruning Analyst → Information Architecture Auditor → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-quarterly-content-portfolio && bash scripts/run.sh --fixture)
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

Merge, redirect, retire, or URL changes require separate ACT and migration approval.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
