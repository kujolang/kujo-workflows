# webops-weekly-site-health

Compare weekly crawl and rendered site health, links, performance, accessibility, schema, and metadata.

## Sequence

`SiteProbe → Site QA Operator → Link Health Auditor → Performance Analyst → Accessibility Auditor → Schema Auditor → Metadata Auditor → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-weekly-site-health && bash scripts/run.sh --fixture)
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

No site mutation; optional provider credentials enable performance modules only.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
