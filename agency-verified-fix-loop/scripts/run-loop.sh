#!/usr/bin/env bash
set -u

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$ROOT/.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
PORT="${PORT:-8099}"
STRICT="${STRICT:-0}"
KEEP_WORK="${KEEP_WORK:-0}"

SPEC_BIN="$KUJO_REPOS/spec/scripts/spec"
LENS_BIN="$KUJO_REPOS/lens/lens"
RUNLEDGER_BIN="$KUJO_REPOS/runledger/bin/runledger"
CHANGEBUCKET_BIN="$KUJO_REPOS/changebucket/bin/changebucket"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$ROOT/.runs/$STAMP"
WORK_DIR="$ROOT/.work/$STAMP"
PROJECT="$WORK_DIR/northstar-storefront"
LOG_DIR="$RUN_DIR/logs"
SUMMARY="$RUN_DIR/summary.md"

PASS_COUNT=0
FAIL_COUNT=0
EXPECTED_FAIL_COUNT=0
WARN_COUNT=0
RUN_ID=""
PHP_PID=""

mkdir -p "$RUN_DIR" "$WORK_DIR" "$LOG_DIR"

cat > "$SUMMARY" <<EOF
# Agency Verified Fix Loop Run

- Run timestamp: $STAMP
- Demo root: $ROOT
- Project worktree: $PROJECT
- Artifact root: $RUN_DIR
- Port: $PORT

## Stage Results

| Stage | Status | Exit | Log |
|---|---:|---:|---|
EOF

cleanup() {
  if [ -n "${PHP_PID:-}" ]; then
    kill "$PHP_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

record_stage() {
  local stage="$1"
  local status="$2"
  local code="$3"
  local log="$4"

  case "$status" in
    pass) PASS_COUNT=$((PASS_COUNT + 1)) ;;
    fail) FAIL_COUNT=$((FAIL_COUNT + 1)) ;;
    expected-fail) EXPECTED_FAIL_COUNT=$((EXPECTED_FAIL_COUNT + 1)) ;;
    warn) WARN_COUNT=$((WARN_COUNT + 1)) ;;
  esac

  printf '| `%s` | %s | %s | `%s` |\n' "$stage" "$status" "$code" "${log#$RUN_DIR/}" >> "$SUMMARY"
}

run_host() {
  local stage="$1"
  shift
  local log="$LOG_DIR/$stage.log"
  {
    printf '$'
    printf ' %q' "$@"
    printf '\n'
  } > "$log"
  "$@" >> "$log" 2>&1
  local code=$?
  if [ "$code" -eq 0 ]; then
    record_stage "$stage" pass "$code" "$log"
  else
    record_stage "$stage" fail "$code" "$log"
  fi
  return "$code"
}

run_host_shell() {
  local stage="$1"
  local command="$2"
  local log="$LOG_DIR/$stage.log"
  printf '$ %s\n' "$command" > "$log"
  bash -lc "$command" >> "$log" 2>&1
  local code=$?
  if [ "$code" -eq 0 ]; then
    record_stage "$stage" pass "$code" "$log"
  else
    record_stage "$stage" fail "$code" "$log"
  fi
  return "$code"
}

run_root() {
  local stage="$1"
  shift
  local log="$LOG_DIR/$stage.log"
  {
    printf 'cd %q\n' "$ROOT"
    printf '$'
    printf ' %q' "$@"
    printf '\n'
  } > "$log"
  (cd "$ROOT" && "$@") >> "$log" 2>&1
  local code=$?
  if [ "$code" -eq 0 ]; then
    record_stage "$stage" pass "$code" "$log"
  else
    record_stage "$stage" fail "$code" "$log"
  fi
  return "$code"
}

run_project() {
  local stage="$1"
  shift
  local log="$LOG_DIR/$stage.log"
  {
    printf 'cd %q\n' "$PROJECT"
    printf '$'
    printf ' %q' "$@"
    printf '\n'
  } > "$log"
  (cd "$PROJECT" && "$@") >> "$log" 2>&1
  local code=$?
  if [ "$code" -eq 0 ]; then
    record_stage "$stage" pass "$code" "$log"
  else
    record_stage "$stage" fail "$code" "$log"
  fi
  return "$code"
}

