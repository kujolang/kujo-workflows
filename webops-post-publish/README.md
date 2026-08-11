# webops-post-publish

Verify newly published content, relationships, rendered quality, optional submission, distribution assets, and receipts.

## Sequence

`SiteProbe → Metadata Auditor → Schema Auditor → Internal Link Specialist → Site QA Operator → Search Submission Operator → Distribution Operator → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-post-publish && bash scripts/run.sh --fixture)
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

Search submission and distribution publishing require explicit ACT; fixture mode creates receipts/assets only.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
