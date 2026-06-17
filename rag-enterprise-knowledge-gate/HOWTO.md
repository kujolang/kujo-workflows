# RAG Enterprise Knowledge Gate HOWTO

## 1. Run The Demo

```bash
cd rag-enterprise-knowledge-gate
bash scripts/run-workflow.sh
```

Override the namespace or question set:

```bash
RAG_NAMESPACE=client_alpha bash scripts/run-workflow.sh
```

## 2. Review The Output

Open:

```text
.runs/<timestamp>/SUMMARY.md
.runs/<timestamp>/corpus/
.runs/<timestamp>/index/
.runs/<timestamp>/logs/ingest.json
.runs/<timestamp>/logs/query-security.json
.runs/<timestamp>/logs/query-onboarding.json
```

The query logs are JSON responses that include answer text and citation metadata.

## 3. Use A Real Corpus

Use the underlying command shape:

```bash
cd /Users/robertdevore/2026/Kujolang/kujo-repos/rag
KUJO_RAG_INDEX_PATH=/tmp/client-index/rag_index.json \
KUJO_RAG_NAMESPACE=client_alpha \
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo/target/release/kujo run main.kujo --interpreter ingest \
  --path /path/to/docs \
  --recursive true
```

Query it:

```bash
KUJO_RAG_INDEX_PATH=/tmp/client-index/rag_index.json \
KUJO_RAG_NAMESPACE=client_alpha \
/Users/robertdevore/2026/Kujolang/kujo-repos/kujo/target/release/kujo run main.kujo --interpreter query \
  --question "What approval controls apply?"
```

## 4. Content Notes

The best demo artifact is a query response with citations pointing at files in the local corpus. It shows the practical difference between grounded retrieval and generic AI answers.

## 5. Troubleshooting

If results are weak, add more explicit terms to the corpus or query. This demo uses offline hash embeddings, so clear source phrasing is useful.

