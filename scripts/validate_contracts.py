#!/usr/bin/env python3
"""Validate the versioned workflow contracts and their checked-in examples."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_ROOT = ROOT / "contracts"


def required_paths(schema: dict[str, Any], value: Any, prefix: tuple[str, ...] = ()) -> list[tuple[str, ...]]:
    paths: list[tuple[str, ...]] = []
    if schema.get("type") != "object" or not isinstance(value, dict):
        return paths
    properties = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in value:
            continue
        path = prefix + (name,)
        paths.append(path)
        child_schema = properties.get(name)
        if isinstance(child_schema, dict):
            paths.extend(required_paths(child_schema, value[name], path))
    return paths


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:  # pragma: no cover - environment diagnostic
        print(f"contract validation requires jsonschema: {exc}", file=sys.stderr)
        return 2

    schemas = sorted(CONTRACT_ROOT.glob("*/*.schema.json"))
    examples = sorted((CONTRACT_ROOT / "examples").glob("*.json"))
    if not schemas or not examples:
        print("contract inventory is empty", file=sys.stderr)
        return 1

    by_contract: dict[str, tuple[dict, Draft202012Validator]] = {}
    for path in schemas:
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        contract_property = schema.get("properties", {}).get("contract", {})
        contract = contract_property.get("const") if isinstance(contract_property, dict) else None
        # Some catalog schemas (for example WebOps findings and site profiles)
        # use their own `schema` discriminator and fixture suites. They still
        # receive meta-schema validation here, while contract/example pairing
        # remains scoped to the workflow receipt schemas.
        if not isinstance(contract, str):
            continue
        by_contract[contract] = (schema, Draft202012Validator(schema))

    failures: list[str] = []
    for path in examples:
        instance = json.loads(path.read_text())
        contract = instance.get("contract")
        if contract not in by_contract:
            failures.append(f"{path}: no schema for {contract!r}")
            continue
        _, validator = by_contract[contract]
        errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
        if errors:
            failures.append(f"{path}: " + "; ".join(error.message for error in errors))

    # A required-field negative test protects against accidentally weakening a
    # contract while still allowing additive forward-compatible properties.
    required_negative_count = 0
    for contract, (schema, validator) in by_contract.items():
        example = next((json.loads(path.read_text()) for path in examples if json.loads(path.read_text()).get("contract") == contract), None)
        if example is None:
            failures.append(f"{contract}: no checked-in example")
            continue
        for path in required_paths(schema, example):
            missing = copy.deepcopy(example)
            cursor: Any = missing
            for part in path[:-1]:
                cursor = cursor[part]
            cursor.pop(path[-1], None)
            required_negative_count += 1
            if not list(validator.iter_errors(missing)):
                failures.append(f"{contract}: removing required field {'.'.join(path)!r} did not fail")
        additive = copy.deepcopy(example)
        additive["future_additive_field"] = {"preserved": True}
        if list(validator.iter_errors(additive)):
            failures.append(f"{contract}: additive field was rejected")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print(f"PASS contract schemas={len(schemas)} examples={len(examples)} required-field-negatives={required_negative_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
