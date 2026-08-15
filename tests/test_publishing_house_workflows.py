import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOS = Path(os.environ.get("KUJO_REPOS", ROOT.parent))
HAS_RUNTIME = Path(os.environ.get("KUJO_BIN", REPOS / "kujo/target/release/kujo")).is_file() and all(
    (REPOS / name).is_dir()
    for name in ["dispatch", "agents-sdk", "kujo-agents", "kujo-skills", "storydesk", "dossier", "galleypack", "bluepencil", "versionseal", "presswire", "readersignal", "assetworks"]
)
requires_runtime = unittest.skipUnless(HAS_RUNTIME, "Publishing House runtime dependencies are not available")
WORKFLOWS = [
    "publishing-house-governance",
    "publishing-house-daily-desk",
    "publishing-house-commissioning",
    "publishing-house-evidence-dossier",
    "publishing-house-primary-piece",
    "publishing-house-asset-production",
    "publishing-house-editorial-review",
    "publishing-house-adaptation",
    "publishing-house-format-production",
    "publishing-house-approval-publication",
    "publishing-house-post-publication",
]


def run_workflow(workflow: str, request: Path, output: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ROOT / workflow / "bin" / "run"), "--request", str(request), "--out", str(output), "--json", *extra],
        cwd=ROOT / workflow,
        text=True,
        capture_output=True,
        timeout=180,
    )


