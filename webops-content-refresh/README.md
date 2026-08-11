# webops-content-refresh

Turn decay and accuracy evidence into a Spec, approved update boundary, verification, and future measurement cue.

## Sequence

`Content Decay Analyst → Content Accuracy Reviewer → Search Performance Analyst → ContentGraph → Spec → Authorized Content Update → Eval → Site QA Operator → Search Submission Operator → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-content-refresh && bash scripts/run.sh --fixture)
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

Content mutation and submission pause for separate role-bounded ACT approval.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
