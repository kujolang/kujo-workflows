#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPOS="$(cd "$ROOT/.." && pwd)"
if [ -n "${KUJO_REPOS-}" ]; then REPOS="$KUJO_REPOS"; fi
KUJO="$REPOS/kujo/target/release/kujo"
if [ -n "${KUJO_BIN-}" ]; then KUJO="$KUJO_BIN"; fi
SPEC="$REPOS/spec/scripts/spec"
SCOUT="$REPOS/scout/scout.kujo"
SCENT="$REPOS/scent/scent.kujo"
LENS="$REPOS/lens/lens"
CASEFILE="$REPOS/casefile/casefile.kujo"
PACKWRITE="$REPOS/packwrite"
RUNLEDGER="$REPOS/runledger/bin/runledger"

for required in "$KUJO" "$SPEC" "$SCOUT" "$SCENT" "$LENS" "$CASEFILE" "$PACKWRITE/bin/packwrite" "$RUNLEDGER"; do
  test -e "$required" || { echo "missing relationship dependency: $required" >&2; exit 1; }
done

TMP="$(mktemp -d /tmp/kujo-skill-relationships.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

expect_failure() {
  local log="$1"
  shift
  set +e
  "$@" >"$log" 2>&1
  local code=$?
  set -e
  test "$code" -ne 0 || { echo "expected failure but command passed: $*" >&2; cat "$log" >&2; return 1; }
}

AGENCY_PROJECT="$TMP/agency-project"
mkdir -p "$AGENCY_PROJECT/src"
printf 'print("fixture")\n' > "$AGENCY_PROJECT/src/main.py"
git -C "$AGENCY_PROJECT" init -q
git -C "$AGENCY_PROJECT" config user.email skill-contract@example.invalid
git -C "$AGENCY_PROJECT" config user.name SkillContract
git -C "$AGENCY_PROJECT" add .
git -C "$AGENCY_PROJECT" commit -qm fixture

python3 "$ROOT/agency-runner/bin/agency-loop" --project "$AGENCY_PROJECT" init >/dev/null
python3 "$ROOT/agency-runner/bin/agency-loop" --project "$AGENCY_PROJECT" site add fixture \
  --type static --environment local --base-url http://127.0.0.1:1 \
  --repo-path "$AGENCY_PROJECT" --auth-strategy no-auth >/dev/null
python3 "$ROOT/agency-runner/bin/agency-loop" --project "$AGENCY_PROJECT" run \
  --site fixture --recipe theme-layout --text "Review the mobile layout" --phase spec >/dev/null
AGENCY_RUN="$(find "$AGENCY_PROJECT/.kujo/runs" -mindepth 1 -maxdepth 1 -type d | head -1)"
AGENCY_TOOL_TIMEOUT_SECONDS=30 python3 "$ROOT/agency-runner/bin/agency-loop" \
  --project "$AGENCY_PROJECT" run --run "$AGENCY_RUN" --phase context >/dev/null
jq -e '.phases.spec == "pass" and .phases.context == "pass"' "$AGENCY_RUN/run-state.json" >/dev/null
test -s "$AGENCY_RUN/logs/spec-validate.log"
test -s "$AGENCY_RUN/logs/scout.log"
test -s "$AGENCY_RUN/logs/scent.log"
find "$AGENCY_RUN/context/scout" -name scan_manifest.json -print -quit | grep -q .
test -s "$AGENCY_RUN/context/scent/manifest.json"

MISSING_TOOLS="$TMP/missing-tools"
mkdir -p "$MISSING_TOOLS/kujo/target/release"
touch "$MISSING_TOOLS/kujo/target/release/kujo"
KUJO_REPOS="$MISSING_TOOLS" python3 "$ROOT/agency-runner/bin/agency-loop" \
  --project "$AGENCY_PROJECT" run --run "$AGENCY_RUN" --phase context >/dev/null
jq -e '.phases.context == "failed"' "$AGENCY_RUN/run-state.json" >/dev/null

BAD_SCOUT="$TMP/scout-bad.log"
expect_failure "$BAD_SCOUT" "$KUJO" run "$SCOUT" -- "$AGENCY_PROJECT/missing" --output "$TMP/scout-bad"
grep -q "target path not found" "$BAD_SCOUT"

BAD_SCENT="$TMP/scent-bad.log"
expect_failure "$BAD_SCENT" "$KUJO" run "$SCENT" pack --task "contract test" --out "$TMP/scent-bad" --include ../outside
grep -q "cannot contain '..'" "$BAD_SCENT"

LENS_VALID="$TMP/valid.flow.json"
python3 - "$ROOT/agency-verified-fix-loop/lens/mobile-promo-drawer.flow.json.tpl" "$LENS_VALID" <<'PY'
import sys
from pathlib import Path
Path(sys.argv[2]).write_text(Path(sys.argv[1]).read_text().replace("__PORT__", "1"), encoding="utf-8")
PY
"$LENS" flow "$LENS_VALID" --validate >"$TMP/lens-valid.log"
printf '{"name":"invalid","steps":"not-an-array"}\n' > "$TMP/lens-invalid.json"
expect_failure "$TMP/lens-invalid.log" "$LENS" flow "$TMP/lens-invalid.json" --validate
grep -q "INVALID" "$TMP/lens-invalid.log"