class PublishingHouseWorkflowTests(unittest.TestCase):
    def write_request(self, directory: Path, workflow: str, mutate=None) -> Path:
        value = json.loads((ROOT / workflow / "fixtures" / "request.fixture.json").read_text())
        if mutate:
            mutate(value)
        path = directory / f"{workflow}-request.json"
        path.write_text(json.dumps(value))
        return path

    def test_all_workflow_contracts_and_bindings_are_bounded(self):
        for workflow in WORKFLOWS:
            config = json.loads((ROOT / workflow / "workflow.json").read_text())
            self.assertEqual(config["version"], "0.1.0")
            self.assertEqual(config["default_retry_policy"]["max_attempts"], 2)
            self.assertTrue(config["bindings"])
            for binding in config["bindings"]:
                self.assertTrue(binding["canonical_agent"].endswith("/AGENT.md"))
                self.assertTrue(binding["canonical_skill"].endswith("/SKILL.md"))
                self.assertTrue(binding["allowed_tools"])
                self.assertIn(binding["maximum_permission"], {"PROPOSE", "ACT"})
            self.assertNotIn("webops", json.dumps(config).lower())
            self.assertNotIn("chain of command", json.dumps(config).lower())

        primary = json.loads((ROOT / "publishing-house-primary-piece" / "workflow.json").read_text())
        self.assertEqual(
            primary["format_profile_routes"],
            {
                "flagship-feature": "Features Writer",
                "technical-walkthrough": "Technical Editor & Writer",
                "problem-solution": "Features Writer",
                "feature-update-explanation": "Technical Editor & Writer",
                "campaign-copy": "Campaign Copywriter",
            },
        )

    @requires_runtime
    def test_common_fail_closed_request_boundaries(self):
        cases = [
            ("missing", lambda value: value.pop("actor"), "missing_required_field"),
            ("schema", lambda value: value.__setitem__("schema_version", "2.0.0"), "incompatible_schema"),
            ("capability", lambda value: value["capabilities"][0].__setitem__("available", False), "missing_required_capability"),
            ("permission", lambda value: value.__setitem__("permission_mode", "ACT"), "permission_broadened"),
            ("secret", lambda value: value["input"].__setitem__("api_key", "not-a-real-secret"), "secret_rejected"),
            ("live", lambda value: value.__setitem__("mode", "live"), "live_adapter_unavailable"),
        ]
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            for name, mutate, expected in cases:
                request = self.write_request(temp_path, WORKFLOWS[0], mutate)
                result = run_workflow(WORKFLOWS[0], request, temp_path / name)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(expected, result.stdout + result.stderr)

    @requires_runtime
    def test_optional_capability_unavailable_is_honest_degradation(self):
        with tempfile.TemporaryDirectory() as temp:
            request = self.write_request(Path(temp), WORKFLOWS[0])
            output = Path(temp) / "run"
            result = run_workflow(WORKFLOWS[0], request, output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipt = json.loads((output / "capability-receipt.json").read_text())
            optional = {entry["name"]: entry["available"] for entry in receipt["optional"]}
            self.assertFalse(optional["runledger"])
            self.assertFalse(optional["watchdog"])

    @requires_runtime
    def test_agents_execute_loaded_canonical_contracts(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "run"
            result = run_workflow(WORKFLOWS[0], ROOT / WORKFLOWS[0] / "fixtures" / "request.fixture.json", output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipts = list((output / "agent-receipts").glob("*.json"))
            self.assertTrue(receipts)
            for path in receipts:
                receipt = json.loads(path.read_text())
                sdk = receipt["agents_sdk"]["result"]
                self.assertTrue(receipt["contract_loaded"])
                self.assertGreaterEqual(len(receipt["contract_paths"]), 8)
                self.assertEqual(receipt["instructions_sha256"], sdk["instructions_sha256"])
                self.assertEqual(receipt["instructions_bytes"], sdk["instructions_bytes"])

    @requires_runtime
    def test_record_references_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            missing = self.write_request(
                temp_path,
                WORKFLOWS[2],
                lambda value: value["input"].__setitem__(
                    "fixture_record_references",
                    [{"schema_version": "1.0.0", "record_id": "missing", "path": str(temp_path / "missing.json"), "checksum": "0" * 64}],
                ),
            )
            missing_result = run_workflow(WORKFLOWS[2], missing, temp_path / "missing-ref")
            self.assertNotEqual(missing_result.returncode, 0)
            self.assertIn("invalid_record_reference", missing_result.stdout + missing_result.stderr)

            record = temp_path / "record.json"
            record.write_text("{}\n")
            drifted = self.write_request(
                temp_path,
                WORKFLOWS[2],
                lambda value: value["input"].__setitem__(
                    "fixture_record_references",
                    [{"schema_version": "1.0.0", "record_id": "drifted", "path": str(record), "checksum": "0" * 64}],
                ),
            )
            drift_result = run_workflow(WORKFLOWS[2], drifted, temp_path / "drift-ref")
            self.assertNotEqual(drift_result.returncode, 0)
            self.assertIn("checksum_drift", drift_result.stdout + drift_result.stderr)

    @requires_runtime
    def test_primary_piece_format_profile_routes_writer(self):
        workflow = "publishing-house-primary-piece"
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            request = self.write_request(
                temp_path,
                workflow,
                lambda value: value["input"].__setitem__("format_profile", "technical-walkthrough"),
            )
            output = temp_path / "technical"
            result = run_workflow(workflow, request, output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipts = {path.name for path in (output / "agent-receipts").glob("*.json")}
            self.assertTrue(any("technical-editor-writer" in name for name in receipts))
            self.assertFalse(any("features-writer" in name for name in receipts))
            self.assertFalse(any("campaign-copywriter" in name for name in receipts))

    @requires_runtime
    def test_unsafe_output_path_is_rejected(self):
        workflow = WORKFLOWS[0]
        request = ROOT / workflow / "fixtures" / "request.fixture.json"
        result = run_workflow(workflow, request, Path("../unsafe-output"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe_path", result.stdout + result.stderr)

    @requires_runtime
    def test_approval_failure_matrix_and_no_effect(self):
        workflow = "publishing-house-approval-publication"
        faults = {
            "no_approval": "approval_required",
            "wrong_package": "wrong_package",
            "wrong_checksum": "checksum_drift",
            "wrong_destination": "destination_mismatch",
            "wrong_action": "action_mismatch",
            "expired_approval": "approval_expired",
            "revoked_approval": "approval_revoked",
            "changed_artifact": "checksum_drift",
            "missing_adapter": "adapter_unavailable",
            "failed_preflight": "preflight_failed",
            "fixture_external_publication": "fixture_external_effect_denied",
        }
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            base_request = self.write_request(temp_path, workflow)
            base_output = temp_path / "base"
            paused = run_workflow(workflow, base_request, base_output)
            self.assertEqual(paused.returncode, 0, paused.stdout + paused.stderr)
            self.assertEqual(json.loads((base_output / "completion-receipt.json").read_text())["outcome"], "paused")
            approval = (ROOT / "fixtures" / "publishing-house" / "fixture-approval.fixture.json").resolve()
            for fault, expected in faults.items():
                output = temp_path / fault
                shutil.copytree(base_output, output)
                request = self.write_request(temp_path, workflow, lambda value, fault=fault: value["input"].__setitem__("fixture_fault", fault))
                result = run_workflow(workflow, request, output, "--resume", "--fixture-approval", str(approval))
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(expected, result.stdout + result.stderr)
                self.assertFalse((output / "published" / "package-v2.md").exists())

    @requires_runtime
    def test_denied_act_and_invalid_fixture_approval(self):
        workflow = "publishing-house-approval-publication"
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            request = self.write_request(temp_path, workflow)
            output = temp_path / "run"
            self.assertEqual(run_workflow(workflow, request, output).returncode, 0)
            propose = self.write_request(temp_path, workflow, lambda value: value.__setitem__("permission_mode", "PROPOSE"))
            denied = run_workflow(workflow, propose, output, "--resume", "--fixture-approval", str((ROOT / "fixtures/publishing-house/fixture-approval.fixture.json").resolve()))
            self.assertNotEqual(denied.returncode, 0)
            self.assertIn("act_permission_denied", denied.stdout + denied.stderr)

    @requires_runtime
    def test_json_envelope_report_and_receipt_are_stable(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            request = self.write_request(temp_path, WORKFLOWS[1])
            output = temp_path / "run"
            first = run_workflow(WORKFLOWS[1], request, output)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            envelope = json.loads(first.stdout)
            self.assertEqual(set(envelope), {"ok", "data", "error", "error_code", "workflow_contract_version"})
            self.assertTrue((output / "report.md").is_file())
            receipt = json.loads((output / "completion-receipt.json").read_text())
            self.assertEqual(receipt["outcome"], "completed")
            second = run_workflow(WORKFLOWS[1], request, output)
            self.assertEqual(second.returncode, 0)
            self.assertTrue(json.loads(second.stdout)["data"]["idempotent_replay"])


if __name__ == "__main__":
    unittest.main()
