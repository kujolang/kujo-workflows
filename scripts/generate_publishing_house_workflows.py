#!/usr/bin/env python3
"""Generate the repository-owned Publishing House lifecycle kit wrappers."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_CAPABILITIES = ["dispatch", "agents-sdk"]

WORKFLOWS = [
    {
        "slug": "governance",
        "name": "Publishing House Governance",
        "description": "Set a bounded house mandate, portfolio decision, operating priorities, and accountable handoffs without replacing human approval.",
        "tools": ["storydesk", "dossier"],
        "next": "publishing-house-daily-desk",
        "boundary": "Governance may commission, defer, revise, or decline work under PROPOSE; it cannot approve or publish artifacts.",
        "roles": [
            ("Publisher", "publisher", ["storydesk", "dossier"], "publishing mandate and portfolio decision", "Editor-in-Chief"),
            ("Editor-in-Chief", "editor-in-chief", ["storydesk", "dossier"], "editorial ambition and quality boundary", "Managing Editor"),
            ("Managing Editor", "managing-editor", ["storydesk"], "operating plan and queue handoff", "Commissioning Editor"),
        ],
    },
    {
        "slug": "adaptation",
        "name": "Publishing House Adaptation",
        "description": "Extend an approved primary artifact into a versioned franchise and format-native derivative plan without changing its claim boundary.",
        "tools": ["storydesk", "dossier", "galleypack", "bluepencil", "assetworks"],
        "next": "publishing-house-format-production",
        "boundary": "Adaptation remains PROPOSE-only; new or strengthened claims return to Dossier and every derivative retains source lineage.",
        "roles": [
            ("Franchise & Adaptation Editor", "franchise-adaptation-editor", ["storydesk", "dossier", "galleypack", "bluepencil"], "adaptation architecture and claim-boundary map", "Creative Director"),
            ("Creative Director", "creative-director", ["storydesk", "galleypack", "assetworks"], "cross-format creative direction", "Standards & Evidence Editor"),
            ("Standards & Evidence Editor", "standards-evidence-editor", ["dossier", "bluepencil", "galleypack"], "adaptation evidence and rights review", "Production Editor"),
            ("Production Editor", "production-editor", ["galleypack", "assetworks", "bluepencil"], "versioned adaptation package", "Format Desk"),
        ],
    },
    {
        "slug": "format-production",
        "name": "Publishing House Format Production",
        "description": "Produce reviewable newsletter, social, case-study, and video/audio packages from approved source lineage.",
        "tools": ["storydesk", "dossier", "galleypack", "bluepencil", "assetworks"],
        "next": "publishing-house-approval-publication",
        "boundary": "Format production creates proposals and packages only; it cannot publish, infer consent, or expand claims beyond approved evidence.",
        "roles": [
            ("Newsletter Editor", "newsletter-editor", ["storydesk", "dossier", "galleypack", "bluepencil"], "newsletter-native package", "Copy Chief"),
            ("Social & Community Editor", "social-community-editor", ["storydesk", "dossier", "galleypack", "bluepencil"], "social and community package", "Copy Chief"),
            ("Case Study Editor", "case-study-editor", ["storydesk", "dossier", "galleypack", "bluepencil"], "consent-bound case-study package", "Standards & Evidence Editor"),
            ("Video & Audio Producer", "video-audio-producer", ["assetworks", "dossier", "galleypack", "bluepencil"], "accessible video and audio production package", "Production Editor"),
            ("Production Editor", "production-editor", ["galleypack", "assetworks", "bluepencil"], "format package manifest", "Editor-in-Chief"),
        ],
    },
]


def binding(role: tuple[str, str, list[str], str, str]) -> dict:
    name, slug, tools, output, next_owner = role
    return {
        "step_id": slug,
        "canonical_role": name,
        "role_slug": slug,
        "canonical_agent": f"kujo-agents/publishing-house/{slug}/AGENT.md",
        "canonical_skill": f"kujo-agents/publishing-house/{slug}/SKILL.md",
        "allowed_tools": tools,
        "maximum_permission": "PROPOSE",
        "required_inputs": ["workflow request", "record references"],
        "expected_output": output,
        "handoff_destination": next_owner,
        "stop_condition": f"{output} is versioned, blocked, or handed off",
    }


def config(item: dict) -> dict:
    steps = []
    prior = "input"
    prior_id = None
    for index, role in enumerate(item["roles"], start=1):
        role_id = f"role_{index}_{role[1]}"
        steps.append({
            "id": role_id,
            "name": role[0],
            "type": "agent",
            "agent_id": "planner" if index == 1 else "verification",
            "input_from": [prior],
            "output_key": f"role_{index}_output",
            "depends_on": [] if prior_id is None else [prior_id],
            "retry_policy": {"max_attempts": 2, "base_delay_ms": 0, "max_delay_ms": 0, "strategy": "none", "retry_on_codes": ["transient_error"]},
            "idempotency_key": f"publishing-house-{item['slug']}-role-{index}",
        })
        prior = f"role_{index}_output"
        prior_id = role_id
    steps.append({"id": "final_report", "name": "Workflow Report", "type": "report", "input_from": [prior], "depends_on": [prior_id], "output_key": "final_output"})
    workflow_id = f"publishing-house-{item['slug']}"
    return {
        "id": workflow_id,
        "name": item["name"],
        "description": item["description"],
        "version": "0.1.0",
        "purpose": item["description"],
        "audience": "portable Publishing House operators",
        "default_permission": "PROPOSE",
        "maximum_permission": "PROPOSE",
        "fixture_mode": True,
        "live_mode": True,
        "tools": item["tools"] + SHARED_CAPABILITIES,
        "required_capabilities": ["kujo"] + item["tools"] + SHARED_CAPABILITIES,
        "optional_capabilities": ["runledger", "watchdog"],
        "approval_boundaries": [item["boundary"]],
        "state_and_recovery": "state.json and Dispatch state/trace/report artifacts support interruption and bounded resume.",
        "next_workflow": item["next"],
        "input_schema": {"type": "dict", "required": ["topic", "run_id"], "properties": {"topic": {"type": "string"}, "run_id": {"type": "string"}}},
        "steps": steps,
        "output_schema": {"type": "dict"},
        "default_retry_policy": {"max_attempts": 2, "base_delay_ms": 0, "max_delay_ms": 0, "strategy": "none", "retry_on_codes": ["transient_error"]},
        "approval_config": {"auto_approve": False},
        "bindings": [binding(role) for role in item["roles"]],
        "format_profiles": [],
    }


def request(item: dict) -> dict:
    workflow_id = f"publishing-house-{item['slug']}"
    capabilities = [{"name": name, "available": True, "required": True} for name in ["kujo"] + item["tools"] + SHARED_CAPABILITIES]
    capabilities += [{"name": "runledger", "available": False, "required": False}, {"name": "watchdog", "available": False, "required": False}]
    return {
        "contract": "publishing-house.workflow-run-request/v1",
        "schema_name": "publishing-house.workflow-run-request",
        "schema_version": "1.0.0",
        "workflow_id": workflow_id,
        "workflow_version": "0.1.0",
        "run_id": f"run-fixture-{item['slug']}",
        "correlation_id": "correlation-publishing-house-fixture",
        "parent_run_id": None,
        "child_run_ids": [],
        "created_at": "2026-08-14T12:00:00Z",
        "actor": "fixture-operator",
        "permission_mode": "PROPOSE",
        "mode": "fixture",
        "profiles": {"house": "../fixtures/publishing-house/house-profile.fixture.json", "brand": "../fixtures/publishing-house/brand-profile.fixture.json", "audience": "../fixtures/publishing-house/audience-profile.fixture.json"},
        "capabilities": capabilities,
        "input": {"assignment_id": "assignment-fixture-writer", "campaign_id": "campaign-trustworthy-local-publishing", "format_profile": "flagship-feature", "fixture_record_references": []},
        "external_effects_allowed": False,
    }


def write(path: Path, text: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def main() -> None:
    for item in WORKFLOWS:
        workflow_id = f"publishing-house-{item['slug']}"
        directory = ROOT / workflow_id
        write(directory / "workflow.json", json.dumps(config(item), indent=2) + "\n")
        write(directory / "workflow.kujo", f'from lib.publishing_house.runtime import run_workflow\nrun_workflow("{workflow_id}")\n')
        write(directory / "bin/run", '''#!/usr/bin/env bash
set -euo pipefail
WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$WORKFLOW_DIR/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$ROOT/.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
export KUJO_MODULE_PATH="$ROOT${KUJO_MODULE_PATH:+:$KUJO_MODULE_PATH}"
cd "$WORKFLOW_DIR"
exec "$KUJO_BIN" run workflow.kujo -- "$@"
''', True)
        write(directory / "scripts/test.sh", f'''#!/usr/bin/env bash
set -euo pipefail
WORKFLOW_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/.." && pwd)"
RUN_ROOT="$(mktemp -d "${{TMPDIR:-/tmp}}/{workflow_id}.XXXXXX")"
trap 'rm -rf "$RUN_ROOT"' EXIT
bash "$WORKFLOW_DIR/bin/run" --request "$WORKFLOW_DIR/fixtures/request.fixture.json" --out "$RUN_ROOT/run" --json
bash "$WORKFLOW_DIR/bin/run" --request "$WORKFLOW_DIR/fixtures/request.fixture.json" --out "$RUN_ROOT/run" --json
''', True)
        value = json.dumps(request(item), indent=2) + "\n"
        write(directory / "fixtures/request.fixture.json", value)
        write(directory / "examples/request.json", value)
        roles = ", ".join(role[0] for role in item["roles"])
        tools = ", ".join(item["tools"] + SHARED_CAPABILITIES)
        write(directory / "README.md", f'''# {item["name"]}

{item["description"]}

## Boundary

{item["boundary"]}

## Run the deterministic fixture

```bash
(cd {workflow_id} && bash bin/run --request fixtures/request.fixture.json --json)
```

Fixture mode is offline, deterministic, credential-free, and cannot target a live destination. Live mode must be explicit and fails closed until compatible operator adapters are configured; it never falls back to fixture behavior.

## Inputs and outputs

The request supplies portable House, Brand, and Audience profiles, permission, capabilities, correlation IDs, and tool record references. Outputs include capability, contract-loaded agent-step, tool, Dispatch, summary, blocker, or completion receipts under the selected run directory.

Primary roles: {roles}. Required tools: {tools}. Default permission: PROPOSE.
''')
        write(directory / "HOWTO.md", f'''# How to run {item["name"]}

1. Read `README.md` and `workflow.json`.
2. Run `bash bin/run --request fixtures/request.fixture.json --json`.
3. Reuse `--out <path>` to inspect idempotent completion; never overwrite unrelated paths.
4. Inspect `capability-receipt.json`, `agent-contracts/`, `agent-receipts/`, `tool-receipts/`, `dispatch/`, `run-summary.json`, and `completion-receipt.json`.
5. Run `bash scripts/test.sh` after changes.
''')


if __name__ == "__main__":
    main()
