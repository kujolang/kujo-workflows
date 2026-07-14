#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$WORKFLOW_DIR/../.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
CASEFILE_REPO="${CASEFILE_REPO:-$KUJO_REPOS/casefile}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR:-$WORKFLOW_DIR/.runs/$STAMP}"
FIXTURE="$RUN_DIR/fixture"
LOG_DIR="$RUN_DIR/logs"

mkdir -p "$FIXTURE" "$LOG_DIR"

if [[ ! -x "$KUJO_BIN" ]]; then
  echo "Missing executable Kujo runtime: $KUJO_BIN" >&2
  exit 1
fi

if [[ ! -f "$CASEFILE_REPO/casefile.kujo" ]]; then
  echo "Missing CaseFile repo: $CASEFILE_REPO" >&2
  exit 1
fi

cat > "$FIXTURE/README.md" <<'EOF'
# Billing Worker Fixture

This fixture intentionally contains a failing health check so CaseFile can capture a useful evidence packet.
EOF

cat > "$FIXTURE/check.sh" <<'EOF'
#!/usr/bin/env bash
echo "checking billing worker"
echo "DATABASE_URL is not configured" >&2
exit 9
EOF
chmod +x "$FIXTURE/check.sh"

(
  cd "$FIXTURE"
  git init -q
  git config user.email "demo@example.test"
  git config user.name "Kujo Demo"
  git add .
  git commit -qm "Initial fixture"
) >/dev/null 2>&1 || true

{
  echo -e "stage\tstatus\tdetail"
  echo -e "fixture\tpass\t$FIXTURE"
} > "$RUN_DIR/status.tsv"

(
  cd "$FIXTURE"
  "$KUJO_BIN" run --interpreter "$CASEFILE_REPO/casefile.kujo" -- init
) > "$LOG_DIR/init.log" 2>&1
echo -e "init\tpass\t$LOG_DIR/init.log" >> "$RUN_DIR/status.tsv"

(
  cd "$FIXTURE"
  "$KUJO_BIN" run --interpreter "$CASEFILE_REPO/casefile.kujo" -- validate
) > "$LOG_DIR/validate.log" 2>&1
echo -e "validate\tpass\t$LOG_DIR/validate.log" >> "$RUN_DIR/status.tsv"

(
  cd "$FIXTURE"
  "$KUJO_BIN" run --interpreter "$CASEFILE_REPO/casefile.kujo" -- capture --name billing-worker-health -- ./check.sh
) > "$LOG_DIR/capture.log" 2>&1
echo -e "capture\tpass\t$LOG_DIR/capture.log" >> "$RUN_DIR/status.tsv"

(
  cd "$FIXTURE"
  "$KUJO_BIN" run --interpreter "$CASEFILE_REPO/casefile.kujo" -- show latest --format markdown
) > "$LOG_DIR/show-latest.md" 2>&1
echo -e "show-markdown\tpass\t$LOG_DIR/show-latest.md" >> "$RUN_DIR/status.tsv"

(
  cd "$FIXTURE"
  "$KUJO_BIN" run --interpreter "$CASEFILE_REPO/casefile.kujo" -- show latest --format json
) > "$LOG_DIR/show-latest.json" 2>&1
echo -e "show-json\tpass\t$LOG_DIR/show-latest.json" >> "$RUN_DIR/status.tsv"

CASE_DIR="$(find "$FIXTURE/.casefile" -mindepth 1 -maxdepth 1 -type d | sort | tail -1)"
if [[ -z "$CASE_DIR" ]]; then
  echo "CaseFile did not create a case directory" >&2
  exit 1
fi

for required in "$CASE_DIR/case.md" "$CASE_DIR/case.json" "$CASE_DIR/combined.log" "$CASE_DIR/reproduction.md" "$CASE_DIR/handoff.md"; do
  if [[ ! -f "$required" ]]; then
    echo "Missing expected CaseFile artifact: $required" >&2
    exit 1
  fi
done
echo -e "artifact-check\tpass\t$CASE_DIR" >> "$RUN_DIR/status.tsv"

cat > "$RUN_DIR/SUMMARY.md" <<EOF
# CaseFile Incident Evidence Packet Summary

Run: $STAMP

## Verdict

PASS - CaseFile captured a deterministic local failure and produced a reviewable case bundle.

## Content Pillar

Failures should automatically become structured evidence packets with command, logs, git context, reproduction notes, and handoff guidance.

## Key Artifacts

- Fixture repo: \`$FIXTURE\`
- Case directory: \`$CASE_DIR\`
- Case markdown: \`$CASE_DIR/case.md\`
- Handoff: \`$CASE_DIR/handoff.md\`
- Rendered latest case: \`$LOG_DIR/show-latest.md\`
- JSON latest case: \`$LOG_DIR/show-latest.json\`

## Buyer Relevance

- Developers: faster failure triage and cleaner handoffs.
- Agency owners: client-ready evidence without manual reconstruction.
- Enterprise: repeatable incident packet format with local redaction and provenance.
EOF

echo "Workflow complete: $RUN_DIR"
