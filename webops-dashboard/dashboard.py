#!/usr/bin/env python3
"""SQLite-backed local control surface for Kujo WebOps workflow evidence."""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
APP = Path(__file__).resolve().parent
PUBLIC = APP / "public"
DEFAULT_DB = ROOT / ".webops" / "dashboard" / "webops.sqlite3"
AGENTS_CATALOG = ROOT.parent / "kujo-agents" / "webops" / "webops-catalog.json"
WORKFLOW_GLOB = "webops-*"

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS sites (
  id TEXT PRIMARY KEY, url TEXT NOT NULL, repository TEXT, platform TEXT
);
CREATE TABLE IF NOT EXISTS workflows (
  id TEXT PRIMARY KEY, version TEXT NOT NULL, purpose TEXT NOT NULL,
  readiness TEXT NOT NULL, default_permission TEXT NOT NULL, manifest_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS agents (
  slug TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, category TEXT NOT NULL,
  purpose TEXT NOT NULL, permission_min TEXT NOT NULL, permission_max TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS workflow_agents (
  workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  agent_name TEXT NOT NULL, position INTEGER NOT NULL,
  PRIMARY KEY (workflow_id, agent_name)
);
CREATE TABLE IF NOT EXISTS runs (
  key TEXT PRIMARY KEY, run_id TEXT NOT NULL, workflow_id TEXT NOT NULL,
  site_id TEXT NOT NULL, started_at TEXT, completed_at TEXT, verdict TEXT NOT NULL,
  permission TEXT NOT NULL, fixture INTEGER NOT NULL, source_path TEXT NOT NULL,
  imported_at TEXT NOT NULL,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id),
  FOREIGN KEY (site_id) REFERENCES sites(id)
);
CREATE TABLE IF NOT EXISTS steps (
  run_key TEXT NOT NULL REFERENCES runs(key) ON DELETE CASCADE,
  step_index INTEGER NOT NULL, name TEXT NOT NULL, status TEXT NOT NULL,
  detail TEXT, PRIMARY KEY (run_key, step_index)
);
CREATE TABLE IF NOT EXISTS findings (
  run_key TEXT NOT NULL REFERENCES runs(key) ON DELETE CASCADE,
  finding_id TEXT NOT NULL, agent TEXT NOT NULL, check_name TEXT NOT NULL,
  target TEXT NOT NULL, state TEXT NOT NULL, severity TEXT NOT NULL,
  first_seen TEXT, last_seen TEXT, PRIMARY KEY (run_key, finding_id)
);
CREATE TABLE IF NOT EXISTS capabilities (
  run_key TEXT NOT NULL REFERENCES runs(key) ON DELETE CASCADE,
  name TEXT NOT NULL, available INTEGER NOT NULL, source TEXT NOT NULL,
  PRIMARY KEY (run_key, name, source)
);
CREATE INDEX IF NOT EXISTS idx_runs_completed ON runs(completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_runs_workflow_completed ON runs(workflow_id, completed_at DESC);
CREATE INDEX IF NOT EXISTS idx_findings_state_severity ON findings(state, severity);
CREATE INDEX IF NOT EXISTS idx_findings_check ON findings(check_name);
CREATE INDEX IF NOT EXISTS idx_steps_status ON steps(status);
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    db.execute("PRAGMA journal_mode = WAL")
    return db


def workflow_manifests() -> list[tuple[Path, dict[str, Any]]]:
    manifests = []
    for folder in sorted(ROOT.glob(WORKFLOW_GLOB)):
        path = folder / "workflow.json"
        if path.is_file():
            manifests.append((folder, read_json(path)))
    return manifests


def sync_catalogs(db: sqlite3.Connection) -> None:
    for _folder, item in workflow_manifests():
        db.execute(
            "INSERT INTO workflows VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
            "version=excluded.version,purpose=excluded.purpose,readiness=excluded.readiness,"
            "default_permission=excluded.default_permission,manifest_json=excluded.manifest_json",
            (item["id"], item["version"], item["purpose"], item["readiness"],
             item["default_permission"], json.dumps(item, sort_keys=True)),
        )
        db.execute("DELETE FROM workflow_agents WHERE workflow_id=?", (item["id"],))
        db.executemany(
            "INSERT INTO workflow_agents(workflow_id,agent_name,position) VALUES(?,?,?)",
            [(item["id"], name, index) for index, name in enumerate(item["agents"], 1)],
        )
    if AGENTS_CATALOG.is_file():
        for item in read_json(AGENTS_CATALOG).get("agents", []):
            db.execute(
                "INSERT INTO agents VALUES(?,?,?,?,?,?) ON CONFLICT(slug) DO UPDATE SET "
                "name=excluded.name,category=excluded.category,purpose=excluded.purpose,"
                "permission_min=excluded.permission_min,permission_max=excluded.permission_max",
                (item["slug"], item["agent"], item["category"], item["purpose"],
                 item["permission_min"], item["permission_max"]),
            )
    db.commit()


def import_run(db: sqlite3.Connection, run_dir: Path) -> bool:
    required = ["state.json", "profile.json", "findings.json", "run-receipt.json"]
    if not all((run_dir / name).is_file() for name in required):
        return False
    state = read_json(run_dir / "state.json")
    profile = read_json(run_dir / "profile.json")
    receipt = read_json(run_dir / "run-receipt.json")
    finding_rows = read_json(run_dir / "findings.json").get("findings", [])
    caps = read_json(run_dir / "capabilities.json").get("capabilities", []) if (run_dir / "capabilities.json").is_file() else []
    site = profile["site"]
    workflow_id = receipt["workflow"]
    run_id = receipt["run_id"]
    key = f"{workflow_id}:{run_id}"
    db.execute(
        "INSERT INTO sites VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET "
        "url=excluded.url,repository=excluded.repository,platform=excluded.platform",
        (site["id"], site["url"], site.get("repository"), site.get("platform")),
    )
    db.execute("DELETE FROM runs WHERE key=?", (key,))
    db.execute(
        "INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?,?)",
        (key, run_id, workflow_id, site["id"], state.get("started_at"),
         receipt.get("completed_at", state.get("completed_at")), receipt["verdict"],
         receipt["permission"], int(receipt.get("fixture", False)), str(run_dir.resolve()), utc_now()),
    )
    db.executemany(
        "INSERT INTO steps VALUES(?,?,?,?,?)",
        [(key, item["index"], item["step"], item["status"], item.get("detail", ""))
         for item in state.get("steps", [])],
    )
    db.executemany(
        "INSERT INTO findings VALUES(?,?,?,?,?,?,?,?,?)",
        [(key, item["id"], item["agent"], item["check"], item["target"], item["state"],
          item["severity"], item.get("first_seen"), item.get("last_seen")) for item in finding_rows],
    )
    db.executemany(
        "INSERT OR REPLACE INTO capabilities VALUES(?,?,?,?)",
        [(key, item["capability"], int(bool(item["available"])), item.get("source", "unknown")) for item in caps],
    )
    db.commit()
    return True


def discover_runs(roots: list[Path]) -> list[Path]:
    found = set()
    for root in roots:
        if not root.exists():
            continue
        if (root / "run-receipt.json").is_file():
            found.add(root)
            continue
        for receipt in root.rglob("run-receipt.json"):
            found.add(receipt.parent)
    return sorted(found)


def query_rows(db: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in db.execute(sql, params).fetchall()]


def api_payload(db: sqlite3.Connection, endpoint: str) -> Any:
    if endpoint == "summary":
        result = dict(db.execute("""
            SELECT (SELECT COUNT(*) FROM runs) runs,
                   (SELECT COUNT(*) FROM (SELECT DISTINCT r.site_id,f.finding_id FROM findings f JOIN runs r ON r.key=f.run_key WHERE f.state!='RESOLVED')) findings,
                   (SELECT COUNT(*) FROM workflows) workflows,
                   (SELECT COUNT(*) FROM agents) agents,
                   (SELECT COUNT(*) FROM steps WHERE status='approval-required') approvals
        """).fetchone())
        result["latest"] = query_rows(db, "SELECT r.*,s.url FROM runs r JOIN sites s ON s.id=r.site_id ORDER BY completed_at DESC LIMIT 1")
        return result
    if endpoint == "runs":
        return query_rows(db, """
            SELECT r.*,s.url,
              SUM(CASE WHEN st.status='completed' THEN 1 ELSE 0 END) completed_steps,
              SUM(CASE WHEN st.status IN ('skipped-degraded','approval-required') THEN 1 ELSE 0 END) limited_steps
            FROM runs r JOIN sites s ON s.id=r.site_id LEFT JOIN steps st ON st.run_key=r.key
            GROUP BY r.key ORDER BY r.completed_at DESC LIMIT 200
        """)
    if endpoint == "findings":
        return query_rows(db, """
            WITH ranked AS (
              SELECT f.*,r.workflow_id,r.completed_at,s.url,
                     ROW_NUMBER() OVER (PARTITION BY r.site_id,f.finding_id ORDER BY r.completed_at DESC,r.workflow_id) rank
              FROM findings f JOIN runs r ON r.key=f.run_key JOIN sites s ON s.id=r.site_id
            )
            SELECT * FROM ranked WHERE rank=1
            ORDER BY CASE state WHEN 'NEW' THEN 0 WHEN 'REOPENED' THEN 1 WHEN 'PERSISTENT' THEN 2 ELSE 3 END,
                     CASE severity WHEN 'error' THEN 0 WHEN 'warning' THEN 1 ELSE 2 END,
                     completed_at DESC LIMIT 500
        """)
    if endpoint == "workflows":
        return query_rows(db, """
            SELECT w.id,w.purpose,w.readiness,w.default_permission,COUNT(DISTINCT wa.agent_name) agents,
                   COUNT(DISTINCT r.key) runs,MAX(r.completed_at) last_run
            FROM workflows w LEFT JOIN workflow_agents wa ON wa.workflow_id=w.id
            LEFT JOIN runs r ON r.workflow_id=w.id GROUP BY w.id ORDER BY w.id
        """)
    if endpoint == "agents":
        return query_rows(db, "SELECT * FROM agents ORDER BY category,name")
    if endpoint == "charts":
        return {
            "severity": query_rows(db, """WITH latest AS (
                SELECT f.*,ROW_NUMBER() OVER (PARTITION BY r.site_id,f.finding_id ORDER BY r.completed_at DESC) rank
                FROM findings f JOIN runs r ON r.key=f.run_key)
                SELECT severity name,COUNT(*) value FROM latest WHERE rank=1 AND state!='RESOLVED' GROUP BY severity ORDER BY value DESC"""),
            "coverage": query_rows(db, "SELECT workflow_id label,COUNT(*) runs FROM runs GROUP BY workflow_id ORDER BY runs DESC,workflow_id LIMIT 10"),
            "trend": query_rows(db, "SELECT substr(r.completed_at,1,10) label,COUNT(DISTINCT f.finding_id) findings,COUNT(DISTINCT CASE WHEN f.severity='error' THEN f.finding_id END) errors FROM findings f JOIN runs r ON r.key=f.run_key GROUP BY substr(r.completed_at,1,10) ORDER BY label LIMIT 30"),
            "steps": query_rows(db, "SELECT status name,COUNT(*) value FROM steps GROUP BY status ORDER BY value DESC"),
        }
    raise KeyError(endpoint)


def run_report(db_path: Path, body: dict[str, Any]) -> dict[str, Any]:
    workflow = str(body.get("workflow", ""))
    target = str(body.get("target", "")).strip()
    permission = str(body.get("permission", "OBSERVE"))
    allowed = {item[1]["id"] for item in workflow_manifests()}
    parsed = urlsplit(target)
    if workflow not in allowed or permission not in {"OBSERVE", "PROPOSE"}:
        raise ValueError("Unsupported workflow or permission")
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Target must be a complete HTTP(S) URL")
    slug = re.sub(r"[^a-z0-9.-]+", "-", parsed.hostname.lower()).strip("-")
    state_root = db_path.parent
    profile_path = state_root / "profiles" / f"{slug}.json"
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "schema": "webops.site-profile/v1",
        "site": {"id": slug, "url": target, "platform": "live-website"},
        "capabilities": {"website": True, "site-crawl": True, "content-graph": True, "browser": "optional", "web-search": False},
        "integrations": {}, "permissions": {"default": permission}, "credential_references": {},
    }
    profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = state_root / "runs" / f"{stamp}-{workflow}"
    command = [sys.executable, str(ROOT / "scripts" / "webops_workflow.py"), "--workflow", workflow,
               "--live", "--site-profile", str(profile_path), "--permission", permission, "--out", str(out)]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "WebOps run failed")[-1000:])
    with connect(db_path) as db:
        sync_catalogs(db)
        import_run(db, out)
    return {"ok": True, "run": out.name, "result": json.loads(result.stdout)}


