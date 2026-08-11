#!/usr/bin/env python3
"""Fail closed on WebOps agent/skill/tool/workflow/site contract drift."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; REPOS=ROOT.parent
AGENTS=REPOS/"kujo-agents/webops/webops-catalog.json"; SKILLS=REPOS/"kujo-skills/skills"
TOOL_MAP={"SiteProbe":"siteprobe","SearchBridge":"searchbridge","ContentGraph":"contentgraph","RAG":"rag","RunLedger":"runledger","CaseFile":"casefile","Lens":"lens","Eval":"eval","Dispatch":"dispatch","Howl":"howl","CMS":"cms","SSG":"ssg"}

def frontmatter_name(path:Path):
    match=re.search(r"^name:\s*([^\n]+)$",path.read_text(),re.M); return match.group(1).strip().strip('"\'') if match else ""

def main():
    errors=[]; catalog=json.loads(AGENTS.read_text()); agent_slugs={x["slug"] for x in catalog["agents"]}
    skill_names={frontmatter_name(x) for x in SKILLS.glob("*/SKILL.md")}
    manifests={p.parent.name:json.loads(p.read_text()) for p in ROOT.glob("webops-*/workflow.json")}
    for agent in catalog["agents"]:
        for skill in agent["existing_kujo_skills"]+agent["webops_domain_skills"]:
            if skill not in skill_names: errors.append(f'{agent["slug"]}: dangling skill {skill}')
        for workflow in agent["recommended_workflows"]:
            if workflow not in manifests: errors.append(f'{agent["slug"]}: dangling workflow {workflow}')
        for tool in agent["primary_tools"]+agent["secondary_tools"]:
            repo=TOOL_MAP.get(tool)
            if not repo or not (REPOS/repo/".git").is_dir(): errors.append(f'{agent["slug"]}: dangling tool {tool}')
    for name,manifest in manifests.items():
        if manifest.get("id")!=name or manifest.get("schema")!="webops.workflow/v1": errors.append(f"{name}: invalid manifest identity")
        for skill in manifest.get("skills",[]):
            if skill not in skill_names: errors.append(f"{name}: dangling skill {skill}")
        for tool in manifest.get("tools",[]):
            if tool not in {x.lower() for x in TOOL_MAP.values()} and not (REPOS/tool/".git").is_dir(): errors.append(f"{name}: dangling tool {tool}")
    site=REPOS/"agents.kujolang.ai"
    if (site/"content/agents").is_dir():
        generated={x.stem for x in (site/"content/agents").glob("*.md") if 'categories: ["WebOps"]' in x.read_text(errors="ignore")}
        if generated and generated!=agent_slugs: errors.append(f"public WebOps source mismatch: missing={sorted(agent_slugs-generated)} extra={sorted(generated-agent_slugs)}")
    if errors:
        print(json.dumps({"valid":False,"errors":errors},indent=2)); return 1
    print(json.dumps({"valid":True,"agents":len(agent_slugs),"skills":len(skill_names),"workflows":len(manifests),"tools":sorted({x for a in catalog["agents"] for x in a["primary_tools"]+a["secondary_tools"]})},indent=2)); return 0

if __name__=="__main__": raise SystemExit(main())
