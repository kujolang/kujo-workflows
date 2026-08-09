#!/usr/bin/env python3
"""Validate the workflow catalog against the checked-out Kujo skills and tools."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


COMPATIBILITY = {
    "compatible",
    "compatible-but-under-tested",
    "update-required",
    "migration-required",
    "deprecated",
    "broken",
    "unknown",
}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"catalog root must be an object: {path}")
    return value


def frontmatter_name(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines()[:24]:
        match = re.match(r"^name:\s*[\"']?([^\"']+?)[\"']?\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def validate(catalog_path: Path, skills_root: Path, tools_root: Path, *, check_external: bool = True) -> list[str]:
    errors: list[str] = []
    try:
        catalog = load_json(catalog_path)
    except ValueError as exc:
        return [str(exc)]

    if catalog.get("schema") != "kujo.workflow-catalog/v1":
        errors.append("catalog schema must be kujo.workflow-catalog/v1")

    workflows = catalog.get("active_workflows")
    if not isinstance(workflows, list) or not workflows:
        return ["active_workflows must be a non-empty array"]

    aliases = catalog.get("canonical_tool_aliases", {})
    if not isinstance(aliases, dict):
        errors.append("canonical_tool_aliases must be an object")
        aliases = {}

    known_skills: dict[str, Path] = {}
    skill_dir = skills_root / "skills"
    if check_external and not skill_dir.is_dir():
        errors.append(f"skills directory not found: {skill_dir}")
    elif check_external:
        for skill_file in sorted(skill_dir.glob("*/SKILL.md")):
            name = frontmatter_name(skill_file)
            if name:
                known_skills[name] = skill_file

    seen_ids: set[str] = set()
    for workflow in workflows:
        if not isinstance(workflow, dict):
            errors.append("each workflow entry must be an object")
            continue
        workflow_id = workflow.get("id")
        if not isinstance(workflow_id, str) or not workflow_id:
            errors.append("workflow is missing a non-empty id")
            continue
        if workflow_id in seen_ids:
            errors.append(f"duplicate workflow id: {workflow_id}")
        seen_ids.add(workflow_id)

        workflow_path = workflow.get("path")
        if not isinstance(workflow_path, str):
            errors.append(f"{workflow_id}: path is required")
        elif not (catalog_path.parents[2] / workflow_path).exists():
            errors.append(f"{workflow_id}: workflow path does not exist: {workflow_path}")

        entry = workflow.get("entry")
        if not isinstance(entry, str) or not (catalog_path.parents[2] / entry).exists():
            errors.append(f"{workflow_id}: entry does not exist: {entry}")

        skills = workflow.get("skills")
        if not isinstance(skills, list) or not skills:
            errors.append(f"{workflow_id}: at least one canonical skill is required")
        else:
            for relation in skills:
                if not isinstance(relation, dict):
                    errors.append(f"{workflow_id}: skill relationship must be an object")
                    continue
                name = relation.get("name")
                path = relation.get("path")
                compatibility = relation.get("compatibility")
                if not isinstance(name, str) or not name:
                    errors.append(f"{workflow_id}: skill name must be a non-empty string")
                    continue
                if check_external and name not in known_skills:
                    errors.append(f"{workflow_id}: unknown skill: {name}")
                    continue
                expected = f"skills/{name}/SKILL.md"
                if path != expected:
                    errors.append(f"{workflow_id}: non-canonical path for {name}: {path} (expected {expected})")
                if compatibility not in COMPATIBILITY:
                    errors.append(f"{workflow_id}: invalid compatibility for {name}: {compatibility}")
                if check_external:
                    actual = known_skills[name].relative_to(skills_root).as_posix()
                    if actual != expected:
                        errors.append(f"{workflow_id}: skill identity/path mismatch for {name}: {actual}")

        tools = workflow.get("tools")
        if not isinstance(tools, list):
            errors.append(f"{workflow_id}: tools must be an array")
        else:
            for tool in tools:
                if not isinstance(tool, str):
                    errors.append(f"{workflow_id}: tool name must be a string")
                    continue
                if tool in aliases:
                    errors.append(f"{workflow_id}: non-canonical tool alias {tool}; use {aliases[tool]}")
                    continue
                if tool in {"kujo", "loop-engineering"}:
                    continue
                if check_external:
                    tool_path = tools_root / tool
                    if not (tool_path / ".git").exists():
                        errors.append(f"{workflow_id}: tool repository not found: {tool}")

        for field in ("inputs", "outputs", "approval_boundaries", "tests", "documentation"):
            if not isinstance(workflow.get(field), list) or not workflow[field]:
                errors.append(f"{workflow_id}: {field} must be a non-empty array")
        for doc in workflow.get("documentation", []) if isinstance(workflow.get("documentation"), list) else []:
            if not (catalog_path.parents[2] / doc).exists():
                errors.append(f"{workflow_id}: documentation path does not exist: {doc}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("docs/audit/workflow-catalog.json"))
    parser.add_argument("--skills-root", type=Path)
    parser.add_argument("--tools-root", type=Path)
    parser.add_argument(
        "--structure-only",
        action="store_true",
        help="validate repository-owned catalog structure without requiring sibling skill/tool checkouts",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    catalog_path = args.catalog.resolve()
    workflows_root = catalog_path.parents[2]
    skills_root = (args.skills_root or workflows_root.parent / "kujo-skills").resolve()
    tools_root = (args.tools_root or workflows_root.parent).resolve()
    errors = validate(catalog_path, skills_root, tools_root, check_external=not args.structure_only)
    result = {
        "ok": not errors,
        "catalog": str(catalog_path),
        "workflow_count": 0,
        "mode": "structure-only" if args.structure_only else "full",
        "errors": errors,
    }
    try:
        result["workflow_count"] = len(load_json(catalog_path).get("active_workflows", []))
    except ValueError:
        pass
    if args.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif errors:
        print("workflow catalog: FAIL")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"workflow catalog: PASS ({result['workflow_count']} workflows)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
