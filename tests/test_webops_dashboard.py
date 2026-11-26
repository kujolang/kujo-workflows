#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import http.client
import shutil
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_invalid_reimport_preserves_previous_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = self.make_run(root)
            with dashboard.connect(root / "webops.sqlite3") as db:
                dashboard.sync_catalogs(db)
                dashboard.import_run(db, run)
                finding_path = run / "findings.json"
                entry = json.loads(finding_path.read_text())["findings"][0]
                finding_path.write_text(json.dumps({"findings": [entry, entry]}))
                with self.assertRaises(sqlite3.IntegrityError):
                    dashboard.import_run(db, run)
                self.assertEqual(1, dashboard.api_payload(db, "summary")["runs"])
                self.assertEqual(1, dashboard.api_payload(db, "summary")["findings"])

    def test_summary_counts_the_latest_state_for_each_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = self.make_run(root)
            later = root / "later"
            shutil.copytree(original, later)
            receipt = json.loads((later / "run-receipt.json").read_text())
            receipt.update(run_id="run-resolved", completed_at="2026-08-14T12:01:00Z")
            (later / "run-receipt.json").write_text(json.dumps(receipt))
            findings = json.loads((later / "findings.json").read_text())
            findings["findings"][0]["state"] = "RESOLVED"
            (later / "findings.json").write_text(json.dumps(findings))
            with dashboard.connect(root / "webops.sqlite3") as db:
                dashboard.sync_catalogs(db)
                dashboard.import_run(db, original)
                dashboard.import_run(db, later)
                self.assertEqual(0, dashboard.api_payload(db, "summary")["findings"])
                self.assertEqual("RESOLVED", dashboard.api_payload(db, "findings")[0]["state"])
                self.assertEqual([], dashboard.api_payload(db, "charts")["severity"])

    def test_report_accepts_local_json_and_checks_request_boundaries(self):
        handler = type("FixtureHandler", (dashboard.Handler,), {
            "db_path": Path("unused.sqlite3"),
            "report_slots": threading.BoundedSemaphore(1),
            "log_message": lambda *_: None,
        })
        with dashboard.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            authority = f"127.0.0.1:{server.server_port}"
            handler.allowed_hosts = frozenset({authority})
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()

            def request(body, **headers):
                conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                try:
                    conn.request("POST", "/api/run", body=body, headers={"Content-Type": "application/json", **headers})
                    reply = conn.getresponse()
                    return reply.status, json.loads(reply.read())
                finally:
                    conn.close()

            try:
                with patch.object(dashboard, "run_report", return_value={"ok": True}) as report:
                    self.assertEqual(400, request("{}", Host="unrecognized.example")[0])
                    self.assertEqual(403, request("{}", Origin="https://other.example")[0])
                    self.assertEqual(415, request("{}", **{"Content-Type": "text/plain"})[0])
                    self.assertEqual(413, request(" " * 10001)[0])
                    self.assertEqual(400, request("[]")[0])
                    with handler.report_slots:
                        self.assertEqual(429, request("{}")[0])
                    report.assert_not_called()
                    self.assertEqual((201, {"ok": True}), request("{}", Origin=f"http://{authority}"))
                    report.assert_called_once_with(Path("unused.sqlite3"), {})
            finally:
                server.shutdown()
                worker.join(timeout=3)

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
