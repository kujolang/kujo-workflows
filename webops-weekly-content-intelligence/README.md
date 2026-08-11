# webops-weekly-content-intelligence

Combine trends, query opportunity, content relationships, gaps, accuracy, and internal-link proposals.

## Sequence

`Trend Scout → Keyword Opportunity Analyst → ContentGraph → Content Gap Analyst → Content Accuracy Reviewer → Internal Link Specialist → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-weekly-content-intelligence && bash scripts/run.sh --fixture)
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

Internal-link source changes require a separate ACT run.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
