#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"docs/audit/workflow-catalog.json"

def main():
    data=json.loads(CATALOG.read_text()); existing=[x for x in data["active_workflows"] if not x["id"].startswith("webops-")]
    for folder in sorted(ROOT.glob("webops-*")):
        manifest_path=folder/"workflow.json"
        if not manifest_path.is_file(): continue
        m=json.loads(manifest_path.read_text())
        existing.append({
          "id":m["id"],"path":m["id"],"status":m["readiness"],"purpose":m["purpose"],"entry":f'{m["id"]}/scripts/run.sh',
          "skills":[{"name":name,"path":f"skills/{name}/SKILL.md","compatibility":"compatible"} for name in m["skills"]],
          "tools":m["tools"],"inputs":["WebOps site profile","fixture or live mode","optional previous findings and permission override"],"outputs":m["outputs"],
          "approval_boundaries":m["approval_boundaries"],"state_and_recovery":m["state_and_recovery"],"evidence":"versioned capability, step, finding, report, state, and run receipt artifacts",
          "tests":[f'bash {m["id"]}/scripts/run.sh --fixture',"python3 tests/test_webops_workflows.py"],"documentation":[f'{m["id"]}/README.md',f'{m["id"]}/workflow.json'],"production_readiness":m["readiness"]})
    data["audit_id"]="kujo-workflows-webops-2026-08-11"; data["active_workflows"]=sorted(existing,key=lambda x:x["id"])
    CATALOG.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print(f"Catalog now contains {len(existing)} workflows")

if __name__=="__main__": main()
