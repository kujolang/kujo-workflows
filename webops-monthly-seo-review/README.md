# webops-monthly-seo-review

Synthesize monthly specialist SEO evidence without duplicating specialist analysis.

## Sequence

`SEO Auditor → Search Performance Analyst → Indexation Analyst → Technical SEO Auditor → Content Decay Analyst → Cannibalization Analyst → Internal Link Specialist → Schema Auditor → Metadata Auditor → Performance Analyst → Backlink & Mention Analyst → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-monthly-seo-review && bash scripts/run.sh --fixture)
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

Synthesis is OBSERVE; proposed fixes route to finding-to-fix.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