run_project_shell() {
  local stage="$1"
  local command="$2"
  local log="$LOG_DIR/$stage.log"
  {
    printf 'cd %q\n' "$PROJECT"
    printf '$ %s\n' "$command"
  } > "$log"
  (cd "$PROJECT" && bash -lc "$command") >> "$log" 2>&1
  local code=$?
  if [ "$code" -eq 0 ]; then
    record_stage "$stage" pass "$code" "$log"
  else
    record_stage "$stage" fail "$code" "$log"
  fi
  return "$code"
}

run_expect_code() {
  local expected="$1"
  local stage="$2"
  shift 2
  local log="$LOG_DIR/$stage.log"
  {
    printf '$'
    printf ' %q' "$@"
    printf '\n'
    printf '# Expected exit code: %s\n' "$expected"
  } > "$log"
  "$@" >> "$log" 2>&1
  local code=$?
  if [ "$code" -eq "$expected" ]; then
    record_stage "$stage" expected-fail "$code" "$log"
  else
    record_stage "$stage" fail "$code" "$log"
  fi
  return 0
}

run_lens() {
  local stage="$1"
  shift
  local log="$LOG_DIR/$stage.log"
  {
    printf 'cd %q\n' "$KUJO_REPOS/lens"
    printf '$ KUJO_BIN=%q %q' "$KUJO_BIN" "$LENS_BIN"
    printf ' %q' "$@"
    printf '\n'
  } > "$log"
  (
    cd "$KUJO_REPOS/lens" &&
      KUJO_BIN="$KUJO_BIN" "$LENS_BIN" "$@"
  ) >> "$log" 2>&1
  local code=$?
  if [ "$code" -eq 0 ]; then
    record_stage "$stage" pass "$code" "$log"
  else
    record_stage "$stage" fail "$code" "$log"
  fi
  return "$code"
}

run_lens_expect_code() {
  local expected="$1"
  local stage="$2"
  shift 2
  local log="$LOG_DIR/$stage.log"
  {
    printf 'cd %q\n' "$KUJO_REPOS/lens"
    printf '$ KUJO_BIN=%q %q' "$KUJO_BIN" "$LENS_BIN"
    printf ' %q' "$@"
    printf '\n'
    printf '# Expected exit code: %s\n' "$expected"
  } > "$log"
  (
    cd "$KUJO_REPOS/lens" &&
      KUJO_BIN="$KUJO_BIN" "$LENS_BIN" "$@"
  ) >> "$log" 2>&1
  local code=$?
  if [ "$code" -eq "$expected" ]; then
    record_stage "$stage" expected-fail "$code" "$log"
  else
    record_stage "$stage" fail "$code" "$log"
  fi
  return 0
}

ledger_note() {
  local note="$1"
  if [ -z "${RUN_ID:-}" ]; then
    return 0
  fi
  (
    cd "$PROJECT" &&
      RUNLEDGER_DIR="$RUN_DIR/runledger" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" note "$RUN_ID" "$note"
  ) >> "$LOG_DIR/runledger-notes.log" 2>&1 || true
}

start_runledger() {
  local log="$LOG_DIR/runledger-start.log"
  {
    printf 'cd %q\n' "$PROJECT"
    printf '$ RUNLEDGER_DIR=%q KUJO=%q %q start --provider scripted --model deterministic-fixture --task %q --prompt %q --repo .\n' \
      "$RUN_DIR/runledger" "$KUJO_BIN" "$RUNLEDGER_BIN" \
      "Northstar mobile promo drawer fix" "$RUN_DIR/spec/agent-context.md"
  } > "$log"

  (
    cd "$PROJECT" &&
      RUNLEDGER_DIR="$RUN_DIR/runledger" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" start \
        --provider scripted \
        --model deterministic-fixture \
        --task "Northstar mobile promo drawer fix" \
        --prompt "$RUN_DIR/spec/agent-context.md" \
        --repo .
  ) >> "$log" 2>&1

  local code=$?
  RUN_ID="$(sed -n 's/^Started run: //p' "$log" | head -n 1)"
  if [ "$code" -eq 0 ] && [ -n "$RUN_ID" ]; then
    printf '%s\n' "$RUN_ID" > "$RUN_DIR/run-id.txt"
    record_stage "runledger-start" pass "$code" "$log"
  else
    record_stage "runledger-start" fail "$code" "$log"
  fi
}

