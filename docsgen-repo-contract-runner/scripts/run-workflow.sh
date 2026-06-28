#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-/Users/robertdevore/2026/Kujolang/kujo-repos}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR:-$WORKFLOW_DIR/.runs/$STAMP}"
FIXTURE="$RUN_DIR/fixture/docsgen-demo-service"
OUT_DIR="${DOCGEN_OUT_DIR:-$RUN_DIR/generated-docs}"
ARTIFACT_DIR="$RUN_DIR/artifacts"
LOG_DIR="$RUN_DIR/logs"

mkdir -p "$RUN_DIR" "$OUT_DIR" "$ARTIFACT_DIR" "$LOG_DIR"

if [[ ! -x "$KUJO_BIN" ]]; then
  echo "Missing executable Kujo runtime: $KUJO_BIN" >&2
  exit 1
fi

if [[ -n "${TARGET_REPO:-}" ]]; then
  if [[ ! -e "$TARGET_REPO" ]]; then
    echo "TARGET_REPO does not exist: $TARGET_REPO" >&2
    exit 1
  fi
  if [[ -d "$TARGET_REPO" ]]; then
    TARGET_PATH="$(cd "$TARGET_REPO" && pwd)"
  else
    TARGET_DIR="$(cd "$(dirname "$TARGET_REPO")" && pwd)"
    TARGET_PATH="$TARGET_DIR/$(basename "$TARGET_REPO")"
  fi
  TARGET_MODE="user"
else
  mkdir -p "$FIXTURE/src" "$FIXTURE/docs"
  TARGET_PATH="$FIXTURE"
  TARGET_MODE="fixture"

  cat > "$FIXTURE/README.md" <<'EOF'
# DocsGen Demo Service

Small fixture used to demonstrate scan-only documentation generation, public API gap reporting, and agent-readable output.
EOF

  cat > "$FIXTURE/src/accounts.ts" <<'EOF'
/**
 * Public account record returned by the demo service.
 */
export interface AccountRecord {
  id: string;
  name: string;
}

/**
 * Lists account records that are safe to show in documentation examples.
 */
export function listAccounts(): AccountRecord[] {
  return [
    { id: "acct_001", name: "Acme" },
    { id: "acct_002", name: "Northstar" },
  ];
}
EOF

  cat > "$FIXTURE/src/health.py" <<'EOF'
def health_status():
    """Return the service health status for operational dashboards."""
    return {"ok": True}
EOF

  cat > "$FIXTURE/src/policies.kujo" <<'EOF'
/// Returns the documentation policy used by the fixture.
pub func docs_policy() -> string {
  return "scan-only"
}
EOF

  cat > "$FIXTURE/docs/review.md" <<'EOF'
# Review Notes

Generated docs should be inspected before publication. Agents should use gap files as work queues, not as proof that invented behavior is real.
EOF
fi

DOCGEN_FORMAT="${DOCGEN_FORMAT:-all}"
DOCGEN_PUBLIC_ONLY="${DOCGEN_PUBLIC_ONLY:-1}"
DOCGEN_INCLUDE_PRIVATE="${DOCGEN_INCLUDE_PRIVATE:-0}"
DOCGEN_EMIT_AI_TASKS="${DOCGEN_EMIT_AI_TASKS:-1}"
DOCGEN_SEARCH_INDEX="${DOCGEN_SEARCH_INDEX:-1}"
DOCGEN_VALIDATE_LOCAL_ANCHORS="${DOCGEN_VALIDATE_LOCAL_ANCHORS:-1}"
DOCGEN_FAIL_ON_UNDOCUMENTED="${DOCGEN_FAIL_ON_UNDOCUMENTED:-0}"
DOCGEN_FAIL_ON_BROKEN_LINKS="${DOCGEN_FAIL_ON_BROKEN_LINKS:-0}"
DOCGEN_FAIL_ON_WARNINGS="${DOCGEN_FAIL_ON_WARNINGS:-0}"
DOCGEN_NO_BUILTINS="${DOCGEN_NO_BUILTINS:-0}"

