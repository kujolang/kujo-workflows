# webops-site-bootstrap

Establish a credential-free initial website, repository, content-graph, browser, and reporting baseline.

## Sequence

`Site Profile → Capability Preflight → SiteProbe → Scout → ContentGraph → RAG → Site QA Operator → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-site-bootstrap && bash scripts/run.sh --fixture)
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

Repository access is read-only; authenticated browser state is optional and external.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
