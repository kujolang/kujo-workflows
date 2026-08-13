from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "codebase-cleanup" / "cleanup.py"
SPEC = importlib.util.spec_from_file_location("codebase_cleanup", SCRIPT)
assert SPEC and SPEC.loader
cleanup = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cleanup
SPEC.loader.exec_module(cleanup)


class CodebaseCleanupTests(unittest.TestCase):
    def repo(
        self, files: dict[str, str]
    ) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        for name, body in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.invalid",
                "commit",
                "-qm",
                "fixture",
            ],
            cwd=root,
            check=True,
        )
        return temp, root

    def analyze(self, root: Path) -> list[dict]:
        findings, _, _ = cleanup.analyze(
            root, root, None, set(cleanup.CATEGORIES), "UNKNOWN"
        )
        return findings

    def finding(self, findings: list[dict], category: str, symbol: str) -> dict:
        return next(
            item
            for item in findings
            if item["category"] == category and item["symbol"] == symbol
        )

    def run_workflow(
        self, root: Path, *args: str
    ) -> tuple[subprocess.CompletedProcess[str], dict, Path]:
        output = root.parent / f"output-{root.name}-{len(args)}"
        command = [
            "python3",
            str(SCRIPT),
            "--repo",
            str(root),
            "--output",
            str(output),
            *args,
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        report = (
            json.loads((output / "report.json").read_text())
            if (output / "report.json").exists()
            else {}
        )
        return result, report, output

    def test_unused_private_code_is_proven(self) -> None:
        temp, root = self.repo(
            {
                "app.py": "def _unused():\n    return 1\n\ndef live():\n    return 2\n\nprint(live())\n"
            }
        )
        self.addCleanup(temp.cleanup)
        item = self.finding(self.analyze(root), "dead-code", "_unused")
        self.assertEqual(item["confidence"], "PROVEN")
        self.assertEqual(item["operation"]["type"], "remove-lines")

    def test_proven_dead_code_is_removed_with_approved_plan(self) -> None:
        temp, root = self.repo(
            {
                "app.py": "def _unused():\n    return 1\n\ndef live():\n    return 2\n\nprint(live())\n"
            }
        )
        self.addCleanup(temp.cleanup)
        first, report, output = self.run_workflow(
            root, "--verify-cmd", "python3 app.py"
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        target = self.finding(report["findings"], "dead-code", "_unused")
        plan = json.loads((output / "cleanup-plan.json").read_text())
        plan["approved_finding_ids"] = [target["id"]]
        plan_path = root.parent / "approved-plan.json"
        plan_path.write_text(json.dumps(plan))
        second, applied, _ = self.run_workflow(
            root, "--verify-cmd", "python3 app.py", "--apply-plan", str(plan_path)
        )
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotIn("_unused", (root / "app.py").read_text())
        self.assertEqual(applied["applied"][0]["status"], "applied")

    def test_exact_private_duplicate_can_be_consolidated(self) -> None:
        temp, root = self.repo(
            {
                "app.py": "def _first(x):\n    return x + 1\n\ndef _second(x):\n    return x + 1\n\ndef live():\n    return _second(2)\n\nprint(live())\n"
            }
        )
        self.addCleanup(temp.cleanup)
        item = next(
            f
            for f in self.analyze(root)
            if f["category"] == "duplication" and f["confidence"] == "PROVEN"
        )
        applied, _ = cleanup.apply_findings(root, [item])
        self.assertEqual(applied[0]["operation"], "consolidate-python-functions")
        text = (root / "app.py").read_text()
        self.assertNotIn("def _second", text)
        self.assertIn("return _first(2)", text)
        result = subprocess.run(
            ["python3", "app.py"], cwd=root, text=True, capture_output=True
        )
        self.assertEqual((result.returncode, result.stdout), (0, "3\n"))

    def test_intentional_duplication_is_preserved(self) -> None:
        temp, root = self.repo(
            {
                "app.py": "def _one(x):\n    # cleanup: intentional-duplication -- protocol isolation\n    return x + 1\n\ndef _two(x):\n    return x + 1\n"
            }
        )
        self.addCleanup(temp.cleanup)
        findings = self.analyze(root)
        self.assertTrue(
            any(
                f["category"] == "duplication" and f["confidence"] == "INTENTIONAL"
                for f in findings
            )
        )
        self.assertFalse(
            any(
                f["category"] == "duplication" and f["operation"]
                if "operation" in f
                else False
                for f in findings
            )
        )

    def test_public_dynamic_and_decorated_entries_are_not_proven_dead(self) -> None:
        temp, root = self.repo(
            {
                "app.py": "REGISTRY = {}\ndef route(fn):\n    REGISTRY[fn.__name__] = fn\n    return fn\n\n@route\ndef endpoint():\n    return 1\n\ndef public_api():\n    return 2\n\n__all__ = ['public_api']\n"
            }
        )
        self.addCleanup(temp.cleanup)
        findings = self.analyze(root)
        self.assertEqual(
            self.finding(findings, "dead-code", "endpoint")["confidence"], "UNKNOWN"
        )
        self.assertFalse(
            any(
                f["category"] == "dead-code"
                and f["symbol"] == "public_api"
                and f["confidence"] == "PROVEN"
                for f in findings
            )
        )

    def test_unused_dependency_is_detected_without_automatic_proven_claim(self) -> None:
        temp, root = self.repo(
            {
                "package.json": '{"dependencies":{"left-pad":"1.3.0"}}\n',
                "index.js": "console.log('ok')\n",
            }
        )
        self.addCleanup(temp.cleanup)
        item = self.finding(self.analyze(root), "dependencies", "left-pad")
        self.assertEqual(item["confidence"], "LIKELY")
        self.assertIn("binary", item["risk"])

    def test_verification_regression_rolls_cleanup_back(self) -> None:
        temp, root = self.repo(
            {"app.py": "def _unused():\n    return 1\n\nprint('ok')\n"}
        )
        self.addCleanup(temp.cleanup)
        first, report, output = self.run_workflow(
            root, "--verify-cmd", 'test -n "$(grep _unused app.py)"'
        )
        target = self.finding(report["findings"], "dead-code", "_unused")
        plan = json.loads((output / "cleanup-plan.json").read_text())
        plan["approved_finding_ids"] = [target["id"]]
        plan_path = root.parent / "regression-plan.json"
        plan_path.write_text(json.dumps(plan))
        second, report2, _ = self.run_workflow(
            root,
            "--verify-cmd",
            'test -n "$(grep _unused app.py)"',
            "--apply-plan",
            str(plan_path),
        )
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("_unused", (root / "app.py").read_text())
        self.assertTrue(report2["verification"]["rollback_performed"])
        self.assertEqual(
            report2["applied"][0]["status"], "rolled-back-verification-regression"
        )

    def test_documentation_drift_is_reported(self) -> None:
        temp, root = self.repo(
            {
                "README.md": "Run `scripts/removed.sh` to verify.\n",
                "app.py": "print('ok')\n",
            }
        )
        self.addCleanup(temp.cleanup)
        item = self.finding(self.analyze(root), "documentation", "scripts/removed.sh")
        self.assertEqual(item["confidence"], "LIKELY")

    def test_preexisting_failures_are_distinguished(self) -> None:
        temp, root = self.repo({"app.py": "print('ok')\n"})
        self.addCleanup(temp.cleanup)
        result, report, _ = self.run_workflow(
            root, "--verify-cmd", "echo existing >&2; exit 7"
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(report["verification"]["pre_existing_failures"]), 1)
        self.assertEqual(report["verification"]["cleanup_regressions"], [])

    def test_clean_repository_can_return_zero_actionable_findings(self) -> None:
        temp, root = self.repo(
            {
                "app.py": "def public(value):\n    return value + 1\n\nprint(public(1))\n",
                "README.md": "Small fixture.\n",
            }
        )
        self.addCleanup(temp.cleanup)
        findings, _, _ = cleanup.analyze(
            root, root, None, set(cleanup.CATEGORIES), "LIKELY"
        )
        self.assertEqual(findings, [])

    def test_analysis_only_does_not_modify_repository(self) -> None:
        temp, root = self.repo({"app.py": "def _unused():\n    return 1\n"})
        self.addCleanup(temp.cleanup)
        before = subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, text=True, capture_output=True
        ).stdout
        result, report, _ = self.run_workflow(root)
        after = subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, text=True, capture_output=True
        ).stdout
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report["mode"], "analysis-only")
        self.assertEqual(before, after)

    def test_output_is_deterministic_for_same_input(self) -> None:
        temp, root = self.repo({"app.py": "def _unused():\n    return 1\n"})
        self.addCleanup(temp.cleanup)
        findings1, metrics1, _ = cleanup.analyze(
            root, root, None, set(cleanup.CATEGORIES), "UNKNOWN"
        )
        findings2, metrics2, _ = cleanup.analyze(
            root, root, None, set(cleanup.CATEGORIES), "UNKNOWN"
        )
        self.assertEqual(
            json.dumps(findings1, sort_keys=True), json.dumps(findings2, sort_keys=True)
        )
        self.assertEqual(metrics1, metrics2)

    def test_scope_and_category_controls(self) -> None:
        temp, root = self.repo(
            {
                "one/app.py": "def _unused():\n    return 1\n",
                "two/app.py": "def _other():\n    return 2\n",
            }
        )
        self.addCleanup(temp.cleanup)
        findings, _, _ = cleanup.analyze(
            root, root / "one", None, {"dead-code"}, "PROVEN"
        )
        self.assertEqual({item["path"] for item in findings}, {"one/app.py"})
        self.assertTrue(all(item["category"] == "dead-code" for item in findings))

    def test_integration_disposition_uses_verified_tool_boundaries(self) -> None:
        temp, root = self.repo({"app.py": "print('ok')\n"})
        self.addCleanup(temp.cleanup)
        integrations = {
            item["tool"]: item for item in cleanup.detect_tool_integrations(root)
        }
        self.assertEqual(
            set(integrations),
            {
                "scout",
                "fence",
                "concord",
                "kennel",
                "changebucket",
                "patchbrief",
                "shipcheck",
                "casefile",
                "runledger",
                "dispatch",
            },
        )
        self.assertFalse(integrations["fence"]["applicable"])
        self.assertFalse(integrations["dispatch"]["applicable"])
        self.assertIn("run retention", integrations["dispatch"]["role"])

    def test_bounded_companion_command_timeout_is_evidence(self) -> None:
        temp, root = self.repo({"app.py": "print('ok')\n"})
        self.addCleanup(temp.cleanup)
        result = cleanup.run_command("sleep 5", root, timeout_seconds=1)
        self.assertEqual(result["exit_code"], 124)
        self.assertIn("TIMEOUT after 1 seconds", result["output_tail"])


if __name__ == "__main__":
    unittest.main()
