#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repos_root="$(dirname "$repo_root")"
kujo_bin="${KUJO_BIN:-$repos_root/kujo/target/release/kujo}"

test -x "$kujo_bin"
test -x "$repos_root/packwrite/bin/packwrite"
test -x "$repos_root/howl/bin/howl"

cd "$repo_root"

for source in \
  lib/videoops/runtime.kujo \
  scripts/videoops_fixture.kujo \
  scripts/validate_videoops.kujo \
  videoops-creative-planning/workflow.kujo \
  videoops-asset-resolution/workflow.kujo \
  videoops-media-generation/workflow.kujo \
  videoops-hyperframes-edit/workflow.kujo \
  videoops-quality-review/workflow.kujo; do
  "$kujo_bin" check "$source"
done

KUJO_BIN="$kujo_bin" "$repos_root/spec/scripts/spec" validate specs/videoops-v1-production.spec.yml --strict
"$kujo_bin" run "$repos_root/eval/main.kujo" lint evals/videoops-stage-gates.json
eval_out="$(mktemp -d /tmp/videoops-eval.XXXXXX)"
"$kujo_bin" run "$repos_root/eval/main.kujo" run evals/videoops-stage-gates.json --output-dir "$eval_out" --json

(cd fixtures/videoops/packwrite && KUJO="$kujo_bin" "$repos_root/packwrite/bin/packwrite" validate)
KUJO="$kujo_bin" "$repos_root/howl/bin/howl" validate --manifest fixtures/videoops/howl/howl.json
howl_out="$(mktemp -d /tmp/videoops-howl.XXXXXX)"
KUJO="$kujo_bin" "$repos_root/howl/bin/howl" render --manifest fixtures/videoops/howl/howl.json --out "$howl_out"

fixture_parent="$(mktemp -d /tmp/videoops-fixture.XXXXXX)"
"$kujo_bin" run scripts/videoops_fixture.kujo --out "$fixture_parent/run"
"$kujo_bin" run scripts/validate_videoops.kujo --proof "$fixture_parent/run/integration-proof.json"

probe_output="$fixture_parent/final-ffprobe.json"
ffprobe -v error \
  -show_entries stream=codec_type,width,height,r_frame_rate \
  -show_entries format=duration \
  -of json "$fixture_parent/run/workspace/output/final.mp4" > "$probe_output"
grep -q '"codec_type": "audio"' "$probe_output"

echo "videoops release gate passed"
