#!/usr/bin/env python3
"""Synchronize Publishing House workflow entries in the audit catalog."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "docs/audit/workflow-catalog.json"
SKILL = {
    "name": "kujo-publishing-house-workflows",
    "path": "skills/kujo-publishing-house-workflows/SKILL.md",
    "compatibility": "compatible",
}
PURPOSES = {
    "publishing-house-governance": "Set a bounded house mandate, portfolio decision, operating priorities, and accountable handoffs.",
    "publishing-house-adaptation": "Create a versioned cross-format adaptation plan without expanding approved claim boundaries.",
    "publishing-house-format-production": "Produce reviewable newsletter, social, case-study, and video/audio packages from approved lineage.",
}


def entry(workflow_id: str) -> dict:
    config = json.loads((ROOT / workflow_id / "workflow.json").read_text())
    return {
        "id": workflow_id,
        "path": workflow_id,
        "status": "production-capable-with-limitations",
        "purpose": PURPOSES[workflow_id],
        "entry": f"{workflow_id}/bin/run",
        "skills": [
            SKILL,
            {"name": "kujo-dispatch-workflows", "path": "skills/kujo-dispatch-workflows/SKILL.md", "compatibility": "compatible"},
            {"name": "kujo-agents-sdk-workflows", "path": "skills/kujo-agents-sdk-workflows/SKILL.md", "compatibility": "compatible"},
        ],
        "tools": config["tools"],
        "inputs": ["publishing-house.workflow-run-request/v1", "portable House, Brand, and Audience profiles", "declared local capabilities"],
        "outputs": ["capability-receipt.json", "agent-contracts/*.md", "agent-receipts/*.json", "Dispatch state/trace/report artifacts", "run-summary.json", "completion-receipt.json or blocker.json"],
        "approval_boundaries": config["approval_boundaries"],
        "state_and_recovery": "Kujo-owned state.json with bounded retries, idempotent completed replay, and Dispatch canonical artifacts; approval workflow adds exact paused resume.",
        "evidence": "deterministic offline fixture records and docs/evidence/publishing-house-fixture-proof.json",
        "tests": [f"bash {workflow_id}/scripts/test.sh", "python3 -m unittest discover -s tests -p 'test_publishing_house*.py'", "bash scripts/run-publishing-house-fixture.sh --out <temporary-directory>"],
        "documentation": [f"{workflow_id}/README.md", f"{workflow_id}/HOWTO.md", "docs/publishing-house/README.md"],
        "production_readiness": "production-capable-with-limitations",
    }


def main() -> None:
    value = json.loads(CATALOG.read_text())
    workflows = value["active_workflows"]
    for item in workflows:
        if item["id"].startswith("publishing-house-") and not any(skill["name"] == SKILL["name"] for skill in item["skills"]):
            item["skills"].insert(0, SKILL.copy())
        if item["id"].startswith("publishing-house-") and "agent-contracts/*.md" not in item["outputs"]:
            item["outputs"].insert(1, "agent-contracts/*.md")
        if item["id"].startswith("publishing-house-"):
            item["tests"] = ["python3 -m unittest discover -s tests -p 'test_publishing_house*.py'" if test == "python3 -m unittest tests.test_publishing_house_workflows" else test for test in item["tests"]]
    existing = {item["id"] for item in workflows}
    for workflow_id in PURPOSES:
        if workflow_id not in existing:
            workflows.append(entry(workflow_id))
    value["active_workflows"] = sorted(workflows, key=lambda item: item["id"])
    CATALOG.write_text(json.dumps(value, indent=2) + "\n")


if __name__ == "__main__":
    main()
