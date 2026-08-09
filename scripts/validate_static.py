#!/usr/bin/env python3
"""Run self-contained syntax checks over tracked source and data files."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".runs", ".work", ".workcell", ".tmp", "__pycache__"}


def files_with_suffix(*suffixes: str) -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix in suffixes
        and not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    )


def run(command: list[str], failures: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        failures.append(f"{' '.join(command)}: {detail}")


def main() -> int:
    failures: list[str] = []
    counts = {"shell": 0, "javascript": 0, "python": 0, "json": 0, "yaml": 0}

    for path in files_with_suffix(".sh"):
        counts["shell"] += 1
        run(["bash", "-n", str(path)], failures)

    node = shutil.which("node")
    javascript = files_with_suffix(".js")
    if javascript and not node:
        failures.append("node is required to syntax-check JavaScript files")
    elif node:
        for path in javascript:
            counts["javascript"] += 1
            run([node, "--check", str(path)], failures)

    for path in files_with_suffix(".py"):
        counts["python"] += 1
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (OSError, SyntaxError, UnicodeError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")

    for path in files_with_suffix(".json"):
        counts["json"] += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")

    for path in files_with_suffix(".yml", ".yaml"):
        counts["yaml"] += 1
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError, UnicodeError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")

    if failures:
        print("static validation: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    summary = " ".join(f"{name}={count}" for name, count in counts.items())
    print(f"static validation: PASS ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
