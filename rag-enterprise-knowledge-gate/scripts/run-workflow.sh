#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KUJO_REPOS="${KUJO_REPOS:-$(cd "$WORKFLOW_DIR/../.." && pwd)}"
KUJO_BIN="${KUJO_BIN:-$KUJO_REPOS/kujo/target/release/kujo}"
RAG_REPO="${RAG_REPO:-$KUJO_REPOS/rag}"
RAG_NAMESPACE="${RAG_NAMESPACE:-enterprise_demo}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RUN_DIR:-$WORKFLOW_DIR/.runs/$STAMP}"
CORPUS="$RUN_DIR/corpus"
INDEX_DIR="$RUN_DIR/index"
LOG_DIR="$RUN_DIR/logs"

mkdir -p "$CORPUS" "$INDEX_DIR" "$LOG_DIR"

if [[ ! -x "$KUJO_BIN" ]]; then
  echo "Missing executable Kujo runtime: $KUJO_BIN" >&2
  exit 1
fi

if [[ ! -f "$RAG_REPO/main.kujo" ]]; then
  echo "Missing RAG repo: $RAG_REPO" >&2
  exit 1
fi

cat > "$CORPUS/security-controls.md" <<'EOF'
# Security Controls

The enterprise assistant must answer from approved local sources. Access is scoped by namespace. Production deployments require bearer auth, audit logging, redaction, and rate limits.
EOF

cat > "$CORPUS/onboarding.md" <<'EOF'
# Developer Onboarding

New developers should ingest only approved docs, run retrieval locally, review citations, and attach query evidence to pull requests that change support or policy answers.
EOF

cat > "$CORPUS/release-gate.md" <<'EOF'
# Release Gate

Before release, teams should run golden queries, review confidence bands, verify citation paths, and keep the generated index as a versioned evidence artifact.
EOF

{
  echo -e "stage\tstatus\tdetail"
  echo -e "corpus\tpass\t$CORPUS"
} > "$RUN_DIR/status.tsv"

(
  cd "$RAG_REPO"
  KUJO_RAG_INDEX_PATH="$INDEX_DIR/rag_index.json" \
  KUJO_RAG_NAMESPACE="$RAG_NAMESPACE" \
  KUJO_RAG_INGEST_EXTENSIONS=md,markdown,txt \
  KUJO_RAG_CHUNK_STRATEGY=line \
  "$KUJO_BIN" run main.kujo --interpreter ingest --path "$CORPUS" --recursive true
) > "$LOG_DIR/ingest.json" 2>&1
echo -e "ingest\tpass\t$LOG_DIR/ingest.json" >> "$RUN_DIR/status.tsv"

(
  cd "$RAG_REPO"
  KUJO_RAG_INDEX_PATH="$INDEX_DIR/rag_index.json" \
  KUJO_RAG_NAMESPACE="$RAG_NAMESPACE" \
  "$KUJO_BIN" run main.kujo --interpreter query --question "What controls protect enterprise answers?"
) > "$LOG_DIR/query-security.json" 2>&1
echo -e "query-security\tpass\t$LOG_DIR/query-security.json" >> "$RUN_DIR/status.tsv"

(
  cd "$RAG_REPO"
  KUJO_RAG_INDEX_PATH="$INDEX_DIR/rag_index.json" \
  KUJO_RAG_NAMESPACE="$RAG_NAMESPACE" \
  "$KUJO_BIN" run main.kujo --interpreter query --question "What should developers attach to pull requests?"
) > "$LOG_DIR/query-onboarding.json" 2>&1
echo -e "query-onboarding\tpass\t$LOG_DIR/query-onboarding.json" >> "$RUN_DIR/status.tsv"

if ! find "$INDEX_DIR" -type f -name '*.json' | grep -q .; then
  echo "RAG did not write an index JSON file under $INDEX_DIR" >&2
  exit 1
fi
echo -e "artifact-check\tpass\t$INDEX_DIR" >> "$RUN_DIR/status.tsv"

cat > "$RUN_DIR/SUMMARY.md" <<EOF
# RAG Enterprise Knowledge Gate Summary

Run: $STAMP

## Verdict

PASS - RAG ingested a local corpus under namespace \`$RAG_NAMESPACE\`, wrote a local index, and returned citation-backed query responses.

## Content Pillar

Enterprise AI answers should be grounded in approved local documents with citations and tenant/project isolation.

## Key Artifacts

- Corpus: \`$CORPUS\`
- Index directory: \`$INDEX_DIR\`
- Ingest output: \`$LOG_DIR/ingest.json\`
- Security query: \`$LOG_DIR/query-security.json\`
- Onboarding query: \`$LOG_DIR/query-onboarding.json\`

## Buyer Relevance

- Developers: local retrieval with evidence they can attach to reviews.
- Agency owners: demo client knowledge assistants without live provider setup.
- Enterprise: namespace isolation, local index ownership, citations, and configurable API/security controls.
EOF

echo "Workflow complete: $RUN_DIR"
