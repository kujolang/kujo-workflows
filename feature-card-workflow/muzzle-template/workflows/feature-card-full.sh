#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: feature-card-full.sh <card-id> <task-file> [repo-dir]

Runs the feature card workflow end to end in the target git repository.

Useful environment variables:
  KUJO_REPOS                 Parent folder for sibling Kujo repos.
  KUJO_BIN                   Kujo runtime path.
  CODEX_BIN                  Codex CLI path.
  FEATURE_BRANCH             Branch to create/use. Default: feature/<card-id>.
  FEATURE_SKIP_AGENT=1       Prepare context/proof packet without running Codex.
  FEATURE_IMPLEMENT_COMMAND  Command to run instead of Codex for implementation.
  FEATURE_VERIFY_COMMANDS    Newline-separated shell commands to run after implementation.
  FEATURE_LENS_URL           Local URL for Lens check/proof.
  FEATURE_LENS_FLOW          Existing Lens flow JSON path. If omitted, the agent may create one.
  FEATURE_LENS_PRECHECK=1    Run Lens before implementation too. Default: 1 when a URL is set.
  FEATURE_AUTH_MODE=login    Optional auth mode. Use with FEATURE_LOGIN_URL and credentials.
  FEATURE_LOGIN_URL          Login page URL for authenticated Lens proof.
  FEATURE_LOGIN_USERNAME     Login username. Prefer FEATURE_LOGIN_USERNAME_ENV.
  FEATURE_LOGIN_PASSWORD     Login password. Prefer FEATURE_LOGIN_PASSWORD_ENV.
  FEATURE_LOGIN_USERNAME_ENV Name of env var containing the username.
  FEATURE_LOGIN_PASSWORD_ENV Name of env var containing the password.
  FEATURE_LOGIN_USER_SELECTOR      Username input selector.
  FEATURE_LOGIN_PASSWORD_SELECTOR  Password input selector.
  FEATURE_LOGIN_SUBMIT_SELECTOR    Submit button selector.
  FEATURE_LOGIN_SUCCESS_SELECTOR   Optional selector that proves login worked.
  FEATURE_LOGIN_SUCCESS_TEXT       Optional text that proves login worked.
  FEATURE_COMMIT=1           Commit intended code changes after verification. Default: 0.
  FEATURE_COMMIT_MESSAGE     Commit message. Default: "<card-id>: implement feature card".
  FEATURE_CODEX_MODEL        Optional Codex model.
USAGE
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

card_id="${1:-}"
task_file="${2:-}"
repo_dir="${3:-$PWD}"

if [ -z "$card_id" ] || [ -z "$task_file" ]; then
  usage >&2
  exit 2
fi

case "$card_id" in
  *[!A-Za-z0-9._-]*)
    echo "Invalid card id: use only letters, numbers, dot, underscore, or dash." >&2
    exit 2
    ;;
esac

if [ ! -f "$task_file" ]; then
  echo "Task file not found: $task_file" >&2
  exit 2
fi

cd "$repo_dir"

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "feature-card-full must be run inside a git repository." >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

FEATURE_WORKFLOW_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$FEATURE_WORKFLOW_ROOT/../.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
KUJO="${KUJO:-$KUJO_BIN}"
export KUJO KUJO_BIN

CODEX_BIN="${CODEX_BIN:-$(command -v codex 2>/dev/null || true)}"
if [ -z "$CODEX_BIN" ] && [ -x "/Applications/Codex.app/Contents/Resources/codex" ]; then
  CODEX_BIN="/Applications/Codex.app/Contents/Resources/codex"
fi

run_dir="$repo_root/.kujo/feature-cards/$card_id"
logs_dir="$run_dir/logs"
briefs_dir="$run_dir/briefs"
status_file="$run_dir/status.tsv"
summary_file="$run_dir/summary.md"
task_dest="$run_dir/task/card.md"
spec_file="$run_dir/spec/task.spec.yml"
agent_prompt="$run_dir/implementation/codex-prompt.md"
agent_output="$run_dir/implementation/codex-final.md"
runledger_id_file="$run_dir/ledger/runledger-id.txt"

exclude_entry=".kujo/feature-cards/$card_id/"
if [ -f "$repo_root/.git/info/exclude" ] && ! grep -qxF "$exclude_entry" "$repo_root/.git/info/exclude"; then
  printf "\n%s\n" "$exclude_entry" >> "$repo_root/.git/info/exclude"
