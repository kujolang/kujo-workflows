#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: feature-card-start.sh <card-id> [task-file]

Creates .kujo/feature-cards/<card-id>/ with the standard feature card
artifact folders and starter handoff/proof files.
USAGE
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

card_id="${1:-}"
task_file="${2:-}"

if [ -z "$card_id" ]; then
  usage >&2
  exit 2
fi

case "$card_id" in
  *[!A-Za-z0-9._-]*)
    echo "Invalid card id: use only letters, numbers, dot, underscore, or dash." >&2
    exit 2
    ;;
esac

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "feature-card-start must be run inside a git repository." >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
run_dir="$repo_root/.kujo/feature-cards/$card_id"

mkdir -p \
  "$run_dir/task" \
  "$run_dir/spec" \
  "$run_dir/context/scout" \
  "$run_dir/context/scent" \
  "$run_dir/implementation" \
  "$run_dir/eval/results" \
  "$run_dir/lens/inspect" \
  "$run_dir/lens/check" \
  "$run_dir/lens/proof" \
  "$run_dir/casefile" \
  "$run_dir/briefs" \
  "$run_dir/ledger" \
  "$run_dir/handoff" \
  "$run_dir/logs"

if [ -n "$task_file" ]; then
  if [ ! -f "$task_file" ]; then
    echo "Task file not found: $task_file" >&2
    exit 2
  fi
  cp "$task_file" "$run_dir/task/card.md"
elif [ ! -f "$run_dir/task/card.md" ]; then
  cat > "$run_dir/task/card.md" <<EOF
# Feature Card

- ID: $card_id
- Title:
- Owner:
- Reviewer:

## Problem

## Desired Behavior

## Acceptance Criteria

-

## Verification Expectations

-
EOF
fi

if [ ! -f "$run_dir/task/assumptions.md" ]; then
  cat > "$run_dir/task/assumptions.md" <<'EOF'
# Assumptions

- 
EOF
fi

if [ ! -f "$run_dir/eval/proof-plan.md" ]; then
  cat > "$run_dir/eval/proof-plan.md" <<EOF
# Proof Plan

## Card

- ID: $card_id
- Branch: $(git branch --show-current 2>/dev/null || true)

## Acceptance Criteria To Prove

| Criterion | Proof command or artifact | Status |
| --- | --- | --- |
|  |  | Pending |

## Automated Checks

| Command | Expected result | Actual result | Artifact |
| --- | --- | --- | --- |
|  |  |  |  |

## Lens Proof

- Target URL:
- Flow file:
- Walkthrough path:
- Recording path:
EOF
fi

if [ ! -f "$run_dir/implementation/notes.md" ]; then
  cat > "$run_dir/implementation/notes.md" <<'EOF'
# Implementation Notes

## Decisions

- 

## Commands Run

- 

## Follow-Ups

- 
EOF
fi

if [ ! -f "$run_dir/handoff/reviewer-handoff.md" ]; then
  cat > "$run_dir/handoff/reviewer-handoff.md" <<EOF
# Reviewer Handoff

## Summary

- Card: $card_id
- Branch: $(git branch --show-current 2>/dev/null || true)
- Commit:
- Developer:
- Reviewer:

## What Changed

- 

## Verification

| Check | Result | Artifact |
| --- | --- | --- |
|  |  |  |

## Lens Evidence

- Lens check:
- Lens walkthrough:
- Lens recording:

## Risks And Follow-Ups

- 

## Reviewer Focus

- 
EOF
fi

if [ ! -f "$run_dir/README.md" ]; then
  cat > "$run_dir/README.md" <<EOF
# $card_id Feature Card Run

Start here:

- Task: task/card.md
- Proof plan: eval/proof-plan.md
- Implementation notes: implementation/notes.md
- Reviewer handoff: handoff/reviewer-handoff.md
EOF
fi

echo "Feature card run created: $run_dir"
echo "Next: fill spec/task.spec.yml, build context, implement, prove, and complete handoff/reviewer-handoff.md"