CASE_PROJECT="$TMP/casefile-project"
mkdir -p "$CASE_PROJECT"
git -C "$CASE_PROJECT" init -q
git -C "$CASE_PROJECT" config user.email casefile@example.invalid
git -C "$CASE_PROJECT" config user.name CasefileContract
set +e
(cd "$CASE_PROJECT" && "$KUJO" run --interpreter "$CASEFILE" -- capture --name failing-command --mirror-exit-code -- false) >"$TMP/casefile-good.log" 2>&1
CASE_CODE=$?
set -e
test "$CASE_CODE" -eq 1
find "$CASE_PROJECT/.casefile" -name case.json -print -quit | grep -q .
expect_failure "$TMP/casefile-bad.log" bash -c "cd '$CASE_PROJECT' && '$KUJO' run --interpreter '$CASEFILE' -- capture --from-log '$CASE_PROJECT/missing.log' --name missing-log"
grep -q "log file not found" "$TMP/casefile-bad.log"

PACK_PROJECT="$TMP/packwrite-project"
mkdir -p "$PACK_PROJECT"
printf '# Contract fixture\n' > "$PACK_PROJECT/MEGA_PROMPT.md"
"$KUJO" run "$PACKWRITE/tests/fixture.kujo" > "$TMP/packwrite-valid.json"
(cd "$PACK_PROJECT" && PACKWRITE_FAKE_RESPONSE_FILE="$TMP/packwrite-valid.json" KUJO="$KUJO" "$PACKWRITE/bin/packwrite" init MEGA_PROMPT.md >/dev/null)
test -s "$PACK_PROJECT/agent/MASTER.md"
printf 'not-json\n' > "$TMP/packwrite-invalid.json"
rm -rf "$PACK_PROJECT/agent"
expect_failure "$TMP/packwrite-bad.log" bash -c "cd '$PACK_PROJECT' && PACKWRITE_FAKE_RESPONSE_FILE='$TMP/packwrite-invalid.json' KUJO='$KUJO' '$PACKWRITE/bin/packwrite' init MEGA_PROMPT.md"
test ! -e "$PACK_PROJECT/agent"

LEDGER_PROJECT="$TMP/runledger-project"
LEDGER="$LEDGER_PROJECT/.runledger"
mkdir -p "$LEDGER_PROJECT"
git -C "$LEDGER_PROJECT" init -q
git -C "$LEDGER_PROJECT" config user.email runledger@example.invalid
git -C "$LEDGER_PROJECT" config user.name RunLedgerContract
START_OUT="$(KUJO="$KUJO" "$RUNLEDGER" start --provider local --model fixture --task "skill contract" --repo "$LEDGER_PROJECT" --ledger "$LEDGER")"
RUN_ID="$(printf '%s\n' "$START_OUT" | sed -n 's/^Started run: //p')"
test -n "$RUN_ID"
KUJO="$KUJO" "$RUNLEDGER" finish "$RUN_ID" --status pass --verdict "contract boundary passed" --ledger "$LEDGER" >/dev/null
jq -e '.status == "pass"' "$LEDGER/runs/$RUN_ID.json" >/dev/null
expect_failure "$TMP/runledger-bad.log" env KUJO="$KUJO" "$RUNLEDGER" finish "$RUN_ID" --status in_progress --verdict bad --ledger "$LEDGER"

DOCGEN_RUN="$TMP/docsgen-run"
RUN_DIR="$DOCGEN_RUN" KUJO_REPOS="$REPOS" bash "$ROOT/docsgen-repo-contract-runner/scripts/run-workflow.sh" >/dev/null
test -s "$DOCGEN_RUN/SUMMARY.md"
test -s "$DOCGEN_RUN/generated-docs/docgen.json"
expect_failure "$TMP/docsgen-bad.log" env RUN_DIR="$TMP/docsgen-bad" KUJO_REPOS="$REPOS" TARGET_REPO="$TMP/missing-repo" bash "$ROOT/docsgen-repo-contract-runner/scripts/run-workflow.sh"
grep -q "does not exist" "$TMP/docsgen-bad.log"

RAG_RUN="$TMP/rag-run"
RUN_DIR="$RAG_RUN" KUJO_REPOS="$REPOS" bash "$ROOT/rag-enterprise-knowledge-gate/scripts/run-workflow.sh" >/dev/null
test -s "$RAG_RUN/SUMMARY.md"
find "$RAG_RUN/index" -name '*.json' -print -quit | grep -q .
expect_failure "$TMP/rag-bad.log" env RUN_DIR="$TMP/rag-bad" KUJO_REPOS="$REPOS" RAG_REPO="$TMP/missing-rag" bash "$ROOT/rag-enterprise-knowledge-gate/scripts/run-workflow.sh"
grep -q "Missing RAG repo" "$TMP/rag-bad.log"

echo "PASS skill relationship contracts: Spec Scout Scent Lens CaseFile PackWrite RunLedger DocsGen RAG"