fi

mkdir -p \
  "$run_dir/task" \
  "$run_dir/spec" \
  "$run_dir/context/scout" \
  "$run_dir/context/scent" \
  "$run_dir/implementation" \
  "$run_dir/eval/results" \
  "$run_dir/lens/inspect" \
  "$run_dir/lens/check" \
  "$run_dir/lens/pre-fix" \
  "$run_dir/lens/proof" \
  "$run_dir/casefile" \
  "$briefs_dir" \
  "$run_dir/ledger" \
  "$run_dir/handoff" \
  "$logs_dir"

cp "$task_file" "$task_dest"
: > "$status_file"

log_stage() {
  local name="$1"
  local status="$2"
  local code="$3"
  local detail="$4"
  printf "%s\t%s\t%s\t%s\n" "$name" "$status" "$code" "$detail" >> "$status_file"
}

run_stage() {
  local name="$1"
  shift
  local log="$logs_dir/$name.log"
  set +e
  "$@" >"$log" 2>&1
  local code=$?
  set -e
  if [ "$code" -eq 0 ]; then
    log_stage "$name" "pass" "$code" "$log"
  else
    log_stage "$name" "fail" "$code" "$log"
  fi
  return "$code"
}

run_stage_optional() {
  local name="$1"
  shift
  if run_stage "$name" "$@"; then
    return 0
  fi
  return 0
}

run_shell_stage() {
  local name="$1"
  local command="$2"
  local log="$logs_dir/$name.log"
  set +e
  bash -lc "$command" >"$log" 2>&1
  local code=$?
  set -e
  if [ "$code" -eq 0 ]; then
    log_stage "$name" "pass" "$code" "$log"
  else
    log_stage "$name" "fail" "$code" "$log"
  fi
  return "$code"
}

run_shell_stage_optional() {
  local name="$1"
  local command="$2"
  if run_shell_stage "$name" "$command"; then
    return 0
  fi
  return 0
}

first_heading() {
  sed -n 's/^# \{1,\}//p' "$task_dest" | sed -n '1p'
}

task_title="$(first_heading)"
if [ -z "$task_title" ]; then
  task_title="$card_id feature card"
fi

branch="${FEATURE_BRANCH:-feature/$card_id}"
current_branch="$(git branch --show-current 2>/dev/null || true)"
if [ "$current_branch" != "$branch" ]; then
  if git rev-parse --verify "$branch" >/dev/null 2>&1; then
    run_stage_optional "git-switch-branch" git switch "$branch"
  else
    run_stage_optional "git-branch" git switch -c "$branch"
  fi
else
  log_stage "git-branch" "pass" "0" "Already on $branch"
fi

git status --short > "$run_dir/task/git-status-before.txt"
git rev-parse HEAD > "$run_dir/task/start-commit.txt"

if [ ! -f "$spec_file" ]; then
  cat > "$spec_file" <<EOF
name: "$card_id"
goal: "$task_title"
version: "1.0.0"
background: "Imported from task card at $task_dest."
scope: "Implement the scoped feature described in the task card."
non_goals:
  - "Do not perform unrelated refactors."
  - "Do not change dependencies unless required by the card."