start_php_server() {
  local stage="php-server"
  local log="$LOG_DIR/$stage.log"
  printf '$ php -S 127.0.0.1:%s -t public\n' "$PORT" > "$log"

  (
    cd "$PROJECT" &&
      php -S "127.0.0.1:$PORT" -t public
  ) >> "$log" 2>&1 &
  PHP_PID=$!

  local i=0
  while [ "$i" -lt 40 ]; do
    if curl -fsS "http://127.0.0.1:$PORT/cart.php" >/dev/null 2>&1; then
      record_stage "$stage" pass 0 "$log"
      return 0
    fi
    sleep 0.25
    i=$((i + 1))
  done

  record_stage "$stage" fail 1 "$log"
  return 1
}

render_templates() {
  mkdir -p "$RUN_DIR/spec" "$RUN_DIR/eval" "$RUN_DIR/lens" "$RUN_DIR/briefs" "$RUN_DIR/client"
  sed "s/__PORT__/$PORT/g" "$ROOT/specs/mobile-promo-drawer.spec.yml.tpl" > "$RUN_DIR/spec/mobile-promo-drawer.spec.yml"
  sed "s/__PORT__/$PORT/g" "$ROOT/eval/mobile-promo-drawer.eval.json.tpl" > "$RUN_DIR/eval/mobile-promo-drawer.eval.json"
  sed "s/__PORT__/$PORT/g" "$ROOT/lens/mobile-promo-drawer.flow.json.tpl" > "$RUN_DIR/lens/mobile-promo-drawer.flow.json"
}

prepare_project() {
  if [ "$KEEP_WORK" != "1" ]; then
    rm -rf "$PROJECT"
  fi
  mkdir -p "$WORK_DIR"
  cp -R "$ROOT/fixtures/northstar-storefront-buggy" "$PROJECT"
  (
    cd "$PROJECT" &&
      git init -q &&
      git config user.email "demo@example.invalid" &&
      git config user.name "Agency Loop Demo" &&
      git add . &&
      git commit -qm "Initial buggy storefront fixture"
  )
}

apply_fix() {
  cp "$ROOT/fixtures/fixed-overrides/public/assets/js/cart.js" "$PROJECT/public/assets/js/cart.js"
  cp "$ROOT/fixtures/fixed-overrides/public/assets/css/cart.css" "$PROJECT/public/assets/css/cart.css"
}

