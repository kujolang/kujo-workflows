#!/usr/bin/env bash
set -euo pipefail

KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KUJO_BIN="${KUJO_BIN:-}"
PROFILE="${PROFILE:-basic}"
PROJECT_NAME="${PROJECT_NAME:-owned-agent-demo}"
OUT_ROOT="${OUT_ROOT:-$KIT_ROOT/.runs}"

if [[ -z "$KUJO_BIN" || ! -x "$KUJO_BIN" ]]; then
  echo "KUJO_BIN must name an executable Kujo binary." >&2
  exit 2
fi
if ! command -v kennel >/dev/null 2>&1; then
  echo "kennel must be available on PATH for pinned dependency installation." >&2
  exit 2
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$OUT_ROOT/$STAMP"
PROJECTS_DIR="$RUN_DIR/projects"
PROJECT_DIR="$PROJECTS_DIR/$PROJECT_NAME"
mkdir -p "$PROJECTS_DIR"

"$KUJO_BIN" agent new "$PROJECT_NAME" \
  --profile "$PROFILE" \
  --dir "$PROJECTS_DIR" \
  --install \
  --no-git \
  --json >"$RUN_DIR/01-new.json"

(
  cd "$PROJECT_DIR"
  "$KUJO_BIN" doctor agent --deep --json >"$RUN_DIR/02-doctor.json"
  "$KUJO_BIN" agent inspect --json >"$RUN_DIR/03-inspect.json"
  "$KUJO_BIN" agent run "Prove the owned Agent Project workflow" --json >"$RUN_DIR/04-run.json"
  "$KUJO_BIN" agent eval --json >"$RUN_DIR/05-eval.json"
)

{
  echo "# Owned Agent Project workflow proof"
  echo
  echo "- Status: pass"
  echo "- Profile: $PROFILE"
  echo "- Project: $PROJECT_DIR"
  echo "- Dependency installation: Kennel pinned manifest"
  echo "- Provider path: deterministic fixture"
  echo "- Evidence: 01-new.json through 05-eval.json"
} >"$RUN_DIR/SUMMARY.md"

echo "$RUN_DIR/SUMMARY.md"
