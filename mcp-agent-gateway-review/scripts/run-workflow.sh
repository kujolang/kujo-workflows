#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$WORKFLOW_DIR/../.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
MCP_REPO="${MCP_REPO:-$KUJO_REPOS/mcp}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR:-$WORKFLOW_DIR/.runs/$STAMP}"
FIXTURE="$RUN_DIR/fixture/crm-mini-service"
LOG_DIR="$RUN_DIR/logs"

mkdir -p "$FIXTURE/src" "$FIXTURE/docs" "$LOG_DIR"

if [[ ! -x "$KUJO_BIN" ]]; then
  echo "Missing executable Kujo runtime: $KUJO_BIN" >&2
  exit 1
fi

if [[ ! -f "$MCP_REPO/mcp.kujo" ]]; then
  echo "Missing MCP repo: $MCP_REPO" >&2
  exit 1
fi

cat > "$FIXTURE/README.md" <<'EOF'
# CRM Mini Service

Small fixture used to demonstrate a reviewable MCP surface for a project repo.
EOF

cat > "$FIXTURE/src/api.js" <<'EOF'
export function listAccounts(user) {
  if (!user || user.role !== "admin") {
    return { ok: false, error: "forbidden" };
  }
  return { ok: true, accounts: ["acme", "northstar"] };
}
EOF

cat > "$FIXTURE/docs/agent-policy.md" <<'EOF'
# Agent Policy

Agents may read docs and source summaries. They may not run deployments, access secrets, or mutate production data.
EOF

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
  cd "$MCP_REPO"
  "$KUJO_BIN" run mcp.kujo --interpreter make "$FIXTURE" \
    --out "$RUN_DIR/generated-server" \
    --artifacts "$RUN_DIR/artifacts" \
    --no-ai \
    --validate
) > "$LOG_DIR/mcp-make.log" 2>&1
echo -e "mcp-make\tpass\t$LOG_DIR/mcp-make.log" >> "$RUN_DIR/status.tsv"

for required in \
  "$RUN_DIR/generated-server/README.md" \
  "$RUN_DIR/generated-server/mcp.manifest.json" \
  "$RUN_DIR/generated-server/repo-profile.json" \
  "$RUN_DIR/generated-server/src/server.kujo" \
  "$RUN_DIR/artifacts/safety-review.md" \
  "$RUN_DIR/artifacts/validation-report.md" \
  "$RUN_DIR/artifacts/agent-handoff.md"; do
  if [[ ! -f "$required" ]]; then
    echo "Missing expected MCP artifact: $required" >&2
    exit 1
  fi
done
echo -e "artifact-check\tpass\t$RUN_DIR/generated-server" >> "$RUN_DIR/status.tsv"

cat > "$RUN_DIR/SUMMARY.md" <<EOF
# MCP Agent Gateway Review Summary

Run: $STAMP

## Verdict

PASS - MCP generated a repo-specific server scaffold and review packet with validation enabled.

## Content Pillar

Agents should receive constrained, reviewable tool surfaces. This workflow converts a normal repo into an MCP gateway with safety artifacts before anything is exposed.

## Key Artifacts

- Fixture repo: \`$FIXTURE\`
- Generated server: \`$RUN_DIR/generated-server\`
- Manifest: \`$RUN_DIR/generated-server/mcp.manifest.json\`
- Repo profile: \`$RUN_DIR/generated-server/repo-profile.json\`
- Safety review: \`$RUN_DIR/artifacts/safety-review.md\`
- Validation report: \`$RUN_DIR/artifacts/validation-report.md\`
- Log: \`$LOG_DIR/mcp-make.log\`

## Buyer Relevance

- Developers: fast local MCP scaffolding for their repo.
- Agency owners: review packet explains what agents can and cannot do.
- Enterprise: least-privilege surface and explicit safety review before rollout.
EOF

echo "Workflow complete: $RUN_DIR"