assemble_client_handoff() {
  mkdir -p "$RUN_DIR/client"
  cat > "$RUN_DIR/client/CLIENT_HANDOFF.md" <<EOF
# Northstar Outfitters: Mobile Promo Drawer Fix

## Summary

The mobile cart promo-code drawer was fixed in the demo storefront. The deterministic fix changes the JavaScript promo handler to submit on the first tap and adds mobile spacing around the sticky checkout bar.

## Verification

- Spec validation and rendering were attempted.
- Scout and Scent context artifacts were attempted.
- Eval was run against PHP, JavaScript, HTTP, and file-content checks.
- Lens recorded a browser walkthrough when available.
- PatchBrief, ChangeBucket, ShipCheck, and RunLedger artifacts were attempted.

## Key Artifacts

- Run summary: \`../summary.md\`
- Lens proof: \`../lens/proof/walkthrough.html\`
- Eval results: \`../eval/results/summary.json\`
- Patch brief: \`../briefs/patchbrief.md\`
- ChangeBucket report: \`../briefs/changebucket.md\`
- RunLedger report: \`../briefs/runledger-report.md\`
EOF

  [ -f "$RUN_DIR/spec/mobile-promo-drawer.md" ] && cp "$RUN_DIR/spec/mobile-promo-drawer.md" "$RUN_DIR/client/mobile-promo-drawer.spec.md"
  [ -f "$RUN_DIR/briefs/patchbrief.md" ] && cp "$RUN_DIR/briefs/patchbrief.md" "$RUN_DIR/client/patchbrief.md"
  [ -f "$RUN_DIR/briefs/changebucket.md" ] && cp "$RUN_DIR/briefs/changebucket.md" "$RUN_DIR/client/changebucket.md"
  [ -f "$RUN_DIR/eval/results/summary.json" ] && cp "$RUN_DIR/eval/results/summary.json" "$RUN_DIR/client/eval-summary.json"
  [ -f "$RUN_DIR/lens/proof/walkthrough.html" ] && cp "$RUN_DIR/lens/proof/walkthrough.html" "$RUN_DIR/client/lens-walkthrough.html"
  mkdir -p "$RUN_DIR/client/video"
  [ -f "$RUN_DIR/lens/proof/video/walkthrough.webm" ] && cp "$RUN_DIR/lens/proof/video/walkthrough.webm" "$RUN_DIR/client/video/walkthrough.webm"
  [ -f "$RUN_DIR/lens/proof/video/walkthrough.mp4" ] && cp "$RUN_DIR/lens/proof/video/walkthrough.mp4" "$RUN_DIR/client/video/walkthrough.mp4"
  [ -f "$RUN_DIR/client/video/walkthrough.webm" ] && cp "$RUN_DIR/client/video/walkthrough.webm" "$RUN_DIR/client/lens-recording.webm"
  [ -f "$RUN_DIR/client/video/walkthrough.mp4" ] && cp "$RUN_DIR/client/video/walkthrough.mp4" "$RUN_DIR/client/lens-recording.mp4"
  [ -f "$RUN_DIR/briefs/shipcheck.md" ] && cp "$RUN_DIR/briefs/shipcheck.md" "$RUN_DIR/client/shipcheck.md"
  [ -f "$RUN_DIR/briefs/runledger-report.md" ] && cp "$RUN_DIR/briefs/runledger-report.md" "$RUN_DIR/client/runledger-report.md"
}

finish_summary() {
  cat >> "$SUMMARY" <<EOF

## Totals

- Passed stages: $PASS_COUNT
- Expected failing stages: $EXPECTED_FAIL_COUNT
- Warning stages: $WARN_COUNT
- Failed stages: $FAIL_COUNT

## Important Paths

- Worktree: \`$PROJECT\`
- Run artifacts: \`$RUN_DIR\`
- Client handoff: \`$RUN_DIR/client/CLIENT_HANDOFF.md\`
- Lens proof: \`$RUN_DIR/lens/proof/walkthrough.html\`
- RunLedger ID: \`${RUN_ID:-not-created}\`

EOF
}

echo "Agency Verified Fix Loop demo"
echo "Artifacts: $RUN_DIR"
echo "Worktree:  $PROJECT"
echo

run_host "preflight-kujo" "$KUJO_BIN" --version
run_host "preflight-php" php -v
run_host "preflight-node" node -v
run_host "preflight-lens" "$LENS_BIN" --version

run_host_shell "prepare-project" "$(printf 'ROOT=%q PROJECT=%q WORK_DIR=%q KEEP_WORK=%q; mkdir -p \"$WORK_DIR\"; rm -rf \"$PROJECT\"; cp -R \"$ROOT/fixtures/northstar-storefront-buggy\" \"$PROJECT\"; cd \"$PROJECT\"; git init -q; git config user.email demo@example.invalid; git config user.name \"Agency Loop Demo\"; git add .; git commit -qm \"Initial buggy storefront fixture\"' "$ROOT" "$PROJECT" "$WORK_DIR" "$KEEP_WORK")"
render_templates
record_stage "render-templates" pass 0 "$SUMMARY"

run_root "spec-validate" env KUJO_BIN="$KUJO_BIN" "$SPEC_BIN" validate "$RUN_DIR/spec/mobile-promo-drawer.spec.yml" --strict
run_root "spec-render" env KUJO_BIN="$KUJO_BIN" "$SPEC_BIN" render "$RUN_DIR/spec/mobile-promo-drawer.spec.yml" --output "$RUN_DIR/spec/mobile-promo-drawer.md"
run_root "spec-export-agent-context" env KUJO_BIN="$KUJO_BIN" "$SPEC_BIN" export-agent-context "$RUN_DIR/spec/mobile-promo-drawer.spec.yml" --output "$RUN_DIR/spec/agent-context.md"
run_root "spec-export-eval" env KUJO_BIN="$KUJO_BIN" "$SPEC_BIN" export-eval "$RUN_DIR/spec/mobile-promo-drawer.spec.yml" --output "$RUN_DIR/eval/mobile-promo-drawer.from-spec.json"

run_host "scout" "$KUJO_BIN" run "$KUJO_REPOS/scout/scout.kujo" -- "$PROJECT" --output "$RUN_DIR/scout" --max-depth 5 --security-export sarif

run_project "scent" "$KUJO_BIN" run "$KUJO_REPOS/scent/scent.kujo" pack \
  --task "Fix the mobile cart promo-code drawer so the input is visible and Apply works on first tap." \
  --out "$RUN_DIR/scent" \
  --target codex \
  --include public/cart.php \
  --include public/assets/js/cart.js \
  --include public/assets/css/cart.css \
  --include src/PromoCodeService.php \
  --include tests/promo_code_test.php \
  --max-files 20 \
  --max-file-bytes 60000 \
  --format both

run_host_shell "prepare-static-agent-pack" "$(printf 'mkdir -p %q; cp -R %q %q' "$RUN_DIR/pack" "$ROOT/agent-pack" "$RUN_DIR/pack/agent")"

if [ "${RUN_PACKWRITE:-0}" = "1" ] && [ -n "${PACKWRITE_API_KEY:-}" ]; then
  run_project "packwrite-live-dry-run" env PACKWRITE_API_KEY="$PACKWRITE_API_KEY" KUJO="$KUJO_BIN" "$KUJO_REPOS/packwrite/bin/packwrite" init "$RUN_DIR/spec/agent-context.md" --provider openai --model gpt-4.1-mini --output .agency-pack --dry-run
else
  record_stage "packwrite-live-dry-run" warn 0 "$SUMMARY"
fi

start_runledger
ledger_note "Started from client request. Spec, Scout, Scent, and static agent-pack artifacts prepared."

start_php_server

run_lens_expect_code 1 "lens-pre-fix-expected-failure" flow "$RUN_DIR/lens/mobile-promo-drawer.flow.json" --execute --walkthrough --out "$RUN_DIR/lens/pre-fix"
ledger_note "Pre-fix Lens flow failed as expected, proving the fixture reproduces the client-visible bug."

run_project "casefile-pre-fix-lens" "$KUJO_BIN" run --interpreter "$KUJO_REPOS/casefile/casefile.kujo" -- capture \
  --name pre-fix-lens-flow \
  --output-dir .casefile-agency-loop \
  -- /bin/bash -lc "cd '$KUJO_REPOS/lens' && KUJO_BIN='$KUJO_BIN' '$LENS_BIN' flow '$RUN_DIR/lens/mobile-promo-drawer.flow.json' --execute --walkthrough --out '$RUN_DIR/lens/casefile-replay'"

run_host_shell "apply-deterministic-fix" "$(printf 'cp %q %q; cp %q %q' \
  "$ROOT/fixtures/fixed-overrides/public/assets/js/cart.js" "$PROJECT/public/assets/js/cart.js" \
  "$ROOT/fixtures/fixed-overrides/public/assets/css/cart.css" "$PROJECT/public/assets/css/cart.css")"
ledger_note "Applied deterministic JS/CSS fix from fixed-overrides."

run_project "eval" "$KUJO_BIN" run "$KUJO_REPOS/eval/main.kujo" run "$RUN_DIR/eval/mobile-promo-drawer.eval.json" --output-dir "$RUN_DIR/eval/results" --artifact-checksums --json
run_project "eval-verify-manifest" "$KUJO_BIN" run "$KUJO_REPOS/eval/main.kujo" verify-manifest --output-dir "$RUN_DIR/eval/results" --json
ledger_note "Eval suite attempted. See eval/results for machine-readable output."

run_lens "lens-check" check "http://127.0.0.1:$PORT/cart.php" --viewport mobile --viewport desktop --html --out "$RUN_DIR/lens/check"
run_lens "lens-inspect" inspect "http://127.0.0.1:$PORT/cart.php" --json --out "$RUN_DIR/lens/inspect"
run_lens "lens-proof" flow "$RUN_DIR/lens/mobile-promo-drawer.flow.json" --execute --record --walkthrough --out "$RUN_DIR/lens/proof"
ledger_note "Lens check, inspect, and proof flow attempted. See lens/proof for walkthrough."

run_project_shell "patchbrief-summary" "$(printf '%q run %q -- summarize --format markdown > %q' "$KUJO_BIN" "$KUJO_REPOS/patchbrief/patchbrief.kujo" "$RUN_DIR/briefs/patchbrief.md")"
run_project_shell "patchbrief-tests" "$(printf '%q run %q -- suggest-tests > %q' "$KUJO_BIN" "$KUJO_REPOS/patchbrief/patchbrief.kujo" "$RUN_DIR/briefs/test-suggestions.md")"
run_project_shell "patchbrief-handoff" "$(printf '%q run %q -- handoff > %q' "$KUJO_BIN" "$KUJO_REPOS/patchbrief/patchbrief.kujo" "$RUN_DIR/briefs/reviewer-handoff.md")"

run_project "changebucket-report" env KUJO="$KUJO_BIN" "$CHANGEBUCKET_BIN" --markdown --output "$RUN_DIR/briefs/changebucket.md"
run_project "changebucket-check" env KUJO="$KUJO_BIN" "$CHANGEBUCKET_BIN" check --max-files 8 --max-churn 350 --no-dependency-changes --no-lockfile-changes --no-generated-changes

run_project_shell "shipcheck-scan" "$(printf '%q run %q -- scan --dir . --format markdown > %q' "$KUJO_BIN" "$KUJO_REPOS/shipcheck/shipcheck.kujo" "$RUN_DIR/briefs/shipcheck.md")"
run_project_shell "shipcheck-gate" "$(printf '%q run %q -- gate --dir . --format json > %q' "$KUJO_BIN" "$KUJO_REPOS/shipcheck/shipcheck.kujo" "$RUN_DIR/briefs/shipcheck-gate.json")"

if [ -n "${RUN_ID:-}" ]; then
  run_project "runledger-usage" env RUNLEDGER_DIR="$RUN_DIR/runledger" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" usage "$RUN_ID" --input 42000 --output 9000
  run_project "runledger-cost" env RUNLEDGER_DIR="$RUN_DIR/runledger" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" cost "$RUN_ID" --total 0.84 --currency USD
  run_project "runledger-finish" env RUNLEDGER_DIR="$RUN_DIR/runledger" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" finish "$RUN_ID" --status pass --verdict "Demo fix applied; Eval and Lens evidence attempted; review summary artifacts generated." --repo .
  run_project "runledger-report" env RUNLEDGER_DIR="$RUN_DIR/runledger" KUJO="$KUJO_BIN" "$RUNLEDGER_BIN" report --task "Northstar mobile promo drawer fix" --output "$RUN_DIR/briefs/runledger-report.md"
else
  record_stage "runledger-finish" warn 0 "$SUMMARY"
fi

assemble_client_handoff
record_stage "client-handoff" pass 0 "$SUMMARY"

finish_summary

echo
echo "Run complete."
echo "Summary: $SUMMARY"
echo "Client handoff: $RUN_DIR/client/CLIENT_HANDOFF.md"
echo

if [ "$STRICT" = "1" ] && [ "$FAIL_COUNT" -gt 0 ]; then
  exit 1
fi

exit 0
