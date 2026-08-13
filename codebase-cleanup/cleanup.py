#!/usr/bin/env python3
"""Evidence-first repository cleanup analyzer and controlled applicator."""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time
import tokenize
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "kujo.codebase-cleanup/v1"
CATEGORIES = (
    "dead-code",
    "duplication",
    "unnecessary-abstraction",
    "over-engineering",
    "legacy-compatibility",
    "dependencies",
    "configuration",
    "tests",
    "documentation",
    "architecture",
)
CONFIDENCE_ORDER = {"UNKNOWN": 0, "INTENTIONAL": 1, "LIKELY": 2, "PROVEN": 3}
SOURCE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".kujo",
    ".rs",
    ".go",
    ".java",
    ".rb",
    ".php",
}
TEXT_SUFFIXES = SOURCE_SUFFIXES | {
    ".md",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".sh",
    ".txt",
}
IGNORED_DIRS = {
    ".git",
    ".cleanup-runs",
    ".runs",
    ".work",
    ".workcell",
    ".suites",
    "outputs",
    "results",
    "tmp",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "coverage",
}
TEST_PARTS = {
    "test",
    "tests",
    "spec",
    "specs",
    "fixtures",
    "fixture",
    "snapshots",
    "__snapshots__",
}


def stable_id(category: str, path: str, symbol: str, detail: str) -> str:
    digest = hashlib.sha256(
        f"{category}\0{path}\0{symbol}\0{detail}".encode()
    ).hexdigest()[:12]
    return f"CC-{category.upper().replace('-', '_')}-{digest}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


@dataclass
class Finding:
    category: str
    confidence: str
    path: str
    symbol: str
    summary: str
    evidence: list[str]
    risk: str
    action: str
    affected_behavior: str = "none identified"
    public_api_impact: str = "none identified"
    related_tests: list[str] = field(default_factory=list)
    documentation_impact: str = "none identified"
    operation: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        detail = "|".join(self.evidence)
        value = {
            "id": stable_id(self.category, self.path, self.symbol, detail),
            "category": self.category,
            "confidence": self.confidence,
            "path": self.path,
            "symbol": self.symbol,
            "summary": self.summary,
            "evidence": self.evidence,
            "risk": self.risk,
            "recommended_action": self.action,
            "affected_behavior": self.affected_behavior,
            "public_api_impact": self.public_api_impact,
            "related_tests": self.related_tests,
            "documentation_impact": self.documentation_impact,
        }
        if self.operation:
            value["operation"] = self.operation
        return value


def iter_files(root: Path, scope: Path, changed: set[str] | None) -> Iterable[Path]:
    for path in sorted(scope.rglob("*")):
        if not path.is_file() or any(
            part in IGNORED_DIRS for part in path.relative_to(root).parts
        ):
            continue
        relative = rel(path, root)
        if changed is not None and relative not in changed:
            continue
        yield path


def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > 2_000_000:
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def has_intentional_duplication_marker(segment: str) -> bool:
    return bool(re.search(r"(?m)^\s*#\s*cleanup:\s*intentional-duplication\b", segment))


