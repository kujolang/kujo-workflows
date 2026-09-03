import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPOS = ROOT.parents[1]
CLI = ROOT / "bin/publishing-house"
HAS_RUNTIME = (REPOS / "kujo/target/release/kujo").is_file()


class OperatorTests(unittest.TestCase):
    def exec_cli(self, state, *args, input_text=None, ok=True, env=None):
        result = subprocess.run([str(CLI), "--state", str(state), "--repos", str(REPOS), "--json", *args],
                                text=True, input=input_text, capture_output=True, timeout=120,
                                env=env)
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return payload

    def test_init_profiles_doctor_and_idempotent_intake(self):
        if not HAS_RUNTIME: self.skipTest("Kujo release runtime unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "house"
            self.assertEqual(self.exec_cli(state, "init")["data"]["profiles"], 4)
            self.assertTrue(self.exec_cli(state, "doctor")["data"]["ok"])
            first = self.exec_cli(state, "intake", "--publication", "personal-blog", "--text", "Messy notes about agent projects")
            second = self.exec_cli(state, "intake", "--publication", "personal-blog", "--text", "Messy notes about agent projects")
            self.assertEqual(first["data"]["id"], second["data"]["id"])
            self.assertTrue(second["data"]["idempotent_replay"])
            pack = json.loads(Path(first["data"]["path"]).read_text())
            self.assertTrue(Path(pack["sources"][0]["preserved_path"]).is_file())
            self.assertTrue((state / "storydesk/records" / f"{first['data']['storydesk_idea_id']}.json").is_file())

    def test_plan_dependency_tick_resume_and_low_risk_auto_flow(self):
        if not HAS_RUNTIME: self.skipTest("Kujo release runtime unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "house"
            self.exec_cli(state, "init")
            imported = self.exec_cli(state, "plan", "import", str(ROOT / "fixtures/september-2026.json"))
            replay = self.exec_cli(state, "plan", "import", str(ROOT / "fixtures/september-2026.json"))
            self.assertEqual(imported["data"]["items"], 4)
            self.assertTrue(replay["data"]["idempotent_replay"])
            for _ in range(10): self.exec_cli(state, "tick", "--fixture", "--limit", "4")
            status = self.exec_cli(state, "status")["data"]
            self.assertIn("agents-are-projects", status["approvals"])
            self.assertNotIn("agent-catalog-sync", status["approvals"])
            self.assertGreaterEqual(status["counts"].get("completed", 0), 2)

    def test_missing_source_and_duplicate_lease_fail_closed(self):
        if not HAS_RUNTIME: self.skipTest("Kujo release runtime unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "house"
            self.exec_cli(state, "init")
            missing = self.exec_cli(state, "intake", "--publication", "personal-blog", "--source", str(Path(tmp) / "absent"), ok=False)
            self.assertEqual(missing["error_code"], "source_missing")
            (state / "locks/operator").mkdir(parents=True)
            locked = self.exec_cli(state, "tick", "--fixture", ok=False)
            self.assertEqual(locked["error_code"], "concurrent_run")

    def test_event_commissioning_is_policy_bounded_and_idempotent(self):
        if not HAS_RUNTIME: self.skipTest("Kujo release runtime unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "house"
            self.exec_cli(state, "init")
            first = self.exec_cli(state, "event", "--input", str(ROOT / "fixtures/release-event.json"))
            second = self.exec_cli(state, "event", "--input", str(ROOT / "fixtures/release-event.json"))
            self.assertEqual(first["data"]["actions"], ["documentation-obligation", "article-candidate", "social-candidate"])
            self.assertEqual(len(first["data"]["storydesk_idea_ids"]), 3)
            self.assertTrue(second["data"]["idempotent_replay"])

    def test_live_phase_adapter_advances_with_checksum_bound_receipt(self):
        if not HAS_RUNTIME: self.skipTest("Kujo release runtime unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "house"
            adapter = root / "adapter.py"
            adapter.write_text("""#!/usr/bin/env python3
import hashlib, json
from pathlib import Path
request = json.load(__import__('sys').stdin)
artifact = Path(request['state_root']) / 'runs' / request['item']['id'] / request['phase'] / 'live.json'
artifact.parent.mkdir(parents=True, exist_ok=True)
artifact.write_text(json.dumps({'item': request['item']['id'], 'phase': request['phase']}) + '\\n')
receipt = {'schema_name': 'publishing-house.phase-receipt', 'schema_version': '1.0.0',
           'item_id': request['item']['id'], 'phase': request['phase'], 'artifact': str(artifact),
           'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(), 'external_effect': False}
print(json.dumps({'ok': True, 'data': receipt}))
""", encoding="utf-8")
            adapter.chmod(0o700)
            env = dict(os.environ, PUBLISHING_HOUSE_PHASE_ADAPTER=str(adapter))
            self.exec_cli(state, "init", env=env)
            doctor = self.exec_cli(state, "doctor", env=env)["data"]
            live_check = next(check for check in doctor["checks"] if check["name"] == "live-phase-adapter")
            self.assertTrue(live_check["available"])
            self.exec_cli(state, "plan", "import", str(ROOT / "fixtures/september-2026.json"), env=env)
            result = self.exec_cli(state, "tick", "--limit", "1", env=env)["data"]
            self.assertEqual(result["selected"][0]["status"], "in_progress")
            item = json.loads((state / "items/agents-are-projects.json").read_text())
            self.assertEqual(item["phase_index"], 1)
            self.assertFalse(item["receipts"][0]["external_effect"])

    def test_live_adapter_failure_retries_then_blocks_and_can_resume(self):
        if not HAS_RUNTIME: self.skipTest("Kujo release runtime unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "house"
            adapter = root / "adapter.py"
            adapter.write_text("#!/usr/bin/env python3\nimport json\nprint(json.dumps({'ok': False, 'error_code': 'provider_unavailable', 'error': 'offline'}))\n", encoding="utf-8")
            adapter.chmod(0o700)
            env = dict(os.environ, PUBLISHING_HOUSE_PHASE_ADAPTER=str(adapter))
            self.exec_cli(state, "init", env=env)
            self.exec_cli(state, "plan", "import", str(ROOT / "fixtures/september-2026.json"), env=env)
            first = self.exec_cli(state, "tick", "--limit", "1", env=env)["data"]
            self.assertEqual(first["selected"][0]["status"], "retry_pending")
            second = self.exec_cli(state, "tick", "--limit", "1", env=env)["data"]
            self.assertEqual(second["selected"][0]["status"], "blocked")
            resumed = self.exec_cli(state, "resume", "agents-are-projects", env=env)["data"]
            self.assertEqual(resumed["status"], "in_progress")


if __name__ == "__main__": unittest.main()
