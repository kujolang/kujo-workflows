#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPOS="$(cd "$ROOT/.." && pwd)"
KUJO_RUNTIME="${KUJO_BIN:-$REPOS/kujo/target/release/kujo}"
export KUJO_BIN="$KUJO_RUNTIME"

bash "$REPOS/siteprobe/scripts/validate.sh"
bash "$REPOS/searchbridge/scripts/validate.sh"
bash "$REPOS/contentgraph/scripts/validate.sh"
python3 "$REPOS/kujo-skills/scripts/validate_skills.py"
python3 "$ROOT/tests/test_webops_workflows.py"
python3 "$ROOT/scripts/validate_catalog.py" --skills-root "$REPOS/kujo-skills" --tools-root "$REPOS" --json
python3 "$REPOS/kujo-agents/scripts/validate_webops.py"
python3 "$ROOT/scripts/validate_webops_cross_repo.py"
python3 "$REPOS/agents.kujolang.ai/tests/test_sync_agent_content.py"
python3 "$REPOS/agents.kujolang.ai/scripts/validate-agent-content.py" "$REPOS/kujo-agents"
(cd "$REPOS/agents.kujolang.ai" && bash scripts/validate-generated-output.sh)

for repo in siteprobe searchbridge contentgraph kujo-agents kujo-skills kujo-workflows agents.kujolang.ai; do
  git -C "$REPOS/$repo" diff --check
done

printf 'Kujo WebOps campaign validation passed.\n'
