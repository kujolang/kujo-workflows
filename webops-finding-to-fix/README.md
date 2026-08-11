# webops-finding-to-fix

Move one stable WebOps finding through Spec, proposal, approval, implementation boundary, Eval, Lens, SiteProbe, and receipt evidence.

## Sequence

`WebOps Finding → Spec → Proposal → Approval Gate → Implementation → Eval → Site QA Operator → SiteProbe → WebOps Reporter`

## Run fixture mode

```bash
(cd webops-finding-to-fix && bash scripts/run.sh --fixture)
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

Implementation and any production mutation require explicit role-bounded ACT; fixture mode produces proposal and proof plan.

Current readiness: **production-capable-with-limitations**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
