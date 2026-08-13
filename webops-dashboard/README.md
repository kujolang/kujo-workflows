# WebOps Dashboard

WebOps Dashboard turns WebOps run packets into a local SQLite-backed control
surface. It preserves the JSON and Markdown evidence as the audit source while
giving operators a SiteKit interface for findings, runs, workflow coverage,
agent roles, capability gaps, and Dither Kit charts.

## Start

```bash
python3 webops-dashboard/dashboard.py sync
python3 webops-dashboard/dashboard.py serve --open
```

The server binds to `127.0.0.1` by default. Its **Run report** form accepts an
HTTP(S) website, an allow-listed WebOps workflow, and `OBSERVE` or `PROPOSE`.
The browser never grants `ACT`; production changes remain outside this control
surface.

To import an existing run directly:

```bash
python3 webops-dashboard/dashboard.py import-run webops-weekly-site-health/.runs/<run-id>
```

Local state is stored under `.webops/dashboard/` and is intentionally ignored.
Use `--db` to choose another SQLite file. The database uses indexed relational
tables for sites, workflow manifests, agent contracts, runs, steps, findings,
and capability receipts. `PRAGMA optimize` runs after synchronization.

## Assets

- `public/sitekit/` is vendored from the supported SiteKit `dist/` artifact.
- `ui/components/dither-kit/` is source-vendored Dither Kit 0.1.1 component
  code, matching the established Watchdog integration.
- `public/assets/dither-charts.*` is the deterministic browser bundle generated
  by `npm run build:charts` in `ui/`.

## Verification

```bash
python3 -m unittest tests/test_webops_dashboard.py
(cd webops-dashboard/ui && npm ci && npm run build:charts)
python3 webops-dashboard/dashboard.py sync
```
