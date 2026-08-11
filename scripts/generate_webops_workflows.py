#!/usr/bin/env python3
"""Generate the ten reviewed WebOps workflow kit manifests and wrappers."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ROWS=[
{"id":"webops-site-bootstrap","purpose":"Establish a credential-free initial website, repository, content-graph, browser, and reporting baseline.","permission":"OBSERVE","agents":["Site Profile","Capability Preflight","SiteProbe","Scout","ContentGraph","RAG","Site QA Operator","WebOps Reporter"],"tools":["siteprobe","scout","contentgraph","rag","lens","runledger"],"skills":["webops-site-profile","webops-capability-preflight","kujo-siteprobe-workflows","kujo-scout-workflows","kujo-contentgraph-workflows","kujo-rag-workflows","kujo-lens-workflows","webops-reporting"],"credentials":[],"approval":["Repository access is read-only; authenticated browser state is optional and external."],"readiness":"production-capable-with-limitations"},
{"id":"webops-weekly-site-health","purpose":"Compare weekly crawl and rendered site health, links, performance, accessibility, schema, and metadata.","permission":"OBSERVE","agents":["SiteProbe","Site QA Operator","Link Health Auditor","Performance Analyst","Accessibility Auditor","Schema Auditor","Metadata Auditor","WebOps Reporter"],"tools":["siteprobe","lens","searchbridge","runledger"],"skills":["kujo-siteprobe-workflows","kujo-lens-workflows","webops-link-health","webops-web-performance","webops-accessibility-review","webops-schema-and-metadata","webops-reporting"],"credentials":[],"approval":["No site mutation; optional provider credentials enable performance modules only."],"readiness":"production-capable-with-limitations"},
{"id":"webops-weekly-search-intelligence","purpose":"Compare measured search evidence, keyword opportunities, and decay signals with capability-level degradation.","permission":"OBSERVE","agents":["SearchBridge","Search Performance Analyst","Keyword Opportunity Analyst","Content Decay Analyst","WebOps Reporter"],"tools":["searchbridge","contentgraph","runledger"],"skills":["kujo-searchbridge-workflows","webops-search-performance","webops-keyword-opportunity","webops-content-decay","webops-reporting"],"credentials":["Optional Search Console, keyword, and analytics environment credentials for live mode."],"approval":["Provider cost and property access; fixture mode is credential-free."],"readiness":"production-capable-with-limitations"},
{"id":"webops-weekly-content-intelligence","purpose":"Combine trends, query opportunity, content relationships, gaps, accuracy, and internal-link proposals.","permission":"PROPOSE","agents":["Trend Scout","Keyword Opportunity Analyst","ContentGraph","Content Gap Analyst","Content Accuracy Reviewer","Internal Link Specialist","WebOps Reporter"],"tools":["contentgraph","searchbridge","rag","siteprobe","runledger"],"skills":["webops-search-standards-watch","webops-keyword-opportunity","kujo-contentgraph-workflows","webops-content-gap","webops-content-accuracy","webops-internal-linking","webops-reporting"],"credentials":["Optional search and keyword provider credentials."],"approval":["Internal-link source changes require a separate ACT run."],"readiness":"production-capable-with-limitations"},
{"id":"webops-post-publish","purpose":"Verify newly published content, relationships, rendered quality, optional submission, distribution assets, and receipts.","permission":"PROPOSE","agents":["SiteProbe","Metadata Auditor","Schema Auditor","Internal Link Specialist","Site QA Operator","Search Submission Operator","Distribution Operator","WebOps Reporter"],"tools":["siteprobe","contentgraph","lens","eval","searchbridge","howl","runledger"],"skills":["kujo-siteprobe-workflows","webops-schema-and-metadata","webops-internal-linking","kujo-lens-workflows","kujo-eval-workflows","webops-search-submission","webops-distribution","webops-reporting"],"credentials":["Optional submission and distribution credentials for explicit ACT mode."],"approval":["Search submission and distribution publishing require explicit ACT; fixture mode creates receipts/assets only."],"readiness":"production-capable-with-limitations"},
{"id":"webops-content-refresh","purpose":"Turn decay and accuracy evidence into a Spec, approved update boundary, verification, and future measurement cue.","permission":"PROPOSE","agents":["Content Decay Analyst","Content Accuracy Reviewer","Search Performance Analyst","ContentGraph","Spec","Authorized Content Update","Eval","Site QA Operator","Search Submission Operator","WebOps Reporter"],"tools":["searchbridge","contentgraph","spec","eval","lens","runledger"],"skills":["webops-content-decay","webops-content-accuracy","webops-search-performance","kujo-contentgraph-workflows","kujo-spec-workflows","kujo-eval-workflows","kujo-lens-workflows","webops-search-submission","webops-reporting"],"credentials":["Optional measurement/submission providers."],"approval":["Content mutation and submission pause for separate role-bounded ACT approval."],"readiness":"production-capable-with-limitations"},
{"id":"webops-monthly-seo-review","purpose":"Synthesize monthly specialist SEO evidence without duplicating specialist analysis.","permission":"OBSERVE","agents":["SEO Auditor","Search Performance Analyst","Indexation Analyst","Technical SEO Auditor","Content Decay Analyst","Cannibalization Analyst","Internal Link Specialist","Schema Auditor","Metadata Auditor","Performance Analyst","Backlink & Mention Analyst","WebOps Reporter"],"tools":["siteprobe","searchbridge","contentgraph","lens","runledger"],"skills":["webops-technical-seo","webops-search-performance","webops-indexation","webops-content-decay","webops-cannibalization","webops-internal-linking","webops-schema-and-metadata","webops-web-performance","webops-backlink-and-mention-analysis","webops-reporting"],"credentials":["Optional search, analytics, backlink, and performance providers."],"approval":["Synthesis is OBSERVE; proposed fixes route to finding-to-fix."],"readiness":"production-capable-with-limitations"},
{"id":"webops-quarterly-content-portfolio","purpose":"Classify the content portfolio from graph, search, analytics, decay, pruning, and information-architecture evidence.","permission":"PROPOSE","agents":["ContentGraph","Search Performance Analyst","Analytics Analyst","Content Decay Analyst","Content Portfolio Manager","Content Pruning Analyst","Information Architecture Auditor","WebOps Reporter"],"tools":["contentgraph","searchbridge","siteprobe","runledger"],"skills":["kujo-contentgraph-workflows","webops-search-performance","webops-analytics-analysis","webops-content-decay","webops-content-portfolio","webops-content-pruning","webops-information-architecture","webops-reporting"],"credentials":["Search and analytics providers are optional; their modules degrade independently."],"approval":["Merge, redirect, retire, or URL changes require separate ACT and migration approval."],"readiness":"production-capable-with-limitations"},
{"id":"webops-ai-visibility-benchmark","purpose":"Run a fixed longitudinal query suite across explicitly available AI/search surfaces without fabricated availability.","permission":"OBSERVE","agents":["Capability Preflight","AI Search Visibility Analyst","WebOps Reporter"],"tools":["searchbridge","runledger","casefile"],"skills":["webops-capability-preflight","webops-ai-search-visibility","webops-longitudinal-findings","webops-reporting"],"credentials":["Surface/provider credentials are optional and explicit; fixture surfaces require none."],"approval":["Live provider cost and terms; unavailable surfaces are skipped."],"readiness":"experimental"},
{"id":"webops-finding-to-fix","purpose":"Move one stable WebOps finding through Spec, proposal, approval, implementation boundary, Eval, Lens, SiteProbe, and receipt evidence.","permission":"PROPOSE","agents":["WebOps Finding","Spec","Proposal","Approval Gate","Implementation","Eval","Site QA Operator","SiteProbe","WebOps Reporter"],"tools":["spec","eval","lens","siteprobe","runledger","casefile","patchbrief","changebucket"],"skills":["webops-longitudinal-findings","kujo-spec-workflows","kujo-eval-workflows","kujo-lens-workflows","kujo-siteprobe-workflows","kujo-runledger-workflows","kujo-casefile-workflows","kujo-patchbrief-workflows","kujo-changebucket-workflows"],"credentials":[],"approval":["Implementation and any production mutation require explicit role-bounded ACT; fixture mode produces proposal and proof plan."],"readiness":"production-capable-with-limitations"},
]

def main():
    for row in ROWS:
        folder=ROOT/row["id"]; (folder/"scripts").mkdir(parents=True,exist_ok=True)
        manifest={"schema":"webops.workflow/v1","id":row["id"],"version":"0.1.0","purpose":row["purpose"],"default_permission":row["permission"],"fixture_mode":True,"live_mode":True,"agents":row["agents"],"tools":row["tools"],"skills":row["skills"],"credentials":row["credentials"],"approval_boundaries":row["approval"],"state_and_recovery":"state.json records every step; rerun with --resume continues after completed steps.","outputs":["state.json","capabilities.json","steps/*.json","findings.json","report.md","run-receipt.json"],"readiness":row["readiness"]}
        (folder/"workflow.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
        (folder/"scripts/run.sh").write_text('''#!/usr/bin/env bash
set -euo pipefail
WORKFLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$WORKFLOW_DIR/.." && pwd)"
exec python3 "$ROOT/scripts/webops_workflow.py" --workflow "$(basename "$WORKFLOW_DIR")" "$@"
''',encoding="utf-8")
        agent_sequence=" → ".join(row["agents"])
        (folder/"README.md").write_text(f'''# {row["id"]}

{row["purpose"]}

## Sequence

`{agent_sequence}`

## Run fixture mode

```bash
(cd {row["id"]} && bash scripts/run.sh --fixture)
```

Use `--site-profile ../fixtures/webops/site-profile.fixture.json`, `--out`,
`--permission OBSERVE|PROPOSE|ACT`, and `--resume` as needed. Fixture mode is
offline, deterministic, and never requires paid credentials. Live mode uses
the same profile and capability preflight but never expands authority.

## Evidence and recovery

The run packet contains state, capability receipt, step receipts, stable
findings, quiet report, and run receipt. Completed steps are resumable. A
missing optional capability records `skipped-degraded`; an ACT boundary records
`approval-required` rather than pretending the action occurred.

## Approval boundary

{row["approval"][0]}

Current readiness: **{row["readiness"]}**. Live provider, authenticated browser,
and production mutation evidence remain environment-specific.
''',encoding="utf-8")
    print(f"Generated {len(ROWS)} WebOps workflow kits")

if __name__=="__main__": main()
