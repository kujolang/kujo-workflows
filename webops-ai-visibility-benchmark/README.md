# webops-ai-visibility-benchmark

Run a fixed longitudinal query suite across explicitly available AI/search surfaces without fabricated availability.

## Sequence

`Capability Preflight → AI Search Visibility Analyst → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-ai-visibility-benchmark && bash scripts/run.sh --fixture)
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

Live provider cost and terms; unavailable surfaces are skipped.

Current readiness: **experimental**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
