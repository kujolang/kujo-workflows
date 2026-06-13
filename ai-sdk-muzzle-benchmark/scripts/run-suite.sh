#!/usr/bin/env bash
set -u -o pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TRIALS="${TRIALS:-5}"
SUITE_STAMP="${SUITE_STAMP:-$(date -u +%Y%m%dT%H%M%SZ)}"
SUITE_DIR="${SUITE_DIR:-$ROOT/.suites/$SUITE_STAMP}"
PORT_BASE="${PORT_BASE:-8220}"
TEMPERATURE="${TEMPERATURE:-0}"

mkdir -p "$SUITE_DIR/logs"

RUN_DIRS_FILE="$SUITE_DIR/run-dirs.txt"
SUMMARY="$SUITE_DIR/summary.md"
: > "$RUN_DIRS_FILE"

cat > "$SUMMARY" <<EOF
# AI SDK + Muzzle Benchmark Suite

- Suite timestamp: $SUITE_STAMP
- Trials: $TRIALS
- Provider: ${PROVIDER:-openai}
- Model: ${MODEL:-provider default}
- Temperature: $TEMPERATURE

## Trials

| Trial | Status | Run dir | Log |
|---:|---:|---|---|
EOF

echo "AI SDK + Muzzle benchmark suite"
echo "Suite dir: $SUITE_DIR"
echo "Trials: $TRIALS"
echo "Provider: ${PROVIDER:-openai}"
echo "Model: ${MODEL:-provider default}"
echo "Temperature: $TEMPERATURE"
echo

trial=1
failures=0

while [ "$trial" -le "$TRIALS" ]; do
  trial_label="$(printf 'trial-%02d' "$trial")"
  trial_stamp="$SUITE_STAMP-$trial_label"
  trial_run_dir="$ROOT/.runs/$trial_stamp"
  trial_log="$SUITE_DIR/logs/$trial_label.log"
  trial_port=$((PORT_BASE + (trial - 1) * 4))

  echo "Running $trial_label..."

  RUN_DIR="$trial_run_dir" \
    STAMP="$trial_stamp" \
    PORT_BASE="$trial_port" \
    TEMPERATURE="$TEMPERATURE" \
    bash "$ROOT/scripts/run-benchmark.sh" >"$trial_log" 2>&1
  code=$?

  printf '%s\n' "$trial_run_dir" >> "$RUN_DIRS_FILE"

  if [ "$code" -eq 0 ]; then
    printf '| %s | pass | `%s` | `%s` |\n' "$trial" "$trial_run_dir" "${trial_log#$SUITE_DIR/}" >> "$SUMMARY"
  else
    failures=$((failures + 1))
    printf '| %s | fail | `%s` | `%s` |\n' "$trial" "$trial_run_dir" "${trial_log#$SUITE_DIR/}" >> "$SUMMARY"
  fi

  trial=$((trial + 1))
done

SUITE_REVIEW="$(node "$ROOT/scripts/generate-suite-review-html.js" "$SUITE_DIR" $(cat "$RUN_DIRS_FILE"))"

cat >> "$SUMMARY" <<EOF

## Totals

- Failed trial commands: $failures
- Suite dashboard: \`$SUITE_REVIEW\`
- Run dirs file: \`$RUN_DIRS_FILE\`

EOF

echo
echo "Suite dashboard: $SUITE_REVIEW"
echo "Summary: $SUMMARY"

if [ "$failures" -gt 0 ]; then
  exit 1
fi

exit 0

