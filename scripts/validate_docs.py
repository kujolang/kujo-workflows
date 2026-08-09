#!/usr/bin/env python3
"""Validate public Markdown links, portable paths, and release metadata."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".runs", ".work", ".workcell", ".tmp", "__pycache__"}
REQUIRED_FILES = ("README.md", "LICENSE", "VERSION", "CHANGELOG.md")
REQUIRED_README_SECTIONS = ("Start Here", "Workflow Catalog", "Verification", "Known Limits", "License")
INLINE_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.md")
        if not any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)
    )


def slugify(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("`", "").lower()
    value = re.sub(r"[^\w\- ]", "", value, flags=re.UNICODE)
    return re.sub(r"[ -]+", "-", value.strip())


def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    result: set[str] = set()
    for heading in HEADING.findall(path.read_text(encoding="utf-8")):
        base = slugify(heading)
        count = seen.get(base, 0)
        seen[base] = count + 1
        result.add(base if count == 0 else f"{base}-{count}")
    return result


def normalize_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    match = re.match(r"^(\S+)(?:\s+[\"'].*[\"'])?$", target)
    return unquote(match.group(1) if match else target)


def validate_link(source: Path, raw: str, failures: list[str]) -> None:
    target = normalize_target(raw)
    if not target or target.startswith(("http://", "https://", "mailto:", "data:")):
        return
    file_part, separator, fragment = target.partition("#")
    destination = source if not file_part else (source.parent / file_part).resolve()
    try:
        destination.relative_to(ROOT)
    except ValueError:
        failures.append(f"{source.relative_to(ROOT)}: relative link escapes repository: {target}")
        return
    if not destination.exists():
        failures.append(f"{source.relative_to(ROOT)}: missing link target: {target}")
        return
    if separator and fragment and destination.suffix.lower() == ".md":
        if fragment.lower() not in anchors(destination):
            failures.append(f"{source.relative_to(ROOT)}: missing Markdown anchor: {target}")


def main() -> int:
    failures: list[str] = []
    for name in REQUIRED_FILES:
        if not (ROOT / name).is_file():
            failures.append(f"missing required release file: {name}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    for section in REQUIRED_README_SECTIONS:
        if f"## {section}" not in readme:
            failures.append(f"README.md: missing required section: {section}")

    files = markdown_files()
    for path in files:
        text = path.read_text(encoding="utf-8")
        if "/Users/" in text:
            failures.append(f"{path.relative_to(ROOT)}: contains a maintainer-specific /Users path")
        for raw in INLINE_LINK.findall(text):
            validate_link(path, raw, failures)
        for raw in REFERENCE_LINK.findall(text):
            validate_link(path, raw, failures)

    if failures:
        print("documentation validation: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"documentation validation: PASS ({len(files)} Markdown files, {len(REQUIRED_FILES)} release files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
