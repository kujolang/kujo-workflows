#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "webops-dashboard" / "dashboard.py"
SPEC = importlib.util.spec_from_file_location("webops_dashboard", MODULE_PATH)
dashboard = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(dashboard)


class WebOpsDashboardTests(unittest.TestCase):
    def make_run(self, root: Path) -> Path:
        run = root / "webops-weekly-site-health" / ".runs" / "20260813T120000Z"
        run.mkdir(parents=True)
        values = {
            "profile.json": {"site": {"id": "example", "url": "https://example.com", "platform": "live-website"}},
            "state.json": {"started_at": "2026-08-13T12:00:00Z", "steps": [{"index": 1, "step": "SiteProbe", "status": "completed", "detail": ""}]},
            "run-receipt.json": {"workflow": "webops-weekly-site-health", "run_id": "20260813T120000Z", "verdict": "success", "permission": "OBSERVE", "fixture": False, "completed_at": "2026-08-13T12:01:00Z"},
            "findings.json": {"findings": [{"id": "WF-123", "agent": "Technical SEO Auditor", "check": "missing-description", "target": "https://example.com/about", "state": "NEW", "severity": "warning", "first_seen": "2026-08-13T12:00:00Z", "last_seen": "2026-08-13T12:00:00Z"}]},
            "capabilities.json": {"capabilities": [{"capability": "site-crawl", "available": True, "source": "site-profile"}]},
        }
        for name, value in values.items():
            (run / name).write_text(json.dumps(value))
        return run

    def test_catalog_sync_import_and_api_views(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = self.make_run(root)
            with dashboard.connect(root / "webops.sqlite3") as db:
                dashboard.sync_catalogs(db)
                self.assertTrue(dashboard.import_run(db, run))
                summary = dashboard.api_payload(db, "summary")
                self.assertEqual(1, summary["runs"])
                self.assertEqual(1, summary["findings"])
                self.assertEqual(10, summary["workflows"])
                findings = dashboard.api_payload(db, "findings")
                self.assertEqual("missing-description", findings[0]["check_name"])
                self.assertEqual("https://example.com", dashboard.api_payload(db, "runs")[0]["url"])
                plan = db.execute("EXPLAIN QUERY PLAN SELECT * FROM findings WHERE state=? AND severity=?", ("NEW", "warning")).fetchall()
                self.assertTrue(any("idx_findings_state_severity" in row[3] for row in plan))

    def test_run_discovery_rejects_incomplete_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = self.make_run(root)
            incomplete = root / "incomplete"
            incomplete.mkdir()
            (incomplete / "run-receipt.json").write_text("{}")
            self.assertEqual([incomplete, valid], dashboard.discover_runs([root]))
            with dashboard.connect(root / "webops.sqlite3") as db:
                dashboard.sync_catalogs(db)
                self.assertFalse(dashboard.import_run(db, incomplete))

    def test_dashboard_fetch_map_does_not_forward_array_callback_arguments(self):
        source = (ROOT / "webops-dashboard" / "public" / "assets" / "dashboard.js").read_text()
        self.assertIn(".map(path=>api(path))", source)
        self.assertNotIn(".map(api)", source)

    def test_dashboard_mobile_navigation_uses_kujo_branding(self):
        public = ROOT / "webops-dashboard" / "public"
        html = (public / "index.html").read_text()
        css = (public / "assets" / "dashboard.css").read_text()
        script = (public / "assets" / "dashboard.js").read_text()
        logo = (public / "assets" / "kujo-logomark.svg").read_text()
        server = (ROOT / "webops-dashboard" / "dashboard.py").read_text()

        self.assertIn('/assets/kujo-logomark.svg', html)
        self.assertNotIn('>W/<', html)
        self.assertIn('data-mobile-menu-toggle', html)
        self.assertIn('id="mobile-navigation"', html)
        self.assertIn('d="M4 6h16"', html)
        self.assertIn('.mobile-navigation-shell', css)
        self.assertIn('.desktop-navigation,.desktop-theme-button{display:none}', css)
        self.assertIn('enhanceMobileNavigation', script)
        self.assertIn('event.key==="Escape"', script)
        self.assertIn('<svg', logo)
        self.assertIn('viewBox="0 0 1527 1536"', logo)
        self.assertIn('".svg": "image/svg+xml"', server)


if __name__ == "__main__":
    unittest.main(verbosity=2)
