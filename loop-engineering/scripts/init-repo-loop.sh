#!/usr/bin/env bash
set -euo pipefail

STATE_DIR="${LOOP_ENGINEERING_DIR:-.loop-engineering}"

mkdir -p "$STATE_DIR/iterations" "$STATE_DIR/evidence"

if [ ! -f "$STATE_DIR/loop.yml" ]; then
  cat > "$STATE_DIR/loop.yml" <<'EOF'
objective: ""
checklist_file: ""
max_iterations: 8
max_no_progress: 2
max_consecutive_failures: 3

allowed_actions:
  - read_files
  - edit_files
  - run_tests
  - commit_local_changes

blocked_actions:
  - deploy
  - destructive_cleanup
  - production_config_change

eval_gates:
  - id: php_tests
    command: "cd connector-plugin && composer test"
    required: true
    when_files_match:
      - "connector-plugin/**"

  - id: node_install
    command: "pnpm install --frozen-lockfile"
    required: true
    when_files_match:
      - "package.json"
      - "pnpm-lock.yaml"
      - "src/**"

  - id: node_tests
    command: "pnpm test"
    required: true
    when_files_match:
      - "src/**"

  - id: typecheck
    command: "pnpm run typecheck"
    required: true
    when_files_match:
      - "src/**"

  - id: build
    command: "pnpm run build"
    required: true
    when_files_match:
      - "src/**"

  - id: diff_check
    command: "git diff --check"
    required: true

commit:
  enabled: false
  strategy: small_meaningful
  push: false

memory:
  enabled: false
  provider: strata
  project: "Agent Notes"
  mode: consolidate
  retrieval_tests: true
EOF
fi

[ -f "$STATE_DIR/ledger.tsv" ] || printf 'iteration\taction\tverdict\tprogress\tevidence\tjustification\n' > "$STATE_DIR/ledger.tsv"
[ -f "$STATE_DIR/SUMMARY.md" ] || cat > "$STATE_DIR/SUMMARY.md" <<'EOF'
# Loop Engineering Summary

## Verdict

not-run

## Completed

- none

## Verification

- passed: none
- blocked: none
- failed: none

## Commits

- none

## Remaining

- configure objective/checklist_file in loop.yml

## External Blockers

- none

## Next Start

- scripts/run-workflow.sh --config .loop-engineering/loop.yml
EOF
[ -f "$STATE_DIR/blockers.md" ] || printf '# External Blockers\n\nblockers:\n' > "$STATE_DIR/blockers.md"

printf 'Initialized %s\n' "$STATE_DIR"