class Handler(BaseHTTPRequestHandler):
    db_path: Path

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("webops-dashboard: " + (format % args) + "\n")

    def send_json(self, value: Any, status: int = 200) -> None:
        data = json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path.startswith("/api/"):
            try:
                with connect(self.db_path) as db:
                    self.send_json(api_payload(db, path.removeprefix("/api/")))
            except KeyError:
                self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        relative = "index.html" if path == "/" else path.lstrip("/")
        candidate = (PUBLIC / relative).resolve()
        if PUBLIC.resolve() not in candidate.parents and candidate != PUBLIC.resolve():
            self.send_error(HTTPStatus.NOT_FOUND); return
        if not candidate.is_file():
            self.send_error(HTTPStatus.NOT_FOUND); return
        types = {".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".json": "application/json"}
        data = candidate.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", types.get(candidate.suffix, "application/octet-stream") + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers(); self.wfile.write(data)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/run":
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND); return
        length = min(int(self.headers.get("Content-Length", "0")), 10000)
        try:
            body = json.loads(self.rfile.read(length))
            self.send_json(run_report(self.db_path, body), HTTPStatus.CREATED)
        except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)


def command_sync(args: argparse.Namespace) -> int:
    db_path = Path(args.db).resolve()
    with connect(db_path) as db:
        sync_catalogs(db)
        roots = [Path(item).resolve() for item in args.runs_root] if args.runs_root else [ROOT]
        runs = discover_runs(roots)
        imported = sum(import_run(db, run) for run in runs)
        db.execute("PRAGMA optimize")
    print(json.dumps({"database": str(db_path), "runs_discovered": len(runs), "runs_imported": imported}, sort_keys=True))
    return 0


