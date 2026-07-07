#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

usage() {
  cat <<'EOF'
Usage:
  scripts/run-workflow.sh --demo
  scripts/run-workflow.sh --config .loop-engineering/loop.yml
  scripts/run-workflow.sh --checklist docs/checklist.md

No default demo run is performed. Initialize a repo with:
  /path/to/loop-engineering/scripts/init-repo-loop.sh
EOF
}

fail() {
  printf 'ERROR: %s\n\n' "$1" >&2
  usage >&2
  exit 2
}

quote_yaml() {
  printf '%s' "$1" | sed 's/"/\\"/g'
}

trim_yaml_value() {
  sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//; s/^"//; s/"$//; s/^'\''//; s/'\''$//'
}

yaml_scalar() {
  local file="$1" key="$2" default="$3"
  local value
  value="$(awk -v key="$key" '
    $0 ~ "^[[:space:]]*" key ":[[:space:]]*" {
      sub("^[[:space:]]*" key ":[[:space:]]*", "", $0)
      print
      exit
    }
  ' "$file" | trim_yaml_value)"
  printf '%s' "${value:-$default}"
}

yaml_section_scalar() {
  local file="$1" section="$2" key="$3" default="$4"
  local value
  value="$(awk -v section="$section" -v key="$key" '
    $0 ~ "^" section ":" { in_section=1; next }
    in_section && $0 ~ "^[^[:space:]-]" { in_section=0 }
    in_section && $0 ~ "^[[:space:]]+" key ":[[:space:]]*" {
      sub("^[[:space:]]+" key ":[[:space:]]*", "", $0)
      print
      exit
    }
  ' "$file" | trim_yaml_value)"
  printf '%s' "${value:-$default}"
}

ensure_repo_layout() {
  local state_dir="$1"
  mkdir -p "$state_dir/iterations" "$state_dir/evidence"
  [ -f "$state_dir/ledger.tsv" ] || printf 'iteration\taction\tverdict\tprogress\tevidence\tjustification\n' > "$state_dir/ledger.tsv"
  [ -f "$state_dir/blockers.md" ] || printf '# External Blockers\n\nblockers:\n' > "$state_dir/blockers.md"
  [ -f "$state_dir/SUMMARY.md" ] || printf '# Loop Engineering Summary\n\n' > "$state_dir/SUMMARY.md"
}

git_changed_files() {
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git diff --name-only HEAD -- 2>/dev/null || true
  fi
}

glob_to_regex() {
  local glob="$1"
  printf '%s' "$glob" |
    sed -E 's/[.[\()+^$|{}]/\\&/g; s#\*\*#@@DOUBLESTAR@@#g; s#\*#[^/]*#g; s#@@DOUBLESTAR@@#.*#g; s#\?#.#g'
}

files_match_any_pattern() {
  local patterns="$1" changed="$2" pattern regex file
  [ -z "$patterns" ] && return 0
  [ -z "$changed" ] && return 1
  while IFS= read -r pattern; do
    [ -z "$pattern" ] && continue
    regex="^$(glob_to_regex "$pattern")$"
    while IFS= read -r file; do
      [ -z "$file" ] && continue
      if printf '%s\n' "$file" | grep -Eq "$regex"; then
        return 0
      fi
    done <<< "$changed"
  done < <(printf '%s\n' "$patterns" | tr '|' '\n')
  return 1
}

