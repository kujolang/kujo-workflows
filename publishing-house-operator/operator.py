#!/usr/bin/env python3
"""Local-first operator for the Kujo Publishing House.

StoryDesk remains the editorial database. This process owns only scheduling,
leases, checkpoints, receipts, and references to records owned by Kujo tools.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parent
WORKFLOWS_ROOT = ROOT.parent
SCHEMA_VERSION = "1.0.0"
PHASES = [
    "commissioning", "evidence-dossier", "primary-piece", "asset-production",
    "editorial-review", "adaptation", "format-production",
    "approval-publication", "post-publication",
]
NOTIFICATIONS = {
    "APPROVAL_REQUIRED", "HARD_BLOCKER", "EVIDENCE_CONFLICT", "SOURCE_MISSING",
    "PUBLICATION_FAILURE", "POST_PUBLISH_VERIFICATION_FAILURE", "DEADLINE_AT_RISK",
    "BUDGET_EXCEEDED", "POLICY_VIOLATION", "SYSTEM_HEALTH_FAILURE",
}


class OperatorError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\0".join(parts).encode()).hexdigest()[:16]
    return f"{prefix}-{digest}"


def read_data(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
    else:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise OperatorError("yaml_unavailable", "PyYAML is required for YAML; JSON is always supported") from exc
        value = yaml.safe_load(text)
    if not isinstance(value, dict):
        raise OperatorError("invalid_document", f"{path} must contain an object")
    return value


def atomic_json(path: Path, value: Any, replace: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not replace:
        raise OperatorError("duplicate_record", f"record already exists: {path.name}")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class House:
    def __init__(self, state: Path, repos: Path):
        self.state = state.resolve()
        self.repos = repos.resolve()
        self.storydesk = self.repos / "storydesk/bin/storydesk"
        self.kujo = self.repos / "kujo/target/release/kujo"

    def require_initialized(self) -> None:
        if not (self.state / "house.json").is_file():
            raise OperatorError("not_initialized", f"run init for {self.state}")

    def init(self) -> dict[str, Any]:
        for name in ["sourcepacks", "plans", "items", "runs", "receipts", "notifications", "locks", "profiles", "voices", "events", "adapters"]:
            (self.state / name).mkdir(parents=True, exist_ok=True)
        for profile in sorted((ROOT / "profiles").glob("*.json")):
            target = self.state / "profiles" / profile.name
            if not target.exists():
                shutil.copy2(profile, target)
        for voice in sorted((ROOT / "voices").glob("*.json")):
            target = self.state / "voices" / voice.name
            if not target.exists():
                shutil.copy2(voice, target)
        house = {
            "schema_name": "publishing-house.operator-state", "schema_version": SCHEMA_VERSION,
            "created_at": now(), "storydesk_state": str(self.state / "storydesk"),
            "limits": {"max_items_per_tick": 4, "max_concurrent_workflows": 2,
                       "max_concurrent_publication_effects": 1, "daily_item_limit": 12,
                       "retry_limit": 2, "token_budget": 250000},
        }
        if not (self.state / "house.json").exists():
            atomic_json(self.state / "house.json", house, replace=False)
        if self.storydesk.is_file() and self.kujo.is_file():
            self._tool([str(self.storydesk), "init", "--state", str(self.state / "storydesk"), "--json"], allow_failure=True)
        return {"state": str(self.state), "profiles": len(list((self.state / "profiles").glob("*.json")))}

    def profiles(self) -> list[dict[str, Any]]:
        self.require_initialized()
        values = [read_data(p) for p in sorted((self.state / "profiles").glob("*.json"))]
        for value in values:
            self._validate_profile(value)
        return values

    def add_profile(self, source: Path) -> dict[str, Any]:
        self.require_initialized()
        value = read_data(source)
        self._validate_profile(value)
        target = self.state / "profiles" / f"{value['id']}.json"
        atomic_json(target, value, replace=False)
        return {"id": value["id"], "path": str(target)}

    def _validate_profile(self, value: dict[str, Any]) -> None:
        required = ["id", "identity", "publication_type", "canonical_repository", "source_of_truth",
                    "audience", "editorial_mission", "voice_profile", "content_formats", "frontmatter",
                    "claim_policy", "evidence_policy", "build", "deployment", "verification",
                    "approval_policy", "refresh_policy", "correction_policy"]
        missing = [key for key in required if not value.get(key)]
        if value.get("schema_name") != "publishing-house.publication-profile" or value.get("schema_version") != SCHEMA_VERSION or missing:
            raise OperatorError("invalid_publication_profile", f"invalid profile {value.get('id', '<unknown>')}; missing: {', '.join(missing)}")
        repo = Path(os.path.expandvars(str(value["canonical_repository"]))).expanduser()
        if not repo.is_absolute():
            repo = self.repos / repo
        if not repo.is_dir():
            raise OperatorError("publication_repository_missing", f"repository unavailable for {value['id']}: {repo}")

    def intake(self, publication: str, sources: list[str], text: str | None, requested_format: str,
               priority: str, title: str | None) -> dict[str, Any]:
        self.require_initialized()
        profile = self._profile(publication)
        chunks: list[dict[str, Any]] = []
        raw_parts: list[bytes] = []
        for source in sources:
            path = Path(source).expanduser().resolve()
            if not path.exists():
                raise OperatorError("source_missing", f"source does not exist: {source}")
            if path.is_dir():
                files = [p for p in sorted(path.rglob("*")) if p.is_file() and not p.is_symlink()]
            else:
                files = [path]
            for item in files:
                if item.stat().st_size > 16 * 1024 * 1024:
                    raise OperatorError("source_too_large", f"source exceeds 16 MiB: {item}")
                data = item.read_bytes()
                raw_parts.append(data)
                chunks.append({"kind": "file", "source": str(item), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        if text is not None:
            data = text.encode()
            raw_parts.append(data)
            chunks.append({"kind": "text", "source": "stdin-or-argument", "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
        if not chunks:
            raise OperatorError("source_missing", "provide --source, --text, or stdin")
        pack_id = stable_id("sourcepack", publication, *(entry["sha256"] for entry in chunks))
        pack_dir = self.state / "sourcepacks" / pack_id
        if (pack_dir / "sourcepack.json").exists():
            return {"id": pack_id, "idempotent_replay": True, "path": str(pack_dir / "sourcepack.json")}
        (pack_dir / "originals").mkdir(parents=True)
        for index, (entry, data) in enumerate(zip(chunks, raw_parts), start=1):
            raw = pack_dir / "originals" / f"{index:03d}.bin"
            raw.write_bytes(data)
            entry["preserved_path"] = str(raw)
        sample = b"\n".join(raw_parts).decode("utf-8", errors="replace")
        working_title = title or next((line.strip("# ") for line in sample.splitlines() if line.strip()), "Untitled intake")[:160]
        pack = {
            "schema_name": "publishing-house.sourcepack", "schema_version": SCHEMA_VERSION,
            "id": pack_id, "created_at": now(), "publication": publication, "publication_profile": profile["id"],
            "working_topic": working_title, "requested_format": requested_format, "priority": priority,
            "sources": chunks, "normalization": {"possible_thesis": "", "known_facts": [], "opinions": [],
                "claims_requiring_verification": [], "unknowns": [], "campaign": "", "related_projects": [],
                "potential_assets": [], "potential_adaptations": []},
        }
        atomic_json(pack_dir / "sourcepack.json", pack, replace=False)
        idea = {"schema_version": SCHEMA_VERSION, "title": working_title,
                "detail": f"SourcePack {pack_id} for {publication}", "publication": publication,
                "sourcepack_id": pack_id, "priority": priority,
                "provenance": [{"kind": "sourcepack", "source": str(pack_dir / "sourcepack.json"), "checksum": sha256(pack_dir / "sourcepack.json")}]}
        idea_id = stable_id("idea", pack_id)
        self._storydesk_mutation("idea add", idea_id, idea)
        pack["storydesk_idea_id"] = idea_id
        atomic_json(pack_dir / "sourcepack.json", pack)
        return {"id": pack_id, "storydesk_idea_id": idea_id, "path": str(pack_dir / "sourcepack.json")}

    def import_plan(self, source: Path) -> dict[str, Any]:
        self.require_initialized()
        plan = read_data(source)
        if plan.get("schema_name") not in (None, "publishing-house.editorial-plan"):
            raise OperatorError("invalid_plan", "unsupported plan schema")
        items = plan.get("items")
        if not isinstance(items, list) or not items:
            raise OperatorError("invalid_plan", "plan requires a non-empty items array")
        plan_id = str(plan.get("id") or stable_id("plan", source.read_text(encoding="utf-8")))
        target = self.state / "plans" / f"{plan_id}.json"
        if target.exists():
            return {"id": plan_id, "idempotent_replay": True, "items": len(items)}
        known: set[str] = set()
        normalized: list[dict[str, Any]] = []
        for raw in items:
            if not isinstance(raw, dict) or not raw.get("id") or not raw.get("publication"):
                raise OperatorError("invalid_plan_item", "each item requires id and publication")
            item_id = str(raw["id"])
            if item_id in known:
                raise OperatorError("duplicate_plan_item", item_id)
            known.add(item_id)
            profile = self._profile(str(raw["publication"]))
            deps = raw.get("depends_on", [])
            if not isinstance(deps, list):
                raise OperatorError("invalid_dependencies", item_id)
            item = {
                "schema_name": "publishing-house.work-item", "schema_version": SCHEMA_VERSION,
                "id": item_id, "plan_id": plan_id, "publication": profile["id"],
                "type": raw.get("type", "article"), "title": raw.get("title", item_id.replace("-", " ").title()),
                "source": raw.get("source", ""), "priority": raw.get("priority", "normal"),
                "depends_on": deps, "publish_window": raw.get("publish_window", {}),
                "series": raw.get("series"), "cluster": raw.get("cluster"),
                "adaptations": raw.get("adaptations", []), "refresh_of": raw.get("refresh_of"),
                "status": "planned", "phase_index": 0, "attempts": {}, "created_at": now(), "updated_at": now(),
            }
            normalized.append(item)
        dangling = sorted({dep for item in normalized for dep in item["depends_on"] if dep not in known and not (self.state / "items" / f"{dep}.json").exists()})
        if dangling:
            raise OperatorError("unknown_dependency", ", ".join(dangling))
        plan_record = {"schema_name": "publishing-house.editorial-plan", "schema_version": SCHEMA_VERSION,
                       "id": plan_id, "kind": plan.get("kind", "monthly"), "period": plan.get("month", plan.get("period", "")),
                       "campaign": plan.get("campaign"), "created_at": now(), "items": [item["id"] for item in normalized],
                       "source": str(source.resolve()), "source_sha256": sha256(source)}
        atomic_json(target, plan_record, replace=False)
        for item in normalized:
            atomic_json(self.state / "items" / f"{item['id']}.json", item, replace=False)
            brief = {"schema_version": SCHEMA_VERSION, "title": item["title"], "audience": self._profile(item["publication"])["audience"],
                     "purpose": f"Produce {item['type']} for {item['publication']}", "publication": item["publication"],
                     "plan_id": plan_id, "dependencies": item["depends_on"], "source": item["source"],
                     "provenance": [{"kind": "editorial-plan", "source": str(target), "checksum": sha256(target)}]}
            self._storydesk_mutation("commission create", f"brief-{item['id']}", brief)
        return {"id": plan_id, "items": len(normalized), "path": str(target)}

    @contextlib.contextmanager
    def lease(self, name: str) -> Iterator[None]:
        lock = self.state / "locks" / name
        try:
            lock.mkdir()
        except FileExistsError as exc:
            raise OperatorError("concurrent_run", f"operator lease already held: {name}") from exc
        atomic_json(lock / "lease.json", {"pid": os.getpid(), "created_at": now()})
        try:
            yield
        finally:
            shutil.rmtree(lock, ignore_errors=True)

    def tick(self, limit: int, fixture: bool) -> dict[str, Any]:
        self.require_initialized()
        with self.lease("operator"):
            doctor = self.doctor()
            if not doctor["ok"]:
                self._notify("SYSTEM_HEALTH_FAILURE", "operator health check failed", doctor)
                raise OperatorError("system_health_failure", "doctor failed")
            items = [read_data(p) for p in sorted((self.state / "items").glob("*.json"))]
            completed = {item["id"] for item in items if item["status"] == "completed"}
            eligible = [item for item in items if item["status"] not in {"completed", "blocked", "approval_required"}
                        and all(dep in completed for dep in item["depends_on"])]
            eligible.sort(key=lambda item: ({"urgent": 0, "high": 1, "normal": 2, "low": 3}.get(item["priority"], 2), item["id"]))
            moved = []
            for item in eligible[:limit]:
                phase = PHASES[item["phase_index"]]
                if phase == "approval-publication" and self._requires_human(item) and not item.get("approval_reference"):
                    item["status"] = "approval_required"
                    self._notify("APPROVAL_REQUIRED", f"exact-version approval required for {item['id']}", {"item": item["id"]})
                elif fixture:
                    receipt = self._fixture_phase(item, phase)
                    item.setdefault("receipts", []).append(receipt)
                    item["phase_index"] += 1
                    item["status"] = "completed" if item["phase_index"] == len(PHASES) else "in_progress"
                else:
                    try:
                        receipt = self._live_phase(item, phase)
                        item.setdefault("receipts", []).append(receipt)
                        item["phase_index"] += 1
                        item["status"] = "completed" if item["phase_index"] == len(PHASES) else "in_progress"
                        item.pop("blocker", None)
                    except OperatorError as exc:
                        attempts = item.setdefault("attempts", {})
                        attempts[phase] = int(attempts.get(phase, 0)) + 1
                        retry_limit = int(read_data(self.state / "house.json")["limits"]["retry_limit"])
                        item["blocker"] = {"code": exc.code, "message": str(exc), "phase": phase,
                                           "attempt": attempts[phase], "retry_limit": retry_limit, "created_at": now()}
                        if attempts[phase] >= retry_limit or exc.code == "live_worker_adapter_unavailable":
                            item["status"] = "blocked"
                            self._notify("HARD_BLOCKER", f"live phase blocked for {item['id']}", item["blocker"])
                        else:
                            item["status"] = "retry_pending"
                item["updated_at"] = now()
                atomic_json(self.state / "items" / f"{item['id']}.json", item)
                moved.append({"id": item["id"], "phase": phase, "status": item["status"]})
            run_id = stable_id("tick", now(), str(os.getpid()))
            receipt = {"schema_name": "publishing-house.operator-run", "schema_version": SCHEMA_VERSION,
                       "id": run_id, "created_at": now(), "fixture": fixture, "selected": moved,
                       "limits": {"items": limit}, "outcome": "completed"}
            atomic_json(self.state / "runs" / f"{run_id}.json", receipt, replace=False)
            return receipt

    def approve(self, item_id: str, checksum: str, approver: str) -> dict[str, Any]:
        self.require_initialized()
        path = self.state / "items" / f"{item_id}.json"
        item = read_data(path)
        if item.get("status") != "approval_required":
            raise OperatorError("approval_not_pending", item_id)
        artifact = self._latest_artifact_checksum(item)
        if artifact != checksum:
            raise OperatorError("checksum_mismatch", "approval must bind the current exact artifact checksum")
        approval = {"schema_name": "publishing-house.approval-reference", "schema_version": SCHEMA_VERSION,
                    "item_id": item_id, "artifact_sha256": checksum, "approver": approver, "created_at": now(),
                    "policy": "REQUIRE_EXACT_HUMAN_APPROVAL"}
        approval_id = stable_id("approval", item_id, checksum, approver)
        atomic_json(self.state / "receipts" / f"{approval_id}.json", approval, replace=False)
        item["approval_reference"] = approval_id
        item["status"] = "in_progress"
        atomic_json(path, item)
        return {"id": approval_id, "item": item_id}

    def resume(self, item_id: str) -> dict[str, Any]:
        """Release a blocked item after an operator has corrected its blocker."""
        self.require_initialized()
        path = self.state / "items" / f"{item_id}.json"
        if not path.is_file():
            raise OperatorError("unknown_item", item_id)
        item = read_data(path)
        if item.get("status") != "blocked":
            raise OperatorError("item_not_blocked", item_id)
        prior = item.pop("blocker", None)
        item["status"] = "in_progress"
        item["updated_at"] = now()
        atomic_json(path, item)
        return {"id": item_id, "status": "in_progress", "released_blocker": prior}

    def status(self) -> dict[str, Any]:
        self.require_initialized()
        items = [read_data(p) for p in sorted((self.state / "items").glob("*.json"))]
        counts: dict[str, int] = {}
        for item in items:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        return {"state": str(self.state), "items": len(items), "counts": counts,
                "approvals": [item["id"] for item in items if item["status"] == "approval_required"],
                "blocked": [item["id"] for item in items if item["status"] == "blocked"]}

    def ingest_event(self, source: Path) -> dict[str, Any]:
        self.require_initialized()
        event = read_data(source)
        required = ["kind", "source", "occurred_at"]
        missing = [key for key in required if not event.get(key)]
        if missing:
            raise OperatorError("invalid_event", f"event missing: {', '.join(missing)}")
        kind = str(event["kind"])
        policies = {
            "release": ["documentation-obligation", "article-candidate", "social-candidate"],
            "cli-change": ["documentation-obligation"], "api-change": ["documentation-obligation"],
            "agent-added": ["agent-site-sync", "social-card-sync", "human-review-announcement"],
            "agent-changed": ["agent-site-sync", "site-validation"],
            "broken-page": ["site-update"], "stale-evidence": ["refresh-job"],
            "search-opportunity": ["article-candidate"], "performance-change": ["human-review"],
        }
        actions = policies.get(kind, [])
        event_id = str(event.get("id") or stable_id("event", kind, str(event["source"]), str(event["occurred_at"])))
        target = self.state / "events" / f"{event_id}.json"
        if target.exists():
            return {"id": event_id, "idempotent_replay": True, "actions": actions}
        storydesk_ids = [stable_id("idea", event_id, action) for action in actions if action not in {"site-validation"}]
        record = {"schema_name": "publishing-house.editorial-event", "schema_version": SCHEMA_VERSION,
                  "id": event_id, "kind": kind, "source": event["source"], "occurred_at": event["occurred_at"],
                  "actions": actions, "decision": "no-editorial-action" if not actions else "storydesk-candidate",
                  "created_at": now(), "evidence": event.get("evidence", []), "storydesk_idea_ids": storydesk_ids}
        atomic_json(target, record, replace=False)
        for action in actions:
            if action in {"site-validation"}:
                continue
            idea_id = stable_id("idea", event_id, action)
            payload = {"schema_version": SCHEMA_VERSION, "title": f"{action}: {event.get('title', kind)}",
                       "detail": f"Event {event_id} proposed {action}; no publication effect authorized",
                       "event_id": event_id, "editorial_action": action,
                       "provenance": [{"kind": "event", "source": str(target), "checksum": sha256(target)}]}
            self._storydesk_mutation("idea add", idea_id, payload)
        return {"id": event_id, "actions": actions, "storydesk_idea_ids": storydesk_ids, "path": str(target)}

    def doctor(self) -> dict[str, Any]:
        checks: list[dict[str, Any]] = []
        for name, path, required in [
            ("storydesk", self.storydesk, True), ("kujo", self.kujo, True),
            ("dispatch", self.repos / "dispatch", True), ("agents-sdk", self.repos / "agents-sdk", True),
            ("presswire", self.repos / "presswire/bin/presswire", True),
            ("lens", self.repos / "lens/lens", False), ("eval", self.repos / "eval/main.kujo", False),
        ]:
            available = path.exists()
            checks.append({"name": name, "available": available, "required": required})
        configured_adapter = os.environ.get("PUBLISHING_HOUSE_PHASE_ADAPTER", "").strip()
        adapter_path = Path(configured_adapter).expanduser() if configured_adapter else None
        checks.append({"name": "live-phase-adapter",
                       "available": bool(adapter_path and adapter_path.is_file() and os.access(adapter_path, os.X_OK)),
                       "required": False, "configured": bool(configured_adapter),
                       "path": str(adapter_path.resolve()) if adapter_path else ""})
        try:
            profile_count = len(self.profiles()) if (self.state / "house.json").exists() else 0
        except OperatorError as exc:
            checks.append({"name": "publication-profiles", "available": False, "required": True, "error": str(exc)})
            profile_count = 0
        ok = all(check["available"] for check in checks if check["required"])
        return {"ok": ok, "checks": checks, "publication_profiles": profile_count}

    def golden_path(self, output: Path) -> dict[str, Any]:
        """Run the real eleven-kit, no-network Publishing House proof."""
        self.require_initialized()
        output = output.expanduser().resolve()
        if output.exists():
            raise OperatorError("output_exists", str(output))
        env = dict(os.environ, KUJO_REPOS=str(self.repos), KUJO_BIN=str(self.kujo))
        result = subprocess.run(["bash", str(WORKFLOWS_ROOT / "scripts/run-publishing-house-fixture.sh"), "--out", str(output)],
                                cwd=WORKFLOWS_ROOT, text=True, capture_output=True, env=env, timeout=900)
        if result.returncode:
            raise OperatorError("golden_path_failed", (result.stdout + result.stderr).strip())
        value = json.loads(result.stdout)
        proof = Path(value["proof"])
        return {"proof": str(proof), "sha256": sha256(proof), "workflow_count": value["workflow_count"],
                "record_references_checked": value["record_references_checked"],
                "agent_receipts_checked": value["agent_receipts_checked"], "external_effect": False}

    def _fixture_phase(self, item: dict[str, Any], phase: str) -> dict[str, Any]:
        artifact_dir = self.state / "runs" / item["id"] / phase
        artifact_dir.mkdir(parents=True, exist_ok=True)
        body = {"item_id": item["id"], "phase": phase, "publication": item["publication"],
                "source": item["source"], "created_at": now(), "fixture": True,
                "lineage": item.get("receipts", [])[-1:]}
        path = artifact_dir / "artifact.json"
        atomic_json(path, body)
        return {"phase": phase, "artifact": str(path), "sha256": sha256(path), "external_effect": False}

    def _live_phase(self, item: dict[str, Any], phase: str) -> dict[str, Any]:
        """Invoke one explicitly configured, bounded production phase adapter."""
        configured = os.environ.get("PUBLISHING_HOUSE_PHASE_ADAPTER", "").strip()
        if not configured:
            raise OperatorError("live_worker_adapter_unavailable", "PUBLISHING_HOUSE_PHASE_ADAPTER is not configured")
        adapter = Path(configured).expanduser().resolve()
        if not adapter.is_file() or not os.access(adapter, os.X_OK):
            raise OperatorError("live_worker_adapter_unavailable", f"phase adapter is not executable: {adapter}")
        request = {
            "schema_name": "publishing-house.phase-request", "schema_version": SCHEMA_VERSION,
            "item": item, "phase": phase, "profile": self._profile(item["publication"]),
            "state_root": str(self.state), "repos_root": str(self.repos),
            "approval_reference": item.get("approval_reference"),
        }
        try:
            timeout = int(os.environ.get("PUBLISHING_HOUSE_PHASE_TIMEOUT_SECONDS", "900"))
        except ValueError as exc:
            raise OperatorError("invalid_live_worker_timeout", "phase timeout must be an integer") from exc
        try:
            result = subprocess.run([str(adapter)], input=json.dumps(request), text=True, capture_output=True,
                                    timeout=max(1, min(timeout, 3600)), env=dict(os.environ))
        except subprocess.TimeoutExpired as exc:
            raise OperatorError("live_worker_timeout", f"phase adapter timed out for {phase}") from exc
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise OperatorError("invalid_live_worker_receipt", "phase adapter did not return JSON") from exc
        if not isinstance(response, dict):
            raise OperatorError("invalid_live_worker_receipt", "phase adapter response must be an object")
        if result.returncode or not response.get("ok"):
            # Adapter stderr can contain provider diagnostics or credentials and
            # is deliberately excluded from durable operator state.
            message = str(response.get("error") or "phase adapter failed")[:1000]
            raise OperatorError(str(response.get("error_code") or "live_worker_failure"), message)
        receipt = response.get("data")
        if not isinstance(receipt, dict):
            raise OperatorError("invalid_live_worker_receipt", "phase adapter data must be an object")
        required = {"schema_name", "schema_version", "item_id", "phase", "artifact", "sha256", "external_effect"}
        if receipt.get("schema_name") != "publishing-house.phase-receipt" or receipt.get("schema_version") != SCHEMA_VERSION or not required.issubset(receipt):
            raise OperatorError("invalid_live_worker_receipt", "phase adapter receipt is incomplete")
        if receipt["item_id"] != item["id"] or receipt["phase"] != phase:
            raise OperatorError("invalid_live_worker_receipt", "phase adapter receipt does not match the request")
        artifact = Path(str(receipt["artifact"])).expanduser().resolve()
        if not artifact.is_file() or sha256(artifact) != receipt["sha256"]:
            raise OperatorError("live_worker_checksum_mismatch", "phase artifact is missing or its checksum does not match")
        if phase != "approval-publication" and receipt["external_effect"]:
            raise OperatorError("policy_violation", f"{phase} may not report a publication effect")
        if phase == "approval-publication" and receipt["external_effect"] and receipt.get("effect_status") not in {"published", "corrected", "unpublished"}:
            raise OperatorError("invalid_publication_receipt", "publication effects require an explicit effect_status")
        return receipt

    def _latest_artifact_checksum(self, item: dict[str, Any]) -> str:
        receipts = item.get("receipts", [])
        if not receipts:
            raise OperatorError("artifact_missing", item["id"])
        return str(receipts[-1]["sha256"])

    def _requires_human(self, item: dict[str, Any]) -> bool:
        profile = self._profile(item["publication"])
        automatic = set(profile["approval_policy"].get("automatic_classes", []))
        return item["type"] not in automatic

    def _profile(self, profile_id: str) -> dict[str, Any]:
        path = self.state / "profiles" / f"{profile_id}.json"
        if not path.is_file():
            raise OperatorError("unknown_publication", profile_id)
        value = read_data(path)
        self._validate_profile(value)
        return value

    def _storydesk_mutation(self, command: str, record_id: str, payload: dict[str, Any]) -> None:
        if not self.storydesk.is_file() or not self.kujo.is_file():
            raise OperatorError("storydesk_unavailable", "StoryDesk or Kujo runtime is unavailable")
        record = self.state / "storydesk/records" / f"{record_id}.json"
        if record.exists():
            return
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
            json.dump(payload, handle)
            payload_path = Path(handle.name)
        try:
            result = self._tool([str(self.storydesk), *command.split(), "--state", str(self.state / "storydesk"),
                                 "--input", str(payload_path), "--actor", "publishing-house-operator",
                                 "--id", record_id, "--json"])
            if not result.get("ok"):
                raise OperatorError(str(result.get("error_code", "storydesk_failure")), str(result.get("error", "StoryDesk mutation failed")))
        finally:
            payload_path.unlink(missing_ok=True)

    def _tool(self, argv: list[str], allow_failure: bool = False) -> dict[str, Any]:
        env = dict(os.environ, KUJO_BIN=str(self.kujo))
        result = subprocess.run(argv, text=True, capture_output=True, env=env, timeout=60)
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            data = {"ok": False, "error": (result.stdout + result.stderr).strip(), "error_code": "invalid_tool_output"}
        if result.returncode and not allow_failure:
            raise OperatorError(str(data.get("error_code", "tool_failed")), str(data.get("error", "tool failed")))
        return data

    def _notify(self, kind: str, message: str, detail: dict[str, Any]) -> None:
        if kind not in NOTIFICATIONS:
            raise OperatorError("invalid_notification_class", kind)
        notification_id = stable_id("notice", kind, message, json.dumps(detail, sort_keys=True))
        path = self.state / "notifications" / f"{notification_id}.json"
        if not path.exists():
            atomic_json(path, {"id": notification_id, "class": kind, "message": message, "detail": detail, "created_at": now()}, replace=False)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="publishing-house")
    p.add_argument("--state", default=os.environ.get("PUBLISHING_HOUSE_STATE", ".publishing-house"))
    p.add_argument("--repos", default=os.environ.get("KUJO_REPOS", str(WORKFLOWS_ROOT.parent)))
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    publication = sub.add_parser("publication")
    publication_sub = publication.add_subparsers(dest="publication_command", required=True)
    publication_sub.add_parser("list")
    add = publication_sub.add_parser("add"); add.add_argument("profile")
    intake = sub.add_parser("intake"); intake.add_argument("--publication", required=True); intake.add_argument("--source", action="append", default=[])
    intake.add_argument("--text"); intake.add_argument("--title"); intake.add_argument("--format", default="article"); intake.add_argument("--priority", default="normal")
    plan = sub.add_parser("plan"); plan_sub = plan.add_subparsers(dest="plan_command", required=True)
    imp = plan_sub.add_parser("import"); imp.add_argument("path")
    event = sub.add_parser("event"); event.add_argument("--input", required=True)
    tick = sub.add_parser("tick"); tick.add_argument("--limit", type=int, default=4); tick.add_argument("--fixture", action="store_true")
    sub.add_parser("run").add_argument("--fixture", action="store_true")
    sub.add_parser("status"); sub.add_parser("approvals"); sub.add_parser("blocked"); sub.add_parser("history"); sub.add_parser("doctor")
    approve = sub.add_parser("approve"); approve.add_argument("item_id"); approve.add_argument("--checksum", required=True); approve.add_argument("--approver", required=True)
    resume = sub.add_parser("resume"); resume.add_argument("item_id")
    golden = sub.add_parser("golden-path"); golden.add_argument("--out", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    house = House(Path(args.state), Path(args.repos))
    try:
        if args.command == "init": result = house.init()
        elif args.command == "publication" and args.publication_command == "list": result = {"publications": house.profiles()}
        elif args.command == "publication": result = house.add_profile(Path(args.profile))
        elif args.command == "intake":
            text = args.text
            if not text and not args.source and not sys.stdin.isatty(): text = sys.stdin.read()
            result = house.intake(args.publication, args.source, text, args.format, args.priority, args.title)
        elif args.command == "plan": result = house.import_plan(Path(args.path))
        elif args.command == "event": result = house.ingest_event(Path(args.input))
        elif args.command in {"tick", "run"}: result = house.tick(getattr(args, "limit", 4), args.fixture)
        elif args.command == "approve": result = house.approve(args.item_id, args.checksum, args.approver)
        elif args.command == "resume": result = house.resume(args.item_id)
        elif args.command == "doctor": result = house.doctor()
        elif args.command == "golden-path": result = house.golden_path(Path(args.out))
        else:
            status = house.status()
            if args.command == "approvals": result = {"approvals": status["approvals"]}
            elif args.command == "blocked": result = {"blocked": status["blocked"]}
            elif args.command == "history": result = {"runs": [read_data(p) for p in sorted((house.state / "runs").glob("*.json"))]}
            else: result = status
        envelope = {"ok": True, "data": result, "error": None, "error_code": None, "schema_version": SCHEMA_VERSION}
        print(json.dumps(envelope, indent=2 if args.json else None, sort_keys=True))
        return 0
    except (OperatorError, json.JSONDecodeError, OSError, subprocess.TimeoutExpired) as exc:
        code = exc.code if isinstance(exc, OperatorError) else "operator_failure"
        print(json.dumps({"ok": False, "data": None, "error": str(exc), "error_code": code, "schema_version": SCHEMA_VERSION}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