if [[ "${DOCGEN_STRICT:-0}" == "1" ]]; then
  DOCGEN_PUBLIC_ONLY=1
  DOCGEN_FAIL_ON_UNDOCUMENTED=1
  DOCGEN_FAIL_ON_BROKEN_LINKS=1
  DOCGEN_FAIL_ON_WARNINGS=1
fi

args=(docgen "$TARGET_PATH" --out-dir "$OUT_DIR" --format "$DOCGEN_FORMAT" --json)

if [[ -n "${DOCGEN_LANGUAGE:-}" ]]; then
  args+=(--language "$DOCGEN_LANGUAGE")
fi

if [[ -n "${DOCGEN_LANGUAGES:-}" ]]; then
  args+=(--languages "$DOCGEN_LANGUAGES")
fi

if [[ "$DOCGEN_PUBLIC_ONLY" == "1" ]]; then
  args+=(--public-only)
fi

if [[ "$DOCGEN_INCLUDE_PRIVATE" == "1" ]]; then
  args+=(--include-private)
fi

if [[ "$DOCGEN_EMIT_AI_TASKS" == "1" ]]; then
  args+=(--emit-ai-tasks)
fi

if [[ "$DOCGEN_SEARCH_INDEX" == "1" ]]; then
  args+=(--search-index)
fi

if [[ "$DOCGEN_VALIDATE_LOCAL_ANCHORS" == "1" ]]; then
  args+=(--validate-local-anchors)
fi

if [[ "${DOCGEN_VALIDATE_EXTERNAL_LINKS:-0}" == "1" ]]; then
  args+=(--validate-external-links)
fi

if [[ -n "${DOCGEN_EXTERNAL_LINK_ALLOWLIST:-}" ]]; then
  args+=(--external-link-allowlist "$DOCGEN_EXTERNAL_LINK_ALLOWLIST")
fi

if [[ -n "${DOCGEN_EXTERNAL_LINK_TIMEOUT_MS:-}" ]]; then
  args+=(--external-link-timeout-ms "$DOCGEN_EXTERNAL_LINK_TIMEOUT_MS")
fi

if [[ -n "${DOCGEN_MAX_LINK_CHECKS:-}" ]]; then
  args+=(--max-link-checks "$DOCGEN_MAX_LINK_CHECKS")
fi

if [[ -n "${DOCGEN_MAX_EXTERNAL_LINK_CHECKS:-}" ]]; then
  args+=(--max-external-link-checks "$DOCGEN_MAX_EXTERNAL_LINK_CHECKS")
fi

if [[ -n "${DOCGEN_MAX_TOTAL_VALIDATION_TIME_MS:-}" ]]; then
  args+=(--max-total-validation-time-ms "$DOCGEN_MAX_TOTAL_VALIDATION_TIME_MS")
fi

if [[ "$DOCGEN_FAIL_ON_UNDOCUMENTED" == "1" ]]; then
  args+=(--fail-on-undocumented)
fi

if [[ "$DOCGEN_FAIL_ON_BROKEN_LINKS" == "1" ]]; then
  args+=(--fail-on-broken-links)
fi

if [[ "$DOCGEN_FAIL_ON_WARNINGS" == "1" ]]; then
  args+=(--fail-on-warnings)
fi

if [[ "$DOCGEN_NO_BUILTINS" == "1" ]]; then
  args+=(--no-builtins)
fi

if [[ "${DOCGEN_SOURCE_LINKS:-0}" == "1" ]]; then
  args+=(--source-links)
fi

if [[ -n "${DOCGEN_SOURCE_LINK_TEMPLATE:-}" ]]; then
  args+=(--source-link-template "$DOCGEN_SOURCE_LINK_TEMPLATE")
fi

if [[ -n "${DOCGEN_MAX_FILE_SIZE_BYTES:-}" ]]; then
  args+=(--max-discovery-file-size-bytes "$DOCGEN_MAX_FILE_SIZE_BYTES")
fi

if [[ -n "${DOCGEN_MAX_FILES:-}" ]]; then
  args+=(--max-discovery-files "$DOCGEN_MAX_FILES")
fi

if [[ -n "${DOCGEN_MAX_DEPTH:-}" ]]; then
  args+=(--max-discovery-depth "$DOCGEN_MAX_DEPTH")
fi

if [[ -n "${DOCGEN_CACHE_DIR:-}" ]]; then
  args+=(--cache-dir "$DOCGEN_CACHE_DIR")