emit_eval_gates() {
  local config="$1"
  awk '
    function clean(s) {
      sub(/^[[:space:]]+/, "", s)
      sub(/[[:space:]]+$/, "", s)
      sub(/^"/, "", s)
      sub(/"$/, "", s)
      sub(/^'\''/, "", s)
      sub(/'\''$/, "", s)
      return s
    }
    function flush() {
      if (id != "") {
        sub(/\|$/, "", patterns)
        printf "%s\t%s\t%s\t%s\n", id, command, required, patterns
      }
      id=""; command=""; required="true"; patterns=""; in_patterns=0
    }
    /^eval_gates:/ { in_gates=1; next }
    in_gates && /^[^[:space:]-]/ { flush(); in_gates=0 }
    !in_gates { next }
    /^  -[[:space:]]*id:/ {
      flush()
      sub(/^  -[[:space:]]*id:[[:space:]]*/, "", $0)
      id=clean($0)
      next
    }
    /^    command:/ {
      sub(/^    command:[[:space:]]*/, "", $0)
      command=clean($0)
      in_patterns=0
      next
    }
    /^    required:/ {
      sub(/^    required:[[:space:]]*/, "", $0)
      required=clean($0)
      in_patterns=0
      next
    }
    /^    when_files_match:/ { in_patterns=1; next }
    in_patterns && /^      -[[:space:]]+/ {
      sub(/^      -[[:space:]]*/, "", $0)
      patterns=patterns clean($0) "|"
      next
    }
    END { flush() }
  ' "$config"
}

classify_blocker_text() {
  local text="$1"
  local lower
  lower="$(printf '%s' "$text" | tr '[:upper:]' '[:lower:]')"
  if printf '%s' "$lower" | grep -Eq 'err_pnpm_tarball_url_mismatch|private registry|eneedauth|e401|401 unauthorized|403 forbidden|npm.*auth|composer.*auth'; then
    printf 'private-registry-auth\tRestore private registry/auth/policy access.'
  elif printf '%s' "$lower" | grep -Eq 'ssh: connect to host .*port .*connection refused|permission denied \(publickey\)|could not read from remote repository|gitlab.*connection refused'; then
    printf 'remote-ssh-unavailable\tRestore SSH/Git remote access.'
  elif printf '%s' "$lower" | grep -Eq 'could not resolve host|temporary failure in name resolution|network is unreachable|enotfound|etimedout'; then
    printf 'network-unavailable\tRestore network/DNS access and retry.'
  elif printf '%s' "$lower" | grep -Eq 'approval required|requires approval|human approval|manual approval'; then
    printf 'human-approval-required\tObtain the required human approval.'
  elif printf '%s' "$lower" | grep -Eq 'release pipeline|protected branch|merge is blocked|ci is required'; then
    printf 'release-pipeline-blocked\tRestore or complete the required release pipeline.'
  else
    printf '\t'
  fi
}

record_blocker() {
  local blockers_file="$1" command="$2" evidence="$3"
  local detected id next_action
  detected="$(classify_blocker_text "$evidence")"
  id="${detected%%	*}"
  next_action="${detected#*	}"
  [ -z "$id" ] && return 1
  {
    printf '  - id: %s\n' "$id"
    printf '    command: "%s"\n' "$(quote_yaml "$command")"
    printf '    evidence: "%s"\n' "$(quote_yaml "$(printf '%s' "$evidence" | head -c 500)")"
    printf '    status: external-blocked\n'
    printf '    next_action: "%s"\n' "$(quote_yaml "$next_action")"
  } >> "$blockers_file"
  return 0
}

classify_checklist_item() {
  local checked="$1" text="$2" lower
  lower="$(printf '%s' "$text" | tr '[:upper:]' '[:lower:]')"
  if [ "$checked" = "x" ]; then
    printf 'already-done'
  elif printf '%s' "$lower" | grep -Eq 'approval|approve|sign[- ]off|permission from|manual decision'; then
    printf 'requires-human-approval'
  elif printf '%s' "$lower" | grep -Eq 'deploy|release|publish|merge to main|merge to default|tag release|ship|ci release|release pipeline'; then
    printf 'needs-release-pipeline'
  elif printf '%s' "$lower" | grep -Eq 'contract first|contract-first|api contract|schema first|spec first|define contract'; then
    printf 'needs-contract-first'
  elif printf '%s' "$lower" | grep -Eq 'private registry|registry auth|credential|token|ssh access|vpn|license|external account|blocked by'; then
    printf 'external-blocked'
  elif printf '%s' "$lower" | grep -Eq 'production config|drop database|destructive|delete production|irreversible|purge'; then
    printf 'policy-blocked'
  elif printf '%s' "$lower" | grep -Eq 'another repo|other repo|upstream|third[- ]party|outside this repo|external service|vendor'; then
    printf 'out-of-repo'
  else
    printf 'local-fixable'
  fi
}

write_checklist_classification() {
  local checklist="$1" state_dir="$2" out="$state_dir/checklist.tsv"
  printf 'line\tstatus\ttext\tevidence\n' > "$out"
  awk '
    /^[[:space:]]*[-*][[:space:]]+\[[ xX]\][[:space:]]+/ {
      checked=$0
      sub(/^[[:space:]]*[-*][[:space:]]+\[/, "", checked)
      checked=substr(checked, 1, 1)
      text=$0
      sub(/^[[:space:]]*[-*][[:space:]]+\[[ xX]\][[:space:]]+/, "", text)
      printf "%s\t%s\t%s\n", NR, checked, text
    }
  ' "$checklist" | while IFS=$'\t' read -r line checked text; do
    status="$(classify_checklist_item "$(printf '%s' "$checked" | tr '[:upper:]' '[:lower:]')" "$text")"
    printf '%s\t%s\t%s\t%s:%s\n' "$line" "$status" "$text" "$checklist" "$line" >> "$out"
  done
}

append_report_list() {
  local title="$1" content="$2"
  printf '## %s\n\n' "$title"
  if [ -n "$content" ]; then
    printf '%s\n\n' "$content"
  else
    printf -- '- none\n\n'
  fi
}

inline_items() {
  local items="$1"
  if [ -z "$items" ]; then
    printf 'none'
    return
  fi
  printf '%s' "$items" | awk '
    /^- / {
      sub(/^- /, "")
      if (out != "") out = out ", "
      out = out $0
    }
    END {
      if (out == "") print "none"
      else print out
    }
  '
}

run_demo() {
  local run_dir="${RUN_DIR:-$WORKFLOW_DIR/.runs/$STAMP}"
  local iter_dir="$run_dir/iterations"
  local ledger="$run_dir/ledger.tsv"
  local summary="$run_dir/SUMMARY.md"
  local max_iterations="${LOOP_MAX_ITERATIONS:-8}"
  local success_at="${LOOP_DEMO_SUCCESS_AT:-2}"
  mkdir -p "$iter_dir"
  printf 'iteration\taction\tverdict\tprogress\tevidence\tjustification\n' > "$ledger"
  local verdict="blocked" stop_reason="budget-exhausted" n progress=0
  for ((n=1; n<=max_iterations; n++)); do
    local step
    step="$(printf '%s/%03d' "$iter_dir" "$n")"
    mkdir -p "$step"
    printf 'demo context refresh\n' > "$step/context.md"
    printf 'demo scoped action\n' > "$step/action.md"
    git diff --no-ext-diff --binary > "$step/diff.patch" 2>/dev/null || true
    if [ "$n" -ge "$success_at" ]; then
      printf 'demo evaluator: pass at iteration %s\n' "$n" > "$step/eval.log"
      printf 'verdict: pass\nprogress: %s\n' "$n" > "$step/verdict.yml"
      printf '%s\tadvance-toward-goal\tpass\t%s\titerations/%03d/eval.log\tdemo success threshold reached\n' "$n" "$n" "$n" >> "$ledger"
      verdict="success"
      stop_reason="success: demo success threshold reached"
      progress="$n"
      break
    fi
    printf 'demo evaluator: fail until iteration %s\n' "$success_at" > "$step/eval.log"
    printf 'verdict: fail\nprogress: %s\n' "$n" > "$step/verdict.yml"
    printf '%s\tadvance-toward-goal\tfail\t%s\titerations/%03d/eval.log\tcontinue demo loop\n' "$n" "$n" "$n" >> "$ledger"
    progress="$n"
  done
  cat > "$summary" <<EOF
# Loop Engineering Summary

## Verdict

$verdict

## Completed

- demo loop executed through progress=$progress

## Verification

- passed: $([ "$verdict" = "success" ] && echo "demo evaluator" || echo "none")
- blocked: $([ "$verdict" = "success" ] && echo "none" || echo "$stop_reason")
- failed: none

## Commits

- none

## Remaining

- none

## External Blockers

- none

## Next Start

- $([ "$verdict" = "success" ] && echo "none" || echo "rerun with --config for real work")
EOF
  printf 'Workflow complete: %s\nVerdict: %s\n' "$run_dir" "$verdict"
}

run_config() {
  local config="$1" checklist_override="${2:-}"
  [ -f "$config" ] || fail "config not found: $config"
  local state_dir
  state_dir="$(cd "$(dirname "$config")" && pwd)"
  ensure_repo_layout "$state_dir"

  local objective checklist max_iterations max_no_progress max_failures
  objective="$(yaml_scalar "$config" objective "")"
  checklist="$(yaml_scalar "$config" checklist_file "")"
  [ -n "$checklist_override" ] && checklist="$checklist_override"
  max_iterations="$(yaml_scalar "$config" max_iterations "8")"
  max_no_progress="$(yaml_scalar "$config" max_no_progress "2")"
  max_failures="$(yaml_scalar "$config" max_consecutive_failures "3")"
  local commit_enabled commit_push memory_enabled memory_provider
  commit_enabled="$(yaml_section_scalar "$config" commit enabled false)"
  commit_push="$(yaml_section_scalar "$config" commit push false)"
  memory_enabled="$(yaml_section_scalar "$config" memory enabled false)"
  memory_provider="$(yaml_section_scalar "$config" memory provider "")"

  local changed_files
  changed_files="$(git_changed_files)"
  if [ -n "$checklist" ]; then
    [ -f "$checklist" ] || fail "checklist file not found: $checklist"
    write_checklist_classification "$checklist" "$state_dir"
  fi

  local iter=1 failures=0 no_progress=0 progress=0 previous_progress=-1 verdict="blocked" stop_reason="" gates_passed="" gates_failed="" gates_blocked="" completed="" remaining="" external_blockers="" commits="" commit_created=0 commit_needs_push=0
  for ((iter=1; iter<=max_iterations; iter++)); do
    local iter_name step action_ok=0 eval_ok=0 gate_count=0 required_failures=0 required_blockers=0 skipped_count=0
    iter_name="$(printf '%03d' "$iter")"
    step="$state_dir/iterations/$iter_name"
    mkdir -p "$step"
    {
      printf '# Context\n\n'
      printf -- '- objective: %s\n' "${objective:-"(unset)"}"
      printf -- '- git_head: %s\n' "$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
      printf -- '- changed_files:\n'
      if [ -n "$changed_files" ]; then
        while IFS= read -r file; do printf '  - %s\n' "$file"; done <<< "$changed_files"
      else
        printf '  - none\n'
      fi
      if [ -f "$state_dir/checklist.tsv" ]; then
        printf -- '- checklist_classification: checklist.tsv\n'
      fi
    } > "$step/context.md"

    {
      printf '# Action\n\n'
      if [ -n "${LOOP_ACT_CMD:-}" ]; then
        printf '$ %s\n\n' "$LOOP_ACT_CMD"
        if bash -lc "$LOOP_ACT_CMD"; then
          printf '\nResult: command completed.\n'
          action_ok=1
        else
          printf '\nResult: command failed.\n'
          action_ok=0
        fi
      else
        printf 'No LOOP_ACT_CMD supplied. This iteration classified context and ran configured gates only.\n'
        action_ok=1
      fi
    } > "$step/action.md" 2>&1

    git diff --no-ext-diff --binary > "$step/diff.patch" 2>/dev/null || true
    changed_files="$(git_changed_files)"
    : > "$step/eval.log"

    while IFS=$'\t' read -r gate_id gate_command gate_required gate_patterns; do
      [ -z "$gate_id" ] && continue
      if ! files_match_any_pattern "$gate_patterns" "$changed_files"; then
        printf 'gate %s: skipped (no changed files matched)\n' "$gate_id" >> "$step/eval.log"
        skipped_count=$((skipped_count + 1))
        continue
      fi
      gate_count=$((gate_count + 1))
      printf '\n## gate: %s\n$ %s\n' "$gate_id" "$gate_command" >> "$step/eval.log"
      local gate_log gate_log_name
      gate_log_name="$(printf '%s' "$gate_id" | tr -c 'A-Za-z0-9_.-' '_')"
      gate_log="$step/gate-$gate_log_name.log"
      if bash -lc "$gate_command" > "$gate_log" 2>&1; then
        cat "$gate_log" >> "$step/eval.log"
        gates_passed="${gates_passed}- $gate_id"$'\n'
        printf 'gate %s: pass\n' "$gate_id" >> "$step/eval.log"
      else
        local gate_evidence
        cat "$gate_log" >> "$step/eval.log"
        gate_evidence="$(cat "$gate_log")"
        if record_blocker "$state_dir/blockers.md" "$gate_command" "$gate_evidence"; then
          gates_blocked="${gates_blocked}- $gate_id"$'\n'
          required_blockers=$((required_blockers + 1))
        else
          gates_failed="${gates_failed}- $gate_id"$'\n'
          [ "$gate_required" = "true" ] && required_failures=$((required_failures + 1))
        fi
      fi
    done < <(emit_eval_gates "$config")

    if [ "$gate_count" -eq 0 ] && [ "$skipped_count" -eq 0 ]; then
      printf 'No eval_gates configured.\n' >> "$step/eval.log"
    fi

    if [ "$required_blockers" -gt 0 ]; then
      eval_ok=2
      verdict="blocked"
      stop_reason="external blocker detected"
    elif [ "$required_failures" -gt 0 ] || [ "$action_ok" -eq 0 ]; then
      eval_ok=1
      verdict="failed"
      failures=$((failures + 1))
      stop_reason="required gate failed"
    else
      eval_ok=0
      verdict="success"
      failures=0
      stop_reason="success: required gates passed"
    fi

    if [ "$eval_ok" -eq 0 ]; then
      progress=$((progress + 1))
    fi
    if [ "$progress" -le "$previous_progress" ]; then
      no_progress=$((no_progress + 1))
    else
      no_progress=0
    fi
    previous_progress="$progress"

    cat > "$step/verdict.yml" <<EOF
iteration: $iter
verdict: $verdict
progress: $progress
required_failures: $required_failures
external_blockers: $required_blockers
stop_reason: "$(quote_yaml "$stop_reason")"
EOF

    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$iter_name" "configured-gates" "$verdict" "$progress" "iterations/$iter_name/eval.log" "$stop_reason" >> "$state_dir/ledger.tsv"

    [ "$eval_ok" -eq 0 ] && break
    if [ "$required_blockers" -gt 0 ]; then
      break
    fi
    if [ "$failures" -ge "$max_failures" ]; then
      verdict="blocked"
      stop_reason="repeated-failure: required gate failed $failures times"
      break
    fi
    if [ "$no_progress" -ge "$max_no_progress" ]; then
      verdict="blocked"
      stop_reason="stall: no measurable progress for $no_progress iterations"
      break
    fi
  done

  if [ "$commit_enabled" = "true" ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if [ -n "$(git status --short)" ]; then
      git add -A
      local msg
      msg="Loop engineering: ${objective:-configured run}"
      if git commit -m "$msg" >/tmp/loop-engineering-commit.log 2>&1; then
        commits="- $msg"
        commit_created=1
        if [ "$commit_push" = "true" ]; then
          commit_needs_push=1
        fi
      else
        gates_failed="${gates_failed}- commit"$'\n'
        verdict="failed"
        stop_reason="commit failed"
      fi
    else
      commits="- none (no changes)"
    fi
  else
    commits="- none"
  fi

  if [ -f "$state_dir/checklist.tsv" ]; then
    completed="$(awk -F '\t' 'NR>1 && $2=="already-done" { printf "- line %s [already-done] %s\n", $1, $3 }' "$state_dir/checklist.tsv")"
    remaining="$(awk -F '\t' 'NR>1 && $2!="already-done" { printf "- line %s [%s] %s\n", $1, $2, $3 }' "$state_dir/checklist.tsv")"
    local checklist_remaining checklist_external
    checklist_remaining="$(awk -F '\t' 'NR>1 && $2!="already-done" { count++ } END { print count+0 }' "$state_dir/checklist.tsv")"
    checklist_external="$(awk -F '\t' 'NR>1 && $2=="external-blocked" { count++ } END { print count+0 }' "$state_dir/checklist.tsv")"
    if [ "$checklist_remaining" -gt 0 ] && [ "$verdict" = "success" ]; then
      verdict="partial"
      stop_reason="remaining checklist items require another iteration or external action"
    fi
    if [ "$checklist_external" -gt 0 ]; then
      awk -F '\t' 'NR>1 && $2=="external-blocked" { printf "  - id: checklist-external-blocked-line-%s\n    command: \"checklist classification\"\n    evidence: \"%s\"\n    status: external-blocked\n    next_action: \"Resolve the external dependency, then rerun checklist mode.\"\n", $1, $4 }' "$state_dir/checklist.tsv" >> "$state_dir/blockers.md"
    fi
  fi
  [ -z "$completed" ] && completed="- configured loop run completed through iteration $iter"
  [ -z "$remaining" ] && remaining="- none"
  if [ -s "$state_dir/blockers.md" ]; then
    external_blockers="$(awk '/^  - id:/ { sub(/^  - id: /, ""); id=$0 } /^    next_action:/ { sub(/^    next_action: "?/, ""); sub(/"?$/, ""); printf "- %s: %s\n", id, $0 }' "$state_dir/blockers.md")"
  fi
  [ -z "$external_blockers" ] && external_blockers="- none"

  if [ "$memory_enabled" = "true" ] && [ "$memory_provider" = "strata" ]; then
    local memory_request="$state_dir/evidence/strata-memory-request.md"
    cat > "$memory_request" <<EOF
# Strata Memory Request

Provider: strata
Mode: consolidate
Objective: ${objective:-"(unset)"}
Verdict: $verdict
Summary: see $state_dir/SUMMARY.md and $state_dir/ledger.tsv.
Retrieval tests requested: $(yaml_section_scalar "$config" memory retrieval_tests false)
EOF
    if [ -n "${LOOP_MEMORY_CMD:-}" ]; then
      bash -lc "$LOOP_MEMORY_CMD '$memory_request'" > "$state_dir/evidence/strata-memory.log" 2>&1 || true
    fi
  fi

  local gates_passed_inline gates_blocked_inline gates_failed_inline
  gates_passed_inline="$(inline_items "$gates_passed")"
  gates_blocked_inline="$(inline_items "$gates_blocked")"
  gates_failed_inline="$(inline_items "$gates_failed")"

  cat > "$state_dir/SUMMARY.md" <<EOF
# Loop Engineering Summary

## Verdict

$verdict

## Completed

$completed

## Verification

- passed: $gates_passed_inline
- blocked: $gates_blocked_inline
- failed: $gates_failed_inline

## Commits

$commits

## Remaining

$remaining

## External Blockers

$external_blockers

## Next Start

- ${stop_reason:-Review ledger.tsv and continue from the next local-fixable item.}
EOF

  if [ "$commit_created" -eq 1 ] && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if [ -n "$(git status --short)" ]; then
      git add -A
      git commit --amend --no-edit >/tmp/loop-engineering-commit-amend.log 2>&1 || true
    fi
    if [ "$commit_needs_push" -eq 1 ]; then
      if git push origin HEAD >>/tmp/loop-engineering-commit.log 2>&1; then
        :
      else
        local push_evidence
        push_evidence="$(cat /tmp/loop-engineering-commit.log)"
        record_blocker "$state_dir/blockers.md" "git push origin HEAD" "$push_evidence" || true
        cat >> "$state_dir/SUMMARY.md" <<'EOF'

## Push Blocker

- git push origin HEAD failed; see blockers.md for normalized evidence.
EOF
        git add -A
        git commit --amend --no-edit >/tmp/loop-engineering-commit-amend.log 2>&1 || true
      fi
    fi
  fi

  printf 'Workflow complete: %s\nVerdict: %s\n' "$state_dir" "$verdict"
}

mode="${1:-}"
case "$mode" in
  --demo)
    run_demo
    ;;
  --config)
    [ $# -ge 2 ] || fail "--config requires a path"
    run_config "$2"
    ;;
  --checklist|checklist)
    [ $# -ge 2 ] || fail "--checklist requires a Markdown checklist path"
    checklist="$2"
    [ -f "$checklist" ] || fail "checklist file not found: $checklist"
    state_dir=".loop-engineering"
    ensure_repo_layout "$state_dir"
    if [ ! -f "$state_dir/loop.yml" ]; then
      "$SCRIPT_DIR/init-repo-loop.sh" >/dev/null
    fi
    run_config "$state_dir/loop.yml" "$checklist"
    ;;
  ""|-h|--help)
    usage
    [ -n "$mode" ] && exit 0 || exit 2
    ;;
  *)
    fail "unknown or missing mode: $mode"
    ;;
esac