def command_import(args: argparse.Namespace) -> int:
    db_path = Path(args.db).resolve()
    with connect(db_path) as db:
        sync_catalogs(db)
        imported = sum(import_run(db, path) for path in discover_runs([Path(item).resolve() for item in args.paths]))
        db.execute("PRAGMA optimize")
    print(json.dumps({"database": str(db_path), "runs_imported": imported}, sort_keys=True))
    return 0 if imported else 1


def command_serve(args: argparse.Namespace) -> int:
    db_path = Path(args.db).resolve()
    with connect(db_path) as db:
        sync_catalogs(db)
    handler = type("WebOpsHandler", (Handler,), {"db_path": db_path})
    server = ThreadingHTTPServer((args.host, args.port), handler)
    url = f"http://{args.host}:{server.server_port}/"
    print(url, flush=True)
    if args.open:
        threading.Timer(0.25, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def parser() -> argparse.ArgumentParser:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--db", default=str(DEFAULT_DB))
    commands = cli.add_subparsers(dest="command", required=True)
    sync = commands.add_parser("sync"); sync.add_argument("--runs-root", action="append", default=[]); sync.set_defaults(func=command_sync)
    ingest = commands.add_parser("import-run"); ingest.add_argument("paths", nargs="+"); ingest.set_defaults(func=command_import)
    serve = commands.add_parser("serve"); serve.add_argument("--host", default="127.0.0.1"); serve.add_argument("--port", type=int, default=8765); serve.add_argument("--open", action="store_true"); serve.set_defaults(func=command_serve)
    return cli


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.func(arguments))