fi

if [[ "${DOCGEN_KUJO_PARSER_ASSISTED:-0}" == "1" ]]; then
  args+=(--kujo-parser-assisted)
fi

printf '%q ' "$KUJO_BIN" "${args[@]}" > "$LOG_DIR/docgen-command.txt"
printf '\n' >> "$LOG_DIR/docgen-command.txt"

{
  echo -e "stage\tstatus\tdetail"
  echo -e "target\tpass\t$TARGET_PATH"
} > "$RUN_DIR/status.tsv"

set +e
"$KUJO_BIN" "${args[@]}" > "$LOG_DIR/docgen-cli.json" 2> "$LOG_DIR/docgen.stderr"
DOCGEN_STATUS=$?
set -e

if [[ "$DOCGEN_STATUS" -eq 0 ]]; then
  echo -e "docgen\tpass\t$LOG_DIR/docgen-cli.json" >> "$RUN_DIR/status.tsv"
  VERDICT="PASS - DocsGen completed and wrote generated documentation artifacts."
else
  echo -e "docgen\tfail\t$LOG_DIR/docgen.stderr" >> "$RUN_DIR/status.tsv"
  VERDICT="FAIL - DocsGen exited with status $DOCGEN_STATUS. Review logs before using generated output."
fi

for required in "$OUT_DIR/docgen.json" "$OUT_DIR/docgen-gaps.json" "$OUT_DIR/docgen-capabilities.json"; do
  if [[ -f "$required" ]]; then
    echo -e "artifact\tpass\t$required" >> "$RUN_DIR/status.tsv"
  else
    echo -e "artifact\tmissing\t$required" >> "$RUN_DIR/status.tsv"
  fi
done

cat > "$ARTIFACT_DIR/agent-handoff.md" <<EOF
# DocsGen Agent Handoff

## Target

- Mode: $TARGET_MODE
- Path: \`$TARGET_PATH\`
- Output: \`$OUT_DIR\`
- Exit status: $DOCGEN_STATUS

## Review Order

1. Read \`$RUN_DIR/SUMMARY.md\`.
2. Inspect \`$LOG_DIR/docgen-cli.json\` for the machine-readable run contract.
3. Inspect \`$OUT_DIR/docgen-gaps.json\` and \`$OUT_DIR/docgen-ai-tasks.md\` for missing-doc work.
4. Compare \`$OUT_DIR/docgen.md\` or \`$OUT_DIR/index.html\` against source behavior before committing public docs.
5. Re-run with \`DOCGEN_STRICT=1\` only when the user wants enforcement.

## Guardrails

- Treat DocsGen output as scan evidence, not invented behavior.
- Do not publish, deploy, or commit generated docs without explicit user approval.
- Keep run packets local unless the user asks for an artifact handoff.
EOF

cat > "$RUN_DIR/SUMMARY.md" <<EOF
# DocsGen Repo Contract Runner Summary

Run: $STAMP

## Verdict

$VERDICT

## Content Pillar

Documentation generation should produce local, inspectable contracts before docs are refreshed, committed, or published.

## Target

- Mode: \`$TARGET_MODE\`
- Path: \`$TARGET_PATH\`
- Strict mode: \`${DOCGEN_STRICT:-0}\`
- Public only: \`$DOCGEN_PUBLIC_ONLY\`
- Format: \`$DOCGEN_FORMAT\`

## Key Artifacts

- Generated docs: \`$OUT_DIR\`
- CLI JSON: \`$LOG_DIR/docgen-cli.json\`
- stderr: \`$LOG_DIR/docgen.stderr\`
- Command: \`$LOG_DIR/docgen-command.txt\`
- Agent handoff: \`$ARTIFACT_DIR/agent-handoff.md\`
- Status: \`$RUN_DIR/status.tsv\`

## Buyer Relevance

- Developers: repeatable docs generation and gap discovery for any local repo.
- Agents: stable JSON, gap, and AI-task files for bounded follow-up work.
- Agencies and enterprise teams: local review packet before public docs refreshes or CI gate enforcement.
EOF

echo "Workflow complete: $RUN_DIR"
exit "$DOCGEN_STATUS"
