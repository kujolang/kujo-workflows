#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_catalog.py"


class CatalogValidatorTests(unittest.TestCase):
    def run_validator(self, catalog: dict, skills: dict[str, str] | None = None, tools: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            skills_root = base / "skills"
            (skills_root / "skills").mkdir(parents=True)
            for name, body in (skills or {"skill": "---\nname: skill\n---\n"}).items():
                path = skills_root / "skills" / name / "SKILL.md"
                path.parent.mkdir(parents=True)
                path.write_text(body, encoding="utf-8")
            tools_root = base / "tools"
            tools_root.mkdir()
            for tool in tools or []:
                (tools_root / tool / ".git").mkdir(parents=True)
            workflow_root = base / "workflows"
            (workflow_root / "entry").mkdir(parents=True)
            (workflow_root / "docs").mkdir()
            (workflow_root / "entry" / "run.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            (workflow_root / "docs" / "README.md").write_text("docs\n", encoding="utf-8")
            (workflow_root / "audit").mkdir()
            catalog_path = workflow_root / "audit" / "workflow-catalog.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            return subprocess.run(
                ["python3", str(VALIDATOR), "--catalog", str(catalog_path), "--skills-root", str(skills_root), "--tools-root", str(tools_root)],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_repository_catalog_passes(self) -> None:
        result = subprocess.run(["python3", str(VALIDATOR)], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_skill_fails_closed(self) -> None:
        catalog = {
            "schema": "kujo.workflow-catalog/v1",
            "active_workflows": [{"id": "x", "path": "entry", "entry": "entry/run.sh", "skills": [{"name": "missing", "path": "skills/missing/SKILL.md", "compatibility": "compatible"}], "tools": ["loop-engineering"], "inputs": ["x"], "outputs": ["x"], "approval_boundaries": ["x"], "tests": ["x"], "documentation": ["docs/README.md"]}],
        }
        result = self.run_validator(catalog)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown skill", result.stdout)

    def test_unknown_tool_fails_closed(self) -> None:
        catalog = {
            "schema": "kujo.workflow-catalog/v1",
            "active_workflows": [{"id": "x", "path": "entry", "entry": "entry/run.sh", "skills": [{"name": "skill", "path": "skills/skill/SKILL.md", "compatibility": "compatible"}], "tools": ["missing-tool"], "inputs": ["x"], "outputs": ["x"], "approval_boundaries": ["x"], "tests": ["x"], "documentation": ["docs/README.md"]}],
        }
        result = self.run_validator(catalog)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("tool repository not found", result.stdout)


if __name__ == "__main__":
    unittest.main()