acceptance_criteria:
$(awk '
  BEGIN { in_ac=0; found=0 }
  /^## Acceptance Criteria/ { in_ac=1; next }
  /^## / && in_ac { in_ac=0 }
  in_ac && /^[[:space:]]*[-*][[:space:]]+/ {
    sub(/^[[:space:]]*[-*][[:space:]]+/, "", $0);
    gsub(/"/, "\\\"", $0);
    print "  - \"" $0 "\"";
    found=1;
  }
  END {
    if (!found) print "  - \"The behavior described in the card is implemented and verified.\""
  }
' "$task_dest")
risks:
  - "Cache or JavaScript changes may affect existing frontend behavior."
  - "Selectors or local environment details may differ from the card description."
dependencies:
  - "Target repository dependencies are installed."
  - "A local site URL is available for Lens when browser proof is required."
review_expectations:
  - "Review implementation diff and generated PatchBrief."
  - "Review Lens walkthrough for browser-visible behavior."
  - "Review test and ShipCheck outputs before moving the card to QA."
human_approval_points:
  - "Before merging or deploying the branch."
priority: "medium"
tags:
  - "feature-card"
  - "$card_id"
EOF
fi

if [ ! -x "$KUJO_BIN" ]; then
  log_stage "spec" "skip" "0" "Kujo runtime not found at $KUJO_BIN"
elif command -v spec >/dev/null 2>&1; then
  run_stage_optional "spec-validate" spec validate "$spec_file"
  run_stage_optional "spec-render" spec render "$spec_file" --output "$run_dir/spec/task.spec.md"
  run_stage_optional "spec-agent-context" spec export-agent-context "$spec_file" --output "$run_dir/spec/agent-context.md"
elif [ -x "$KUJO_REPOS/spec/scripts/spec" ]; then
  run_stage_optional "spec-validate" "$KUJO_REPOS/spec/scripts/spec" validate "$spec_file"
  run_stage_optional "spec-render" "$KUJO_REPOS/spec/scripts/spec" render "$spec_file" --output "$run_dir/spec/task.spec.md"
  run_stage_optional "spec-agent-context" "$KUJO_REPOS/spec/scripts/spec" export-agent-context "$spec_file" --output "$run_dir/spec/agent-context.md"
else
  log_stage "spec" "skip" "0" "spec CLI not found"
fi

if [ -x "$KUJO_BIN" ]; then
  run_stage_optional "scout" "$KUJO_BIN" run "$KUJO_REPOS/scout/scout.kujo" -- . --quick -o "$run_dir/context/scout"
  run_stage_optional "scent" "$KUJO_BIN" run "$KUJO_REPOS/scent/scent.kujo" pack --task "$(sed -n '1,80p' "$task_dest")" --out "$run_dir/context/scent" --format both
else
  log_stage "kujo-runtime" "skip" "0" "Kujo runtime not found at $KUJO_BIN"
fi

ledger_id=""
if [ -x "$KUJO_REPOS/runledger/bin/runledger" ] && [ -x "$KUJO_BIN" ]; then
  set +e
  KUJO="$KUJO_BIN" "$KUJO_REPOS/runledger/bin/runledger" start \
    --provider openai \
    --model "${FEATURE_CODEX_MODEL:-codex}" \
    --task "$card_id $task_title" \
    --prompt "$task_dest" \
    --repo . > "$logs_dir/runledger-start.log" 2>&1
  ledger_code=$?
  set -e
  if [ "$ledger_code" -eq 0 ]; then
    log_stage "runledger-start" "pass" "$ledger_code" "$logs_dir/runledger-start.log"
    ledger_id="$(sed -n 's/^Started run: //p' "$logs_dir/runledger-start.log" | tail -n 1)"
    printf "%s\n" "$ledger_id" > "$runledger_id_file"
  else
    log_stage "runledger-start" "fail" "$ledger_code" "$logs_dir/runledger-start.log"
  fi
else
  log_stage "runledger-start" "skip" "0" "RunLedger not available"
fi

lens_bin="$KUJO_REPOS/lens/lens"
lens_url="${FEATURE_LENS_URL:-}"
lens_flow="${FEATURE_LENS_FLOW:-$run_dir/lens/feature.flow.json}"
lens_precheck="${FEATURE_LENS_PRECHECK:-}"
auth_mode="${FEATURE_AUTH_MODE:-}"
login_url="${FEATURE_LOGIN_URL:-}"
login_username="${FEATURE_LOGIN_USERNAME:-}"
login_password="${FEATURE_LOGIN_PASSWORD:-}"

if [ -n "${FEATURE_LOGIN_USERNAME_ENV:-}" ]; then
  login_username="${!FEATURE_LOGIN_USERNAME_ENV-}"
fi

if [ -n "${FEATURE_LOGIN_PASSWORD_ENV:-}" ]; then
  login_password="${!FEATURE_LOGIN_PASSWORD_ENV-}"
fi

if [ -z "$auth_mode" ] && [ -n "$login_url" ]; then
  auth_mode="login"
fi

if [ -z "$lens_precheck" ] && [ -n "$lens_url" ]; then
  lens_precheck="1"
fi

if [ -n "$lens_url" ] && [ ! -f "$lens_flow" ]; then
  if [ "$auth_mode" = "login" ] && { [ -z "$login_url" ] || [ -z "$login_username" ] || [ -z "$login_password" ]; }; then
    log_stage "lens-auth-config" "fail" "2" "FEATURE_AUTH_MODE=login requires FEATURE_LOGIN_URL plus username/password or *_ENV variables"
  else
    FEATURE_CARD_ID="$card_id" \
    FEATURE_LENS_URL_VALUE="$lens_url" \
    FEATURE_AUTH_MODE_VALUE="$auth_mode" \
    FEATURE_LOGIN_URL_VALUE="$login_url" \
    FEATURE_LOGIN_USERNAME_VALUE="$login_username" \
    FEATURE_LOGIN_PASSWORD_VALUE="$login_password" \
    FEATURE_LOGIN_USER_SELECTOR_VALUE="${FEATURE_LOGIN_USER_SELECTOR:-input[name=\"log\"], input[name=\"username\"], input[name=\"email\"], input[type=\"email\"], #user_login}" \
    FEATURE_LOGIN_PASSWORD_SELECTOR_VALUE="${FEATURE_LOGIN_PASSWORD_SELECTOR:-input[type=\"password\"], input[name=\"pwd\"], #user_pass}" \
    FEATURE_LOGIN_SUBMIT_SELECTOR_VALUE="${FEATURE_LOGIN_SUBMIT_SELECTOR:-button[type=\"submit\"], input[type=\"submit\"], #wp-submit}" \
    FEATURE_LOGIN_SUCCESS_SELECTOR_VALUE="${FEATURE_LOGIN_SUCCESS_SELECTOR:-}" \
    FEATURE_LOGIN_SUCCESS_TEXT_VALUE="${FEATURE_LOGIN_SUCCESS_TEXT:-}" \
    python3 - "$lens_flow" <<'PY'
import json
import os
import sys

out = sys.argv[1]
card_id = os.environ["FEATURE_CARD_ID"]
lens_url = os.environ["FEATURE_LENS_URL_VALUE"]
auth_mode = os.environ.get("FEATURE_AUTH_MODE_VALUE", "")

steps = []
start_url = lens_url
description = "Default flow generated by feature-card-full. The implementation agent may refine this with card-specific selectors and assertions."

if auth_mode == "login":
    login_url = os.environ["FEATURE_LOGIN_URL_VALUE"]
    start_url = login_url
    description = "Authenticated default flow generated by feature-card-full. Login values are typed with secret redaction enabled."
    steps.extend([
        {"visit": login_url},
        {"screenshot": {"name": "login-page"}},
        {"type": {
            "selector": os.environ["FEATURE_LOGIN_USER_SELECTOR_VALUE"],
            "value": os.environ["FEATURE_LOGIN_USERNAME_VALUE"],
        }},
        {"type": {
            "selector": os.environ["FEATURE_LOGIN_PASSWORD_SELECTOR_VALUE"],
            "value": os.environ["FEATURE_LOGIN_PASSWORD_VALUE"],
            "secret": True,
        }},
        {"click": {
            "selector": os.environ["FEATURE_LOGIN_SUBMIT_SELECTOR_VALUE"],
            "safe": True,
        }},
    ])
    success_selector = os.environ.get("FEATURE_LOGIN_SUCCESS_SELECTOR_VALUE", "")
    success_text = os.environ.get("FEATURE_LOGIN_SUCCESS_TEXT_VALUE", "")
    if success_selector:
        steps.append({"wait_for_selector": success_selector})
    elif success_text:
        steps.append({"wait_for_text": success_text})
    else:
        steps.append({"wait": {"ms": 1000}})
    steps.append({"screenshot": {"name": "logged-in"}})

steps.extend([
    {"visit": lens_url},
    {"screenshot": {"name": "target-page-initial"}},
    {"assert_no_console_errors": True},
    {"assert_no_failed_requests": True},
])

flow = {
    "name": f"{card_id} default browser proof",
    "description": description,
    "url": start_url,
    "viewports": ["desktop", "mobile"],
    "timeout_seconds": 30,
    "allow_external": False,
    "allow_destructive": False,
    "steps": steps,
}

with open(out, "w", encoding="utf-8") as fh:
    json.dump(flow, fh, indent=2)
    fh.write("\n")
PY
  fi
fi

if [ -n "$lens_url" ] && [ -x "$lens_bin" ]; then
  run_stage_optional "lens-inspect-pre" "$lens_bin" inspect "$lens_url" --json --out "$run_dir/lens/inspect"
  if [ "$lens_precheck" = "1" ]; then
    run_stage_optional "lens-check-pre" "$lens_bin" check "$lens_url" --viewport mobile --viewport desktop --html --out "$run_dir/lens/pre-fix/check"
    if [ -f "$lens_flow" ]; then
      run_stage_optional "lens-flow-pre" "$lens_bin" flow "$lens_flow" --execute --record --walkthrough --out "$run_dir/lens/pre-fix/flow"
    fi
  fi
elif [ -n "$lens_url" ]; then
  log_stage "lens-pre" "skip" "0" "Lens binary not found at $lens_bin"
else
  log_stage "lens-pre" "skip" "0" "FEATURE_LENS_URL not set"
fi

cat > "$agent_prompt" <<EOF
You are implementing a feature card in an existing repository.

Card ID: $card_id
Repository: $repo_root
Run folder: $run_dir
Task card: $task_dest
Spec: $spec_file

Read the task card, generated spec, Scout/Scent context under $run_dir/context, and the current codebase.

Implement the requested fix in the repository. Keep the change tightly scoped to the card.

For a WordPress plugin or PHP/JS cache-related card, pay special attention to:
- frontend JavaScript event timing, cached markup, scroll/page-jump behavior, and layout stability
- PHP cache keys, invalidation, hooks, transients/options/object-cache use, and backwards compatibility
- avoiding broad dependency or build artifact churn

After implementing:
- add or update focused tests where the repo has a clear test pattern
- create or update $run_dir/eval/proof-plan.md with commands and outcomes
- if FEATURE_LENS_URL is relevant, refine the deterministic Lens flow at $run_dir/lens/feature.flow.json using inspected selectors and assertions that prove the user-visible fix
- if FEATURE_AUTH_MODE=login is configured, preserve the login steps and keep any password type step marked with secret: true
- record implementation decisions in $run_dir/implementation/notes.md

Do not commit unless explicitly asked by the workflow. Leave generated proof artifacts under $run_dir.
EOF

if [ "${FEATURE_SKIP_AGENT:-0}" = "1" ]; then
  log_stage "implementation-agent" "skip" "0" "FEATURE_SKIP_AGENT=1"
elif [ -n "${FEATURE_IMPLEMENT_COMMAND:-}" ]; then
  run_shell_stage_optional "implementation-command" "$FEATURE_IMPLEMENT_COMMAND"
else
  if [ -z "$CODEX_BIN" ] || [ ! -x "$CODEX_BIN" ]; then
    log_stage "implementation-agent" "fail" "127" "Codex CLI not found; set CODEX_BIN or FEATURE_IMPLEMENT_COMMAND"
  else
    codex_args=(exec --cd "$repo_root" --sandbox danger-full-access --ask-for-approval never --output-last-message "$agent_output")
    if [ -n "${FEATURE_CODEX_MODEL:-}" ]; then
      codex_args+=(-m "$FEATURE_CODEX_MODEL")
    fi
    run_stage_optional "implementation-agent" "$CODEX_BIN" "${codex_args[@]}" "$(cat "$agent_prompt")"
  fi
fi

git status --short > "$run_dir/implementation/git-status-after-implementation.txt"
git diff --stat > "$run_dir/implementation/diff-stat.txt" || true
git diff > "$run_dir/implementation/diff.patch" || true

if [ -n "${FEATURE_VERIFY_COMMANDS:-}" ]; then
  i=1
  while IFS= read -r verify_cmd; do
    [ -z "$verify_cmd" ] && continue
    run_shell_stage_optional "verify-$i" "$verify_cmd"
    i=$((i + 1))
  done <<EOF
$FEATURE_VERIFY_COMMANDS
EOF
else
  if [ -f composer.json ]; then
    run_shell_stage_optional "verify-composer-validate" "composer validate --no-check-publish"
    if [ -x vendor/bin/phpunit ]; then
      run_shell_stage_optional "verify-phpunit" "vendor/bin/phpunit"
    fi
  fi
  if [ -f package.json ]; then
    if node -e 'const p=require("./package.json"); process.exit(p.scripts&&p.scripts.test?0:1)' >/dev/null 2>&1; then
      run_shell_stage_optional "verify-npm-test" "npm test -- --watch=false"
    fi
    if node -e 'const p=require("./package.json"); process.exit(p.scripts&&p.scripts.build?0:1)' >/dev/null 2>&1; then
      run_shell_stage_optional "verify-npm-build" "npm run build"
    fi
  fi
fi

if [ -x "$KUJO_BIN" ] && [ -f "$run_dir/eval/task.eval.json" ]; then
  run_stage_optional "eval-run" "$KUJO_BIN" run "$KUJO_REPOS/eval/main.kujo" run "$run_dir/eval/task.eval.json" --out "$run_dir/eval/results"
else
  log_stage "eval-run" "skip" "0" "No $run_dir/eval/task.eval.json found"
fi

if [ -n "$lens_url" ] && [ -x "$lens_bin" ]; then
  run_stage_optional "lens-check-post" "$lens_bin" check "$lens_url" --viewport mobile --viewport desktop --accessibility --html --out "$run_dir/lens/check"
  if [ -f "$lens_flow" ]; then
    run_stage_optional "lens-flow-validate" "$lens_bin" flow "$lens_flow" --validate --json
    run_stage_optional "lens-flow-proof" "$lens_bin" flow "$lens_flow" --execute --record --walkthrough --out "$run_dir/lens/proof"
  else
    log_stage "lens-flow-proof" "skip" "0" "No Lens flow found at $lens_flow"
  fi
fi

if [ -x "$KUJO_BIN" ]; then
  run_shell_stage_optional "patchbrief-summary" "$(printf '%q run %q -- summarize > %q' "$KUJO_BIN" "$KUJO_REPOS/patchbrief/patchbrief.kujo" "$briefs_dir/patchbrief.md")"
  run_shell_stage_optional "patchbrief-tests" "$(printf '%q run %q -- suggest-tests > %q' "$KUJO_BIN" "$KUJO_REPOS/patchbrief/patchbrief.kujo" "$briefs_dir/test-suggestions.md")"
  run_shell_stage_optional "patchbrief-handoff" "$(printf '%q run %q -- handoff > %q' "$KUJO_BIN" "$KUJO_REPOS/patchbrief/patchbrief.kujo" "$briefs_dir/patchbrief-handoff.md")"
  run_shell_stage_optional "shipcheck-scan" "$(printf '%q run %q scan --dir . > %q' "$KUJO_BIN" "$KUJO_REPOS/shipcheck/shipcheck.kujo" "$briefs_dir/shipcheck.md")"
  run_shell_stage_optional "shipcheck-gate" "$(printf '%q run %q gate --dir . --format json > %q' "$KUJO_BIN" "$KUJO_REPOS/shipcheck/shipcheck.kujo" "$briefs_dir/shipcheck-gate.json")"
fi

if [ -x "$KUJO_REPOS/changebucket/bin/changebucket" ] && [ -x "$KUJO_BIN" ]; then
  run_shell_stage_optional "changebucket" "$(printf 'KUJO=%q %q --markdown > %q' "$KUJO_BIN" "$KUJO_REPOS/changebucket/bin/changebucket" "$briefs_dir/changebucket.md")"
  run_shell_stage_optional "changebucket-budget" "$(printf 'KUJO=%q %q check --max-files ${FEATURE_MAX_FILES:-25} --max-churn ${FEATURE_MAX_CHURN:-1200} > %q' "$KUJO_BIN" "$KUJO_REPOS/changebucket/bin/changebucket" "$briefs_dir/changebucket-budget.txt")"
else
  log_stage "changebucket" "skip" "0" "ChangeBucket or Kujo runtime not available"
fi

if [ "${FEATURE_COMMIT:-0}" = "1" ]; then
  commit_message="${FEATURE_COMMIT_MESSAGE:-$card_id: implement feature card}"
  run_shell_stage_optional "git-add-code" "git add -A ':!.kujo/feature-cards/$card_id'"
  run_stage_optional "git-commit" git commit -m "$commit_message"
else
  log_stage "git-commit" "skip" "0" "FEATURE_COMMIT is not 1"
fi

end_commit="$(git rev-parse HEAD 2>/dev/null || true)"
git status --short > "$run_dir/task/git-status-final.txt"

if [ -f "$runledger_id_file" ]; then
  ledger_id="$(cat "$runledger_id_file")"
fi

if [ -n "$ledger_id" ] && [ -x "$KUJO_REPOS/runledger/bin/runledger" ]; then
  KUJO="$KUJO_BIN" "$KUJO_REPOS/runledger/bin/runledger" note "$ledger_id" "Feature card workflow finished. Run folder: $run_dir" >"$logs_dir/runledger-note.log" 2>&1 || true
  if grep -q $'\tfail\t' "$status_file"; then
    ledger_status="partial"
    ledger_verdict="Workflow completed with one or more failed stages; review status.tsv and logs."
  else
    ledger_status="pass"
    ledger_verdict="Workflow completed; implementation, verification, and handoff artifacts are ready for review."
  fi
  KUJO="$KUJO_BIN" "$KUJO_REPOS/runledger/bin/runledger" finish "$ledger_id" --status "$ledger_status" --verdict "$ledger_verdict" --repo . >"$logs_dir/runledger-finish.log" 2>&1 || true
  KUJO="$KUJO_BIN" "$KUJO_REPOS/runledger/bin/runledger" report --task "$card_id $task_title" --output "$run_dir/ledger/runledger-report.md" >"$logs_dir/runledger-report.log" 2>&1 || true
fi

cat > "$run_dir/handoff/reviewer-handoff.md" <<EOF
# Reviewer Handoff

## Summary

- Card: $card_id
- Title: $task_title
- Branch: $(git branch --show-current 2>/dev/null || true)
- Start commit: $(cat "$run_dir/task/start-commit.txt" 2>/dev/null || true)
- End commit: $end_commit
- Run folder: $run_dir

## What Changed

See:

- Implementation notes: $run_dir/implementation/notes.md
- Diff stat: $run_dir/implementation/diff-stat.txt
- PatchBrief: $briefs_dir/patchbrief.md
- ChangeBucket: $briefs_dir/changebucket.md

## Verification

Workflow stage results are in:

- $status_file

Detailed logs are in:

- $logs_dir

## Lens Evidence

- Lens URL: ${lens_url:-not provided}
- Lens check: $run_dir/lens/check
- Lens flow: $lens_flow
- Lens proof: $run_dir/lens/proof
- Walkthrough: $run_dir/lens/proof/walkthrough.html

## Release And Scope Checks

- ShipCheck: $briefs_dir/shipcheck.md
- ShipCheck gate: $briefs_dir/shipcheck-gate.json
- ChangeBucket budget: $briefs_dir/changebucket-budget.txt
- RunLedger: $run_dir/ledger/runledger-report.md

## Reviewer Focus

- Confirm the implementation matches the card acceptance criteria.
- Review the Lens walkthrough for the browser-visible behavior.
- Check failed or skipped rows in status.tsv before approving.
- Confirm generated/local proof artifacts are not accidentally included in the final commit unless team policy requires them.
EOF

cat > "$run_dir/handoff/testing-request.md" <<EOF
Ready for testing.

Card: $card_id
Branch: $(git branch --show-current 2>/dev/null || true)
Commit: $end_commit

Run packet:
$run_dir

Reviewer handoff:
$run_dir/handoff/reviewer-handoff.md

Lens proof:
$run_dir/lens/proof/walkthrough.html

Stage summary:
$status_file
EOF

{
  echo "# Feature Card Workflow Summary"
  echo
  echo "- Card: $card_id"
  echo "- Title: $task_title"
  echo "- Repo: $repo_root"
  echo "- Branch: $(git branch --show-current 2>/dev/null || true)"
  echo "- Run folder: $run_dir"
  echo "- Reviewer handoff: $run_dir/handoff/reviewer-handoff.md"
  echo
  echo "## Stages"
  echo
  echo "| Stage | Status | Exit | Detail |"
  echo "| --- | --- | --- | --- |"
  awk -F '\t' '{ printf "| `%s` | %s | %s | `%s` |\n", $1, $2, $3, $4 }' "$status_file"
} > "$summary_file"

cat "$summary_file"

if grep -q $'\tfail\t' "$status_file"; then
  exit 1
fi
