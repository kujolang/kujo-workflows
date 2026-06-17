#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-/Users/robertdevore/2026/Kujolang/kujo-repos}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
HOWL_REPO="${HOWL_REPO:-$KUJO_REPOS/howl}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR:-$WORKFLOW_DIR/.runs/$STAMP}"
SHOWCASE="$RUN_DIR/showcase"
LOG_DIR="$RUN_DIR/logs"

mkdir -p "$SHOWCASE/examples" "$LOG_DIR"

if [[ ! -x "$KUJO_BIN" ]]; then
  echo "Missing executable Kujo runtime: $KUJO_BIN" >&2
  exit 1
fi

if [[ ! -x "$HOWL_REPO/bin/howl" ]]; then
  echo "Missing Howl launcher: $HOWL_REPO/bin/howl" >&2
  exit 1
fi

cat > "$SHOWCASE/examples/agent-handoff.kujo" <<'EOF'
func build_handoff(task, proof_path) {
  return "Task: " + task + "\nProof: " + proof_path
}

print(build_handoff("Verify checkout fix", ".kujo/runs/latest/client/CLIENT_HANDOFF.md"))
EOF

cat > "$SHOWCASE/examples/release-gate.kujo" <<'EOF'
func release_gate(checks_passed, blockers) {
  if checks_passed == true and blockers == 0 {
    return "ship"
  }
  return "hold"
}

print(release_gate(true, 0))
EOF

cat > "$SHOWCASE/howl.json" <<'EOF'
{
  "project": {
    "name": "Kujo Workflow Pillars",
    "tagline": "Local-first control workflows for AI-native software",
    "url": ""
  },
  "theme": {
    "name": "minimal",
    "mode": "light"
  },
  "cards": [
    {
      "id": "agent-handoff",
      "title": "Agent handoff with proof",
      "tagline": "Keep the task, proof path, and review target together.",
      "file": "examples/agent-handoff.kujo",
      "language": "kujo",
      "concepts": ["handoff", "proof", "developer workflow"],
      "expected_output": "Task: Verify checkout fix\\nProof: .kujo/runs/latest/client/CLIENT_HANDOFF.md",
      "caption": "AI-assisted development gets easier to review when every run ends with a proof path.",
      "cta": "Use Kujo workflows to make agent work inspectable."
    },
    {
      "id": "release-gate",
      "title": "Release gate in plain code",
      "tagline": "Make release readiness explicit enough for humans and agents.",
      "file": "examples/release-gate.kujo",
      "language": "kujo",
      "concepts": ["release gate", "shipcheck", "enterprise readiness"],
      "expected_output": "ship",
      "caption": "Release gates should be explicit, local, and reviewable.",
      "cta": "Kujo turns workflow intent into artifacts."
    }
  ]
}
EOF

{
  echo -e "stage\tstatus\tdetail"
  echo -e "showcase\tpass\t$SHOWCASE"
} > "$RUN_DIR/status.tsv"

(
  cd "$SHOWCASE"
  KUJO="$KUJO_BIN" "$HOWL_REPO/bin/howl" validate
) > "$LOG_DIR/validate.log" 2>&1
echo -e "validate\tpass\t$LOG_DIR/validate.log" >> "$RUN_DIR/status.tsv"

(
  cd "$SHOWCASE"
  KUJO="$KUJO_BIN" "$HOWL_REPO/bin/howl" list
) > "$LOG_DIR/list.txt" 2>&1
echo -e "list\tpass\t$LOG_DIR/list.txt" >> "$RUN_DIR/status.tsv"

(
  cd "$SHOWCASE"
  KUJO="$KUJO_BIN" "$HOWL_REPO/bin/howl" render
) > "$LOG_DIR/render.log" 2>&1
echo -e "render\tpass\t$LOG_DIR/render.log" >> "$RUN_DIR/status.tsv"

(
  cd "$SHOWCASE"
  KUJO="$KUJO_BIN" "$HOWL_REPO/bin/howl" caption agent-handoff --platform x
) > "$LOG_DIR/caption-agent-handoff.txt" 2>&1
echo -e "caption\tpass\t$LOG_DIR/caption-agent-handoff.txt" >> "$RUN_DIR/status.tsv"

for required in \
  "$SHOWCASE/dist/howl/index.html" \
  "$SHOWCASE/dist/howl/agent-handoff.md" \
  "$SHOWCASE/dist/howl/agent-handoff.html" \
  "$SHOWCASE/dist/howl/agent-handoff.svg" \
  "$SHOWCASE/dist/howl/release-gate.md" \
  "$SHOWCASE/dist/howl/release-gate.html" \
  "$SHOWCASE/dist/howl/release-gate.svg"; do
  if [[ ! -f "$required" ]]; then
    echo "Missing expected Howl artifact: $required" >&2
    exit 1
  fi
done
echo -e "artifact-check\tpass\t$SHOWCASE/dist/howl" >> "$RUN_DIR/status.tsv"

cat > "$RUN_DIR/SUMMARY.md" <<EOF
# Howl Content Factory Summary

Run: $STAMP

## Verdict

PASS - Howl validated a showcase manifest, rendered Markdown/HTML/SVG/gallery assets, and generated deterministic caption copy.

## Content Pillar

Content should come from real examples and deterministic manifests, so launch assets stay reviewable and do not drift from source material.

## Key Artifacts

- Showcase project: \`$SHOWCASE\`
- Manifest: \`$SHOWCASE/howl.json\`
- Gallery: \`$SHOWCASE/dist/howl/index.html\`
- Card markdown: \`$SHOWCASE/dist/howl/agent-handoff.md\`
- Card SVG: \`$SHOWCASE/dist/howl/agent-handoff.svg\`
- Caption: \`$LOG_DIR/caption-agent-handoff.txt\`

## Buyer Relevance

- Developers: turn copyable examples into shareable proof.
- Agency owners: produce repeatable content packages from actual workflow assets.
- Enterprise: review deterministic content generation with no network or AI calls.
EOF

echo "Workflow complete: $RUN_DIR"
