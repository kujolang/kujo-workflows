#!/usr/bin/env python3
"""Validate one JSON instance against one checked-in JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: validate_contract_instance.py SCHEMA INSTANCE", file=sys.stderr)
        return 2
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        print(f"contract validation requires jsonschema: {exc}", file=sys.stderr)
        return 2
    schema_path, instance_path = map(Path, sys.argv[1:3])
    schema = json.loads(schema_path.read_text())
    instance = json.loads(instance_path.read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        for error in errors:
            print(error.message, file=sys.stderr)
        return 1
    print(f"PASS {instance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
