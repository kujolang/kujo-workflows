#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
request="$tmp/request.md"
workspace="$tmp/workspace"
printf '# Product release\n\nCreate a 30-second product demo from supplied first-party assets.\n' > "$request"

KUJO_REPOS="$(cd "$root/.." && pwd)" \
  "$root/videoops-production/bin/run" \
  --workspace "$workspace" \
  --request "$request" \
  --run-id arbitrary-production-test > "$tmp/result.json"

grep -q '"ok": true' "$tmp/result.json"
grep -q '"fixture": false' "$tmp/result.json"
grep -q '"fixture": false' "$workspace/intake/producer-request.json"
grep -q '"run_id": "arbitrary-production-test"' "$workspace/intake/producer-request.json"
grep -q '"state": "INTAKE_READY"' "$workspace/review/project-state.json"
grep -q 'VideoOps Producer' "$workspace/RUN_VIDEOOPS.md"
grep -q 'product demo' "$workspace/intake/original-request.md"

if KUJO_REPOS="$(cd "$root/.." && pwd)" "$root/videoops-production/bin/run" \
  --workspace "$workspace" --request "$request" --run-id duplicate >/dev/null 2>&1; then
  echo "initializer replaced intake without --overwrite" >&2
  exit 1
fi

echo "videoops production initializer passed"