def git_changed(root: Path) -> set[str]:
    commands = (
        ["git", "diff", "--name-only", "HEAD", "--"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    names: set[str] = set()
    for command in commands:
        result = subprocess.run(
            command, cwd=root, text=True, capture_output=True, check=False
        )
        if result.returncode == 0:
            names.update(line for line in result.stdout.splitlines() if line)
    return names


def is_test_path(path: str) -> bool:
    return bool(set(Path(path).parts) & TEST_PARTS) or Path(path).name.startswith(
        "test_"
    )


def collect_metrics(root: Path, files: list[Path]) -> dict[str, Any]:
    source_files = production_loc = test_loc = total_loc = 0
    modules: set[str] = set()
    for path in files:
        if path.suffix not in SOURCE_SUFFIXES:
            continue
        text = read_text(path)
        if text is None:
            continue
        count = sum(1 for line in text.splitlines() if line.strip())
        source_files += 1
        total_loc += count
        relative = rel(path, root)
        if is_test_path(relative):
            test_loc += count
        else:
            production_loc += count
        modules.add(relative.split("/", 1)[0])
    direct_dependencies = 0
    package = root / "package.json"
    if package.exists():
        try:
            doc = json.loads(package.read_text())
            direct_dependencies = sum(
                len(doc.get(key, {}))
                for key in ("dependencies", "devDependencies", "optionalDependencies")
            )
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    tests = sum(
        1
        for path in files
        if is_test_path(rel(path, root)) and path.suffix in SOURCE_SUFFIXES
    )
    return {
        "source_files": source_files,
        "total_relevant_loc": total_loc,
        "production_loc": production_loc,
        "test_loc": test_loc,
        "direct_dependency_count": direct_dependencies,
        "module_or_package_count": len(modules),
        "test_file_count": tests,
    }


def python_findings(root: Path, files: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    parsed: dict[str, tuple[ast.Module, str]] = {}
    all_text = "\n".join(
        read_text(path) or "" for path in files if path.suffix in TEXT_SUFFIXES
    )
    pyprojects = "\n".join(
        read_text(root / name) or ""
        for name in ("pyproject.toml", "setup.cfg", "setup.py")
    )

    for path in files:
        if path.suffix != ".py":
            continue
        text = read_text(path)
        if text is None:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        relative = rel(path, root)
        parsed[relative] = (tree, text)

    for relative, (tree, text) in parsed.items():
        lines = text.splitlines(keepends=True)
        names = Counter(
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        )
        string_literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        exported: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets
            ):
                if isinstance(node.value, (ast.List, ast.Tuple)):
                    exported.update(
                        e.value
                        for e in node.value.elts
                        if isinstance(e, ast.Constant) and isinstance(e.value, str)
                    )
        functions = [
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        tests = [p for p in parsed if is_test_path(p)]

        normalized: dict[str, list[ast.FunctionDef | ast.AsyncFunctionDef]] = (
            defaultdict(list)
        )
        for node in functions:
            segment = ast.get_source_segment(text, node) or ""
            marker = has_intentional_duplication_marker(segment)
            body_dump = ast.dump(
                ast.Module(body=node.body, type_ignores=[]), include_attributes=False
            )
            normalized[body_dump].append(node)

            external_mentions = len(
                re.findall(rf"\b{re.escape(node.name)}\b", all_text)
            )
            dynamic = (
                node.name in string_literals
                or node.name in exported
                or node.decorator_list
                or re.search(rf"(?m)^\s*{re.escape(node.name)}\s*=", pyprojects)
            )
            private = node.name.startswith("_") and not node.name.startswith("__")
            if names[node.name] == 0 and external_mentions == 1:
                start = node.lineno
                end = node.end_lineno or node.lineno
                operation = {
                    "type": "remove-lines",
                    "start_line": start,
                    "end_line": end,
                    "content_sha256": sha256_text("".join(lines[start - 1 : end])),
                }
                if private and not dynamic and not is_test_path(relative):
                    findings.append(
                        Finding(
                            "dead-code",
                            "PROVEN",
                            relative,
                            node.name,
                            f"Private top-level function {node.name} has no static, textual, export, decorator, or entry-point reference.",
                            [
                                f"definition:{relative}:{start}",
                                "load_references:0",
                                "repository_mentions:1",
                                "dynamic_surfaces:none",
                            ],
                            "low; deletion still requires an explicit approved plan and verification gates",
                            "remove",
                            related_tests=tests,
                            operation=operation,
                        )
                    )
                else:
                    reasons = []
                    if not private:
                        reasons.append("public symbol")
                    if dynamic:
                        reasons.append("dynamic/export/decorator surface")
                    if is_test_path(relative):
                        reasons.append("test discovery convention")
                    findings.append(
                        Finding(
                            "dead-code",
                            "UNKNOWN",
                            relative,
                            node.name,
                            f"No direct caller was found for {node.name}, but deletion is not proven.",
                            [
                                f"definition:{relative}:{start}",
                                "guard:"
                                + ", ".join(
                                    reasons or ["insufficient cross-language evidence"]
                                ),
                            ],
                            "high; static analysis may miss framework, reflection, plugin, CLI, FFI, macro, or serialization entry points",
                            "preserve pending maintainer evidence",
                            public_api_impact="possible",
                        )
                    )

            if len(node.body) == 1 and isinstance(node.body[0], (ast.Return, ast.Expr)):
                value = node.body[0].value
                if isinstance(value, ast.Call) and isinstance(
                    value.func, (ast.Name, ast.Attribute)
                ):
                    findings.append(
                        Finding(
                            "unnecessary-abstraction",
                            "LIKELY",
                            relative,
                            node.name,
                            f"{node.name} is a one-statement forwarding wrapper.",
                            [
                                f"definition:{relative}:{node.lineno}",
                                "body_shape:single forwarding call",
                            ],
                            "medium; wrapper may encode naming, API stability, mocking, policy, or isolation",
                            "review boundary before inlining",
                            public_api_impact="possible"
                            if not private
                            else "none identified",
                        )
                    )

            if marker:
                findings.append(
                    Finding(
                        "duplication",
                        "INTENTIONAL",
                        relative,
                        node.name,
                        "Duplication is explicitly marked intentional.",
                        [
                            f"definition:{relative}:{node.lineno}",
                            "marker:cleanup: intentional-duplication",
                        ],
                        "none while rationale remains valid",
                        "preserve",
                    )
                )

        for body_dump, group in normalized.items():
            if len(group) < 2 or not body_dump:
                continue
            intentional = [
                node
                for node in group
                if has_intentional_duplication_marker(
                    ast.get_source_segment(text, node) or ""
                )
            ]
            if intentional:
                continue
            names_list = [node.name for node in group]
            private = all(
                name.startswith("_") and not name.startswith("__")
                for name in names_list
            )
            evidence = [
                f"definitions:{','.join(f'{relative}:{n.lineno}' for n in group)}",
                "normalized_ast_bodies:identical",
            ]
            operation = None
            confidence = "LIKELY"
            action = "consolidate after intent review"
            if private and len(group) == 2:
                keeper, duplicate = group
                operation = {
                    "type": "consolidate-python-functions",
                    "keeper": keeper.name,
                    "duplicate": duplicate.name,
                    "start_line": duplicate.lineno,
                    "end_line": duplicate.end_lineno or duplicate.lineno,
                    "content_sha256": sha256_text(
                        "".join(
                            lines[
                                duplicate.lineno - 1 : (
                                    duplicate.end_lineno or duplicate.lineno
                                )
                            ]
                        )
                    ),
                }
                confidence = "PROVEN"
                action = f"redirect local references to {keeper.name} and remove {duplicate.name}"
            findings.append(
                Finding(
                    "duplication",
                    confidence,
                    relative,
                    ",".join(names_list),
                    f"Top-level functions {', '.join(names_list)} have identical normalized implementations.",
                    evidence,
                    "low"
                    if confidence == "PROVEN"
                    else "medium; identical code can still represent intentionally separate concepts",
                    action,
                    related_tests=tests,
                    operation=operation,
                )
            )

        # Imports unused inside this module are candidates, not auto-applied: imports can register plugins.
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    bound = alias.asname or alias.name.split(".")[0]
                    if names[bound] == 0:
                        findings.append(
                            Finding(
                                "dead-code",
                                "LIKELY",
                                relative,
                                bound,
                                f"Import {bound} has no AST load reference.",
                                [
                                    f"import:{relative}:{node.lineno}",
                                    "ast_load_references:0",
                                ],
                                "medium; import side effects may be intentional",
                                "review and remove if side-effect free",
                            )
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module == "__future__":
                    continue
                for alias in node.names:
                    bound = alias.asname or alias.name
                    if bound != "*" and names[bound] == 0:
                        findings.append(
                            Finding(
                                "dead-code",
                                "LIKELY",
                                relative,
                                bound,
                                f"Imported name {bound} has no AST load reference.",
                                [
                                    f"import:{relative}:{node.lineno}",
                                    "ast_load_references:0",
                                ],
                                "medium; re-export or import side effects may be intentional",
                                "review and remove if not a package export",
                            )
                        )
    return findings


def dependency_findings(root: Path, files: list[Path]) -> list[Finding]:
    package = root / "package.json"
    if not package.exists():
        return []
    try:
        doc = json.loads(package.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    searchable = []
    for path in files:
        if path == package or path.suffix not in TEXT_SUFFIXES:
            continue
        text = read_text(path)
        if text is not None:
            searchable.append(text)
    corpus = "\n".join(searchable)
    results: list[Finding] = []
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        deps = doc.get(section, {})
        if not isinstance(deps, dict):
            continue
        for name in sorted(deps):
            patterns = [
                rf"(?:from|require\s*\()\s*['\"]{re.escape(name)}(?:/[^'\"]*)?['\"]",
                rf"\b{re.escape(name)}\b",
            ]
            if any(re.search(pattern, corpus) for pattern in patterns):
                continue
            confidence = "LIKELY"  # scripts, loaders and external consumers can escape text search
            results.append(
                Finding(
                    "dependencies",
                    confidence,
                    "package.json",
                    name,
                    f"Direct {section} entry {name} has no repository text reference.",
                    [
                        f"manifest:package.json#{section}.{name}",
                        "repository_text_references:0",
                    ],
                    "medium; dependency may be invoked as a binary, loader, peer, plugin, or packaging hook",
                    "confirm package-manager and build-tool semantics, then remove",
                    operation={
                        "type": "remove-package-dependency",
                        "section": section,
                        "name": name,
                        "expected": deps[name],
                    },
                )
            )
    return results


def heuristic_findings(root: Path, files: list[Path]) -> list[Finding]:
    results: list[Finding] = []
    repository_corpus = "\n".join(
        read_text(path) or "" for path in files if path.suffix in TEXT_SUFFIXES
    )
    for path in files:
        relative = rel(path, root)
        text = read_text(path)
        if text is None:
            continue
        if path.suffix in SOURCE_SUFFIXES:
            comment_lines: set[int] | None = None
            if path.suffix == ".py":
                try:
                    comment_lines = {
                        token.start[0]
                        for token in tokenize.generate_tokens(
                            io.StringIO(text).readline
                        )
                        if token.type == tokenize.COMMENT
                    }
                except tokenize.TokenError:
                    comment_lines = set()
            for number, line in enumerate(text.splitlines(), 1):
                lower = line.lower()
                marker_allowed = comment_lines is None or number in comment_lines
                if marker_allowed and any(
                    token in lower
                    for token in (
                        "deprecated",
                        "compatibility shim",
                        "legacy fallback",
                        "temporary migration",
                    )
                ):
                    results.append(
                        Finding(
                            "legacy-compatibility",
                            "UNKNOWN",
                            relative,
                            f"line:{number}",
                            "Legacy or compatibility path requires support-policy evidence.",
                            [f"marker:{relative}:{number}", line.strip()[:160]],
                            "high; old-looking behavior may be contractually supported",
                            "preserve until owners and support window confirm removal",
                        )
                    )
                if marker_allowed and any(
                    token in lower
                    for token in (
                        "plugin hook",
                        "extension hook",
                        "future use",
                        "just in case",
                    )
                ):
                    results.append(
                        Finding(
                            "over-engineering",
                            "LIKELY",
                            relative,
                            f"line:{number}",
                            "Potential speculative extension surface detected.",
                            [f"marker:{relative}:{number}", line.strip()[:160]],
                            "medium; extension may have external consumers",
                            "verify current consumers and simplify only if unused",
                        )
                    )
                if re.search(r"os\.environ(?:\.get)?\([\"']([A-Z][A-Z0-9_]*)", line):
                    name = re.search(
                        r"os\.environ(?:\.get)?\([\"']([A-Z][A-Z0-9_]*)", line
                    ).group(1)  # type: ignore[union-attr]
                    if (
                        len(re.findall(rf"\b{re.escape(name)}\b", repository_corpus))
                        == 1
                    ):
                        results.append(
                            Finding(
                                "configuration",
                                "LIKELY",
                                relative,
                                name,
                                f"Environment option {name} is referenced at only one repository location.",
                                [
                                    f"reference:{relative}:{number}",
                                    "repository_reference_count:1",
                                ],
                                "medium; deployment configuration may vary externally",
                                "verify documented/deployed consumers before simplifying",
                            )
                        )
        if is_test_path(relative) and path.suffix in SOURCE_SUFFIXES:
            if "TODO" in text and ("skip" in text.lower() or "xfail" in text.lower()):
                results.append(
                    Finding(
                        "tests",
                        "LIKELY",
                        relative,
                        "stale-skip",
                        "Test file contains TODO plus skip/xfail markers.",
                        [f"file:{relative}"],
                        "medium; skipped coverage can represent a known contract",
                        "review whether fixture or behavior was superseded",
                    )
                )
        if path.suffix == ".md":
            seen_missing: set[str] = set()
            for number, token in enumerate(re.findall(r"`([^`\n]+)`", text), 1):
                if (
                    token.startswith(("http", "--", "$"))
                    or " " in token
                    or token.startswith("/")
                ):
                    continue
                if "/" not in token or token.startswith("kujo."):
                    continue
                clean = token.split(":", 1)[0].rstrip("/.,")
                resolved = (root / clean).exists() or (path.parent / clean).exists()
                if (
                    clean
                    and clean not in seen_missing
                    and not any(ch in clean for ch in "*{}<>")
                    and not resolved
                ):
                    seen_missing.add(clean)
                    results.append(
                        Finding(
                            "documentation",
                            "LIKELY",
                            relative,
                            clean,
                            f"Documentation references path {clean}, which does not exist.",
                            [f"document:{relative}", f"missing_path:{clean}"],
                            "low to medium; example paths can be illustrative",
                            "correct, qualify, or remove stale reference",
                            documentation_impact="direct",
                        )
                    )
    # Architecture findings only when a verified Fence config exists; do not invent boundaries.
    if not (root / "fence.toml").exists():
        results.append(
            Finding(
                "architecture",
                "UNKNOWN",
                ".",
                "boundary-model",
                "No repository-owned Fence boundary model exists, so architecture cleanup is not inferred.",
                ["fence.toml:absent"],
                "high; guessed layering rules create false positives",
                "preserve structure or add a reviewed Fence contract first",
            )
        )
    return results


def detect_tool_integrations(
    root: Path, evidence_dir: Path | None = None
) -> list[dict[str, Any]]:
    repos = Path(os.environ.get("KUJO_REPOS", str(root.parent))).resolve()
    kujo = os.environ.get("KUJO_BIN") or str(
        repos / "kujo" / "target" / "release" / "kujo"
    )
    integrations = []
    specs = {
        "scout": [
            kujo,
            "run",
            str(repos / "scout" / "scout.kujo"),
            "--",
            str(root),
            "-o",
            str((evidence_dir or root / ".cleanup-runs") / "scout"),
        ],
        "fence": [
            kujo,
            "run",
            str(repos / "fence" / "fence.kujo"),
            "--",
            "check",
            "--format",
            "json",
        ],
        "concord": [
            kujo,
            "run",
            str(repos / "concord" / "concord.kujo"),
            "--",
            "scan",
            "--dir",
            str(root),
            "--format",
            "json",
        ],
        "kennel": [
            kujo,
            "run",
            str(repos / "kennel" / "kennel.kujo"),
            "--interpreter",
            "--",
            "validate",
            "--project-dir",
            str(root),
        ],
        "changebucket": [
            shutil_which("changebucket")
            or str(repos / "changebucket" / "bin" / "changebucket"),
            "--repo",
            str(root),
            "--json",
        ],
        "patchbrief": [
            kujo,
            "run",
            str(repos / "patchbrief" / "patchbrief.kujo"),
            "--",
            "summarize",
            "--format",
            "json",
            "--pretty",
        ],
        "shipcheck": [
            kujo,
            "run",
            str(repos / "shipcheck" / "shipcheck.kujo"),
            "scan",
            "--dir",
            str(root),
            "--format",
            "json",
        ],
    }
    applicability = {
        "fence": (root / "fence.toml").exists(),
        "kennel": any((root / name).exists() for name in ("kennel.toml", "kujo.toml")),
        "patchbrief": (root / ".git").exists(),
        "changebucket": (root / ".git").exists(),
    }
    for name, command in specs.items():
        tool_repo = repos / name
        available = (
            tool_repo.exists() and Path(kujo).exists()
            if name != "changebucket"
            else Path(command[0]).is_file()
        )
        integrations.append(
            {
                "tool": name,
                "available": available,
                "applicable": applicability.get(name, True),
                "command": shlex.join(command),
                "role": integration_role(name),
            }
        )
    integrations.extend(
        [
            {
                "tool": "casefile",
                "available": (repos / "casefile").exists(),
                "applicable": "on-verification-failure",
                "command": None,
                "role": "capture failing-command evidence; no automatic capture without an actual failure",
            },
            {
                "tool": "runledger",
                "available": (repos / "runledger").exists(),
                "applicable": "host-adapter",
                "command": None,
                "role": "record run usage/cost metadata when the host owns a RunLedger task",
            },
            {
                "tool": "dispatch",
                "available": (repos / "dispatch").exists(),
                "applicable": False,
                "command": None,
                "role": "its cleanup command manages Dispatch run retention, not repository source cleanup",
            },
        ]
    )
    return integrations


def execute_integrations(
    integrations: list[dict[str, Any]], root: Path, evidence_dir: Path
) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    for item in integrations:
        if (
            item["available"] is not True
            or item["applicable"] is not True
            or not item.get("command")
        ):
            item["execution"] = {
                "status": "skipped",
                "reason": "unavailable or not applicable",
            }
            continue
        result = run_command(item["command"], root, timeout_seconds=20)
        (evidence_dir / f"{item['tool']}.log").write_text(result.pop("output_tail"))
        item["execution"] = {
            "status": "passed" if result["passed"] else "failed",
            **result,
        }


def shutil_which(name: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def integration_role(name: str) -> str:
    return {
        "scout": "repository inventory and language/entry-point context",
        "fence": "repository-owned architecture boundary check",
        "concord": "documentation, CLI, manifest, and spec drift",
        "kennel": "Kujo package manifest validation",
        "changebucket": "diff footprint and blast-radius evidence",
        "patchbrief": "diff risk and reviewer handoff",
        "shipcheck": "release-readiness inspection",
    }[name]


def run_command(
    command: str, cwd: Path, timeout_seconds: int | None = None
) -> dict[str, Any]:
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True,
        executable="/bin/bash",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        exit_code = process.returncode
        output = stdout + stderr
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
        output = stdout + stderr + f"\nTIMEOUT after {timeout_seconds} seconds\n"
        exit_code = 124
    return {
        "command": command,
        "exit_code": exit_code,
        "duration_ms": round((time.monotonic() - started) * 1000),
        "output_sha256": sha256_text(output),
        "output_tail": output[-2000:],
        "passed": exit_code == 0,
    }


def classify_verification(
    baseline: list[dict[str, Any]], final: list[dict[str, Any]]
) -> dict[str, Any]:
    regressions = []
    preexisting = []
    for before, after in zip(baseline, final):
        if not before["passed"]:
            preexisting.append(
                {
                    "command": before["command"],
                    "baseline_exit_code": before["exit_code"],
                    "final_exit_code": after["exit_code"],
                }
            )
        if before["passed"] and not after["passed"]:
            regressions.append(
                {
                    "command": before["command"],
                    "baseline_exit_code": before["exit_code"],
                    "final_exit_code": after["exit_code"],
                }
            )
    return {
        "passed": not regressions,
        "pre_existing_failures": preexisting,
        "cleanup_regressions": regressions,
    }


def analyze(
    root: Path,
    scope: Path,
    changed: set[str] | None,
    categories: set[str],
    minimum: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[Path]]:
    files = list(iter_files(root, scope, changed))
    candidates = (
        python_findings(root, files)
        + dependency_findings(root, files)
        + heuristic_findings(root, files)
    )
    values = [
        f.as_dict()
        for f in candidates
        if f.category in categories
        and CONFIDENCE_ORDER[f.confidence] >= CONFIDENCE_ORDER[minimum]
    ]
    values.sort(
        key=lambda item: (item["category"], item["path"], item["symbol"], item["id"])
    )
    return values, collect_metrics(root, files), files


def remove_lines(text: str, start: int, end: int, expected_hash: str) -> str:
    lines = text.splitlines(keepends=True)
    selected = "".join(lines[start - 1 : end])
    if sha256_text(selected) != expected_hash:
        raise ValueError("candidate content changed after analysis")
    del lines[start - 1 : end]
    while (
        start - 1 < len(lines) - 1
        and start - 1 > 0
        and not lines[start - 2].strip()
        and not lines[start - 1].strip()
    ):
        del lines[start - 1]
    return "".join(lines)


def apply_findings(
    root: Path, approved: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[Path, str]]:
    results: list[dict[str, Any]] = []
    originals: dict[Path, str] = {}
    # Descending source locations keep line operations stable within a file.
    approved = sorted(
        approved,
        key=lambda f: (f["path"], f.get("operation", {}).get("start_line", 0)),
        reverse=True,
    )
    for finding in approved:
        if finding.get("confidence") != "PROVEN":
            raise ValueError(
                f"refusing to auto-apply non-PROVEN finding {finding.get('id')}"
            )
        operation = finding.get("operation")
        if not operation:
            raise ValueError(f"finding {finding.get('id')} has no supported operation")
        path = root / finding["path"]
        if path not in originals:
            originals[path] = path.read_text()
        text = path.read_text()
        if operation["type"] == "remove-lines":
            updated = remove_lines(
                text,
                operation["start_line"],
                operation["end_line"],
                operation["content_sha256"],
            )
        elif operation["type"] == "consolidate-python-functions":
            duplicate = operation["duplicate"]
            keeper = operation["keeper"]
            updated = remove_lines(
                text,
                operation["start_line"],
                operation["end_line"],
                operation["content_sha256"],
            )
            tokens = []
            for token in tokenize.generate_tokens(io.StringIO(updated).readline):
                if token.type == tokenize.NAME and token.string == duplicate:
                    token = tokenize.TokenInfo(
                        token.type, keeper, token.start, token.end, token.line
                    )
                tokens.append(token)
            updated = tokenize.untokenize(tokens)
        elif operation["type"] == "remove-package-dependency":
            doc = json.loads(text)
            section, name = operation["section"], operation["name"]
            if doc.get(section, {}).get(name) != operation["expected"]:
                raise ValueError("dependency declaration changed after analysis")
            del doc[section][name]
            updated = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
        else:
            raise ValueError(f"unsupported operation: {operation['type']}")
        path.write_text(updated)
        results.append(
            {
                "id": finding["id"],
                "path": finding["path"],
                "operation": operation["type"],
                "status": "applied",
            }
        )
    return results, originals


def restore(originals: dict[Path, str]) -> None:
    for path, text in originals.items():
        path.write_text(text)


def markdown_report(report: dict[str, Any]) -> str:
    findings = report["findings"]
    counts = Counter(f["confidence"] for f in findings)
    before = report["metrics"]["before"]
    after = report["metrics"]["after"]
    applied = [
        item for item in report.get("applied", []) if item.get("status") == "applied"
    ]
    lines = [
        "# Codebase Cleanup Report",
        "",
        "## Summary",
        "",
        f"- opportunities discovered: {len(findings)}",
        f"- opportunities completed: {len(applied)}",
        f"- opportunities intentionally preserved: {counts['INTENTIONAL']}",
        f"- remaining candidates: {sum(1 for f in findings if f['confidence'] in ('LIKELY', 'UNKNOWN'))}",
        f"- source files: {before['source_files']} → {after['source_files']}",
        f"- relevant LOC: {before['total_relevant_loc']} → {after['total_relevant_loc']} ({after['total_relevant_loc'] - before['total_relevant_loc']:+d})",
        f"- direct dependencies: {before['direct_dependency_count']} → {after['direct_dependency_count']}",
        f"- verification: {'PASS' if report['verification']['passed'] else 'FAIL'}",
        "",
        "## Changes",
        "",
    ]
    completed = {item["id"] for item in applied}
    for finding in findings:
        if finding["id"] not in completed:
            continue
        lines.extend(
            [
                f"### {finding['id']} — {finding['summary']}",
                "",
                f"- Category: {finding['category']}",
                f"- Files: `{finding['path']}`",
                f"- Evidence: {'; '.join(finding['evidence'])}",
                f"- Change: {finding['recommended_action']}",
                f"- Behavioral risk: {finding['risk']}",
                "",
            ]
        )
    lines.extend(["## Preserved Complexity", ""])
    preserved = [f for f in findings if f["confidence"] in ("INTENTIONAL", "UNKNOWN")]
    lines.extend(
        [
            f"- **{f['id']}** `{f['path']}` — {f['summary']} {f['recommended_action']}."
            for f in preserved
        ]
        or ["- none"]
    )
    lines.extend(["", "## Verification", ""])
    for phase in ("baseline", "final"):
        lines.append(f"### {phase.title()}")
        lines.append("")
        results = report["verification"].get(phase, [])
        lines.extend(
            [f"- `{r['command']}` — exit {r['exit_code']}" for r in results]
            or ["- no commands configured"]
        )
        lines.append("")
    if report["verification"]["pre_existing_failures"]:
        lines.append(
            "Pre-existing failures were recorded separately and were not attributed to cleanup."
        )
        lines.append("")
    lines.extend(["## Remaining Candidates", ""])
    remaining = [
        f
        for f in findings
        if f["id"] not in completed and f["confidence"] != "INTENTIONAL"
    ]
    lines.extend(
        [
            f"- **{f['confidence']} {f['id']}** `{f['path']}` — {f['summary']}"
            for f in remaining
        ]
        or ["- none"]
    )
    lines.extend(["", "## Tool Integration Disposition", ""])
    for item in report["integrations"]:
        state = "available" if item["available"] else "unavailable"
        execution = item.get("execution", {}).get("status", "not requested")
        lines.append(
            f"- **{item['tool']}** ({state}, applicable: {item['applicable']}, execution: {execution}): {item['role']}"
        )
    return "\n".join(lines) + "\n"


def write_outputs(output: Path, report: dict[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    (output / "REPORT.md").write_text(markdown_report(report))
    plan = {
        "schema": SCHEMA,
        "repository_fingerprint": report["repository_fingerprint"],
        "approved_finding_ids": [],
        "candidates": []
        if report["mode"] == "apply"
        else [
            f
            for f in report["findings"]
            if f["confidence"] == "PROVEN" and f.get("operation")
        ],
    }
    (output / "cleanup-plan.json").write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n"
    )


def repository_fingerprint(root: Path, files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        relative = rel(path, root)
        digest.update(relative.encode())
        text = read_text(path)
        if text is not None:
            digest.update(hashlib.sha256(text.encode()).digest())
    return digest.hexdigest()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evidence-first aggressive codebase cleanup workflow"
    )
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument(
        "--path", type=Path, default=Path("."), help="repository-relative scope"
    )
    parser.add_argument(
        "--changed",
        action="store_true",
        help="analyze only git-changed and untracked files",
    )
    parser.add_argument("--category", action="append", choices=CATEGORIES)
    parser.add_argument(
        "--minimum-confidence", choices=CONFIDENCE_ORDER, default="UNKNOWN"
    )
    parser.add_argument("--verify-cmd", action="append", default=[])
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--apply-plan",
        type=Path,
        help="apply only explicitly approved PROVEN finding IDs",
    )
    parser.add_argument(
        "--run-integrations",
        action="store_true",
        help="run available, applicable, read-only Kujo companion tools",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = args.repo.resolve()
    scope = (root / args.path).resolve()
    if not root.is_dir() or not scope.is_dir() or root not in (scope, *scope.parents):
        print(
            "ERROR: --repo and repository-contained --path must be directories",
            file=sys.stderr,
        )
        return 2
    categories = set(args.category or CATEGORIES)
    changed = git_changed(root) if args.changed else None
    output = (
        args.output.resolve()
        if args.output
        else root / ".cleanup-runs" / time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    )
    integrations = detect_tool_integrations(root, output / "integrations")
    if args.run_integrations:
        execute_integrations(
            [item for item in integrations if item["tool"] == "scout"],
            root,
            output / "integrations",
        )
    baseline = [run_command(command, root) for command in args.verify_cmd]
    findings, before, files = analyze(
        root, scope, changed, categories, args.minimum_confidence
    )
    fingerprint = repository_fingerprint(root, files)
    applied: list[dict[str, Any]] = []
    originals: dict[Path, str] = {}

    if args.apply_plan:
        try:
            plan = json.loads(args.apply_plan.resolve().read_text())
            if (
                plan.get("schema") != SCHEMA
                or plan.get("repository_fingerprint") != fingerprint
            ):
                raise ValueError(
                    "plan schema or repository fingerprint does not match current analysis"
                )
            approved_ids = plan.get("approved_finding_ids")
            if not isinstance(approved_ids, list) or not approved_ids:
                raise ValueError("plan must contain at least one approved_finding_id")
            index = {finding["id"]: finding for finding in findings}
            if any(item not in index for item in approved_ids):
                raise ValueError(
                    "plan approves a finding that is absent from the current analysis"
                )
            applied, originals = apply_findings(
                root, [index[item] for item in approved_ids]
            )
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            restore(originals)
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    final = [run_command(command, root) for command in args.verify_cmd]
    verification = classify_verification(baseline, final)
    verification["baseline"] = baseline
    verification["final"] = final
    if applied and not verification["passed"]:
        restore(originals)
        applied = [
            {**item, "status": "rolled-back-verification-regression"}
            for item in applied
        ]
        final = [run_command(command, root) for command in args.verify_cmd]
        verification = classify_verification(baseline, final) | {
            "baseline": baseline,
            "final": final,
            "rollback_performed": True,
        }

    if args.run_integrations:
        execute_integrations(
            [item for item in integrations if item["tool"] != "scout"],
            root,
            output / "integrations",
        )
        verification["integration_failures"] = [
            {"tool": item["tool"], **item["execution"]}
            for item in integrations
            if item.get("execution", {}).get("status") == "failed"
        ]

    _, after, final_files = analyze(
        root, scope, changed, categories, args.minimum_confidence
    )
    report = {
        "schema": SCHEMA,
        "mode": "apply" if args.apply_plan else "analysis-only",
        "scope": rel(scope, root) if scope != root else ".",
        "categories_investigated": sorted(categories),
        "repository_fingerprint": repository_fingerprint(root, final_files),
        "metrics": {"before": before, "after": after},
        "findings": findings,
        "applied": applied,
        "verification": verification,
        "integrations": integrations,
    }
    write_outputs(output, report)
    print(str(output / "REPORT.md"))
    return 0 if verification["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
