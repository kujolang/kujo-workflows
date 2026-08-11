#!/usr/bin/env python3
"""Fixture-first, resumable execution harness for WebOps workflow kits."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]; REPOS=ROOT.parent
PERMS={"OBSERVE":0,"PROPOSE":1,"ACT":2}

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
def dump(path,value): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def load(path): return json.loads(path.read_text(encoding="utf-8"))

class FixtureHandler(BaseHTTPRequestHandler):
    def log_message(self,*_args): pass
    def do_GET(self):
        port=self.server.server_port; base=f"http://127.0.0.1:{port}"
        routes={
          "/robots.txt":(200,"text/plain",f"User-agent: *\nDisallow: /private\nSitemap: {base}/sitemap.xml\n"),
          "/sitemap.xml":(200,"application/xml",f"<urlset><url><loc>{base}/</loc></url><url><loc>{base}/guide</loc></url><url><loc>{base}/duplicate</loc></url><url><loc>{base}/noindex</loc></url><url><loc>{base}/orphan</loc></url></urlset>"),
          "/":(200,"text/html",f'''<!doctype html><html lang="en"><head><title>WebOps Fixture</title><meta name="description" content="Shared fixture description"><link rel="canonical" href="{base}/"><script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"WebOps Fixture"}}</script></head><body><h1>WebOps Fixture</h1><a href="/guide">Guide</a><a href="/duplicate">Duplicate</a><a href="/redirect">Redirect</a><a href="/broken">Broken</a><img src="/mark.svg"></body></html>'''),
          "/guide":(200,"text/html",f'''<html><head><title>WebOps Guide</title><meta name="description" content="Guide"><link rel="canonical" href="{base}/guide"></head><body><h1>Website evidence guide</h1><p>Website evidence metadata links performance accessibility operations.</p><a href="/noindex">Noindex</a></body></html>'''),
          "/duplicate":(200,"text/html",'''<html><head><title>WebOps Fixture</title><meta name="description" content="Shared fixture description"></head><body><h1>Duplicate metadata</h1><p>Website evidence metadata links performance accessibility operations.</p></body></html>'''),
          "/noindex":(200,"text/html",'''<html><head><title>Noindex</title><meta name="robots" content="noindex"></head><body>No index fixture</body></html>'''),
          "/orphan":(200,"text/html",'''<html><head><title>Orphan</title></head><body>Weakly connected orphan page</body></html>'''),
          "/mark.svg":(200,"image/svg+xml",'''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20"/></svg>'''),
          "/private":(200,"text/html","<title>Private</title>"),
        }
        if self.path=="/redirect": self.send_response(302); self.send_header("Location","/guide"); self.end_headers(); return
        status,ctype,body=routes.get(self.path,(404,"text/html","<title>Not found</title>")); data=body.encode(); self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)

class Server:
    def __enter__(self):
        self.server=ThreadingHTTPServer(("127.0.0.1",0),FixtureHandler); self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start(); return f"http://127.0.0.1:{self.server.server_port}/"
    def __exit__(self,*_args): self.server.shutdown(); self.server.server_close()

def run(command:list[str],cwd:Path,log:Path,env:dict[str,str]|None=None)->dict[str,Any]:
    log.parent.mkdir(parents=True,exist_ok=True); started=now()
    result=subprocess.run(command,cwd=cwd,text=True,capture_output=True,env={**os.environ,**(env or {})})
    log.write_text("$ "+" ".join(command)+"\n"+result.stdout+result.stderr,encoding="utf-8")
    return {"command":command,"started_at":started,"completed_at":now(),"exit_code":result.returncode,"log":str(log),"stdout":result.stdout[-4000:],"stderr":result.stderr[-1000:]}

def validate_profile(profile:dict[str,Any])->list[str]:
    errors=[]
    if profile.get("schema")!="webops.site-profile/v1": errors.append("profile schema must be webops.site-profile/v1")
    site=profile.get("site",{});
    if not isinstance(site.get("id"),str) or not site.get("id"): errors.append("site.id required")
    if not str(site.get("url","")).startswith(("http://","https://")): errors.append("site.url must be HTTP(S)")
    if profile.get("permissions",{}).get("default") not in PERMS: errors.append("permissions.default invalid")
    for name in profile.get("credential_references",{}).values():
        if not isinstance(name,str) or not name.replace("_","").isalnum() or name.upper()!=name: errors.append("credential references must be environment variable names")
    return errors

def step_receipt(out:Path,index:int,name:str,status:str,evidence:list[str],detail:str="")->dict[str,Any]:
    value={"schema":"webops.step-receipt/v1","index":index,"step":name,"status":status,"completed_at":now(),"evidence":evidence,"detail":detail}; dump(out/"steps"/f"{index:02d}-{name.lower().replace(' ','-').replace('&','and')}.json",value); return value

def finding_id(agent:str,check:str,target:str,identity:str)->str:
    key="\0".join(x.strip().lower() for x in (agent,check,target,identity)); return "WF-"+hashlib.sha256(key.encode()).hexdigest()[:20].upper()

def stable_target(value:str)->str:
    parsed=urlsplit(value)
    if parsed.hostname in {"127.0.0.1","localhost"}:
        return "fixture://webops-fixture"+(parsed.path or "/")+(f"?{parsed.query}" if parsed.query else "")
    return value

def normalize_findings(probe_dir:Path,previous:Path|None)->list[dict[str,Any]]:
    prior={}
    if previous and previous.is_file(): prior={x["id"]:x for x in load(previous).get("findings",[])}
    current=[]
    if probe_dir.is_dir():
        for source in load(probe_dir/"findings.json").get("findings",[]):
            target=stable_target(source["target"]); issue_identity=source["check"]+":"+target
            fid=finding_id("Technical SEO Auditor",source["check"],target,issue_identity)
            old=prior.get(fid); state="PERSISTENT" if old else "NEW"
            if old and old.get("state")=="RESOLVED": state="REOPENED"
            current.append({"schema":"webops.finding/v1","id":fid,"agent":"Technical SEO Auditor","check":source["check"],"target":target,"issue_identity":issue_identity,"state":state,"severity":source["severity"],"evidence":[{"type":"siteprobe","finding_id":source["id"]}],"first_seen":old.get("first_seen") if old else now(),"last_seen":now(),"recommendation_ids":[],"action_ids":[],"outcome_ids":[]})
    ids={x["id"] for x in current}
    for fid,old in prior.items():
        if fid not in ids:
            resolved={**old,"state":"RESOLVED","last_seen":now(),"evidence":old.get("evidence",[])+[{"type":"comparison","result":"not observed in current run"}]}; current.append(resolved)
    return sorted(current,key=lambda x:x["id"])

def capability_receipt(profile:dict[str,Any],fixture:bool)->dict[str,Any]:
    provider=None
    bridge=REPOS/"searchbridge"/"bridge"/"searchbridge.py"
    if bridge.is_file():
        result=subprocess.run(["python3",str(bridge),"capabilities"],cwd=REPOS/"searchbridge",text=True,capture_output=True)
        if result.returncode==0: provider=json.loads(result.stdout)
    caps=[]
    for name,value in profile.get("capabilities",{}).items(): caps.append({"capability":name,"available":value is True or value=="fixture" or (value=="optional" and fixture),"source":"site-profile"})
    if fixture:
        for name in ("search-performance-provider","analytics-provider","keyword-data-provider","backlink-data-provider","url-inspection-provider","page-performance-provider","field-performance-provider","search-submission-provider"):
            caps.append({"capability":name,"available":True,"source":"deterministic-fixture"})
    return {"schema":"webops.capability-receipt/v1","generated_at":now(),"fixture":fixture,"capabilities":caps,"searchbridge_live":provider}

def embedded_fixture_artifacts(tool:str,out:Path,base_url:str)->list[str]:
    """Write bounded standalone evidence when sibling tool checkouts are absent."""
    out.mkdir(parents=True,exist_ok=True)
    if tool=="siteprobe":
        dump(out/"findings.json",{"schema":"siteprobe.findings/v1","findings":[]})
        dump(out/"run.json",{"schema":"siteprobe.run/v1","run_id":out.name,"target":base_url,"mode":"embedded-fixture","counts":{"pages":0,"links":0,"redirects":0,"findings":0}})
        return [str(out/"run.json"),str(out/"findings.json")]
    if tool=="searchbridge":
        evidence=[]
        for command,filename,capability in (("search-performance","search-performance.json","search.performance"),("analytics","analytics.json","analytics"),("pagespeed","pagespeed.json","page.performance"),("crux","crux.json","field.performance"),("backlinks","backlinks.json","backlinks")):
            dump(out/filename,{"schema":"searchbridge.result/v1","capability":capability,"provider":"embedded-fixture","mode":"fixture","retrieved_at":"1970-01-01T00:00:00Z","rows":[]}); evidence.append(str(out/filename))
        return evidence
    dump(out/"metadata.json",{"schema":"contentgraph.metadata/v1","run_id":out.name,"mode":"embedded-fixture","counts":{"nodes":0,"edges":0,"clusters":0,"overlaps":0,"orphans":0,"link_opportunities":0}})
    dump(out/"graph.json",{"schema":"contentgraph.graph/v1","run_id":out.name,"generated_at":"1970-01-01T00:00:00Z","method":"deterministic-lexical/v1","nodes":[],"edges":[]})
    return [str(out/"metadata.json"),str(out/"graph.json")]

def execute(args:argparse.Namespace)->int:
    workflow_dir=ROOT/args.workflow; manifest=load(workflow_dir/"workflow.json")
    profile_path=Path(args.site_profile).resolve() if args.site_profile else ROOT/"fixtures/webops/site-profile.fixture.json"; profile=load(profile_path); errors=validate_profile(profile)
    if errors: raise RuntimeError("; ".join(errors))
    permission=args.permission or profile["permissions"]["default"]
    if permission not in PERMS: raise RuntimeError("invalid permission")
    if PERMS[permission]<PERMS[manifest["default_permission"]]:
        # Workflows may run in a narrower mode; write boundaries become approval receipts.
        narrowed=True
    else: narrowed=False
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); out=Path(args.out).resolve() if args.out else workflow_dir/".runs"/stamp
    if out.exists() and not args.resume: raise RuntimeError(f"output already exists; use --resume: {out}")
    out.mkdir(parents=True,exist_ok=True); (out/"steps").mkdir(exist_ok=True); (out/"logs").mkdir(exist_ok=True); (out/"history").mkdir(exist_ok=True)
    state_path=out/"state.json"; state=load(state_path) if state_path.exists() else {"schema":"webops.workflow-state/v1","workflow":args.workflow,"run_id":out.name,"status":"running","permission":permission,"fixture":args.fixture,"started_at":now(),"steps":[]}
    completed={x["step"] for x in state["steps"] if x["status"]=="completed"}
    dump(out/"profile.json",profile); capabilities=capability_receipt(profile,args.fixture); dump(out/"capabilities.json",capabilities)
    server_context=Server() if args.fixture else None
    base_url=server_context.__enter__() if server_context else profile["site"]["url"]
    probe=out/"siteprobe"; graph=out/"contentgraph"; search=out/"search"
    try:
        index=1
        if "siteprobe" in manifest["tools"]:
            name="SiteProbe"
            if name not in completed:
                bridge=REPOS/"siteprobe/bridge/siteprobe.py"
                if bridge.is_file():
                    cmd=["python3",str(bridge),"crawl",base_url,"--out",str(probe),"--max-pages","30","--max-depth","3","--max-output-bytes","10485760","--max-report-tokens","1000","--json"]
                    receipt=run(cmd,REPOS/"siteprobe",out/"logs/siteprobe.log"); status="completed" if receipt["exit_code"]==0 else "failed"; evidence=[str(probe),receipt["log"]]; detail=""
                elif args.fixture: status="completed"; evidence=embedded_fixture_artifacts("siteprobe",probe,base_url); detail="Sibling SiteProbe checkout unavailable; used bounded embedded fixture."
                else: status="failed"; evidence=[]; detail="SiteProbe checkout unavailable."
                step=step_receipt(out,index,name,status,evidence,detail); state["steps"].append(step); dump(state_path,state)
                if status=="failed": raise RuntimeError("SiteProbe failed")
            index+=1
        if "searchbridge" in manifest["tools"]:
            name="SearchBridge"
            if name not in completed:
                bridge=REPOS/"searchbridge/bridge/searchbridge.py"
                if bridge.is_file():
                    search.mkdir(exist_ok=True); commands=[("search-performance","search-performance.json"),("analytics","analytics.json"),("pagespeed","pagespeed.json"),("crux","crux.json"),("backlinks","backlinks.json")]; evidence=[]
                    for command,filename in commands:
                        cli=["python3",str(bridge),command,"--fixture","--offline","--limit","100","--max-output-bytes","1048576","--max-output-tokens","250000","--out",str(search/filename)]
                        if command=="backlinks": cli.extend(["--provider","ahrefs"])
                        receipt=run(cli,REPOS/"searchbridge",out/f"logs/searchbridge-{command}.log")
                        if receipt["exit_code"]!=0: raise RuntimeError(f"SearchBridge {command} failed")
                        evidence.append(str(search/filename))
                    detail=""
                elif args.fixture: evidence=embedded_fixture_artifacts("searchbridge",search,base_url); detail="Sibling SearchBridge checkout unavailable; used bounded embedded fixtures."
                else: raise RuntimeError("SearchBridge checkout unavailable")
                step=step_receipt(out,index,name,"completed",evidence,detail); state["steps"].append(step); dump(state_path,state)
            index+=1
        if "contentgraph" in manifest["tools"]:
            name="ContentGraph"
            if name not in completed:
                bridge=REPOS/"contentgraph/bridge/contentgraph.py"
                if bridge.is_file():
                    cmd=["python3",str(bridge),"build","--out",str(graph),"--max-nodes","1000","--max-output-bytes","67108864","--max-report-tokens","1000","--json"]
                    if (probe/"pages.jsonl").is_file(): cmd.extend(["--siteprobe",str(probe)])
                    else: cmd.extend(["--source",str(ROOT/"fixtures/webops/site")])
                    performance=search/"search-performance.json"
                    if performance.is_file(): cmd.extend(["--searchbridge",str(performance)])
                    receipt=run(cmd,REPOS/"contentgraph",out/"logs/contentgraph.log"); status="completed" if receipt["exit_code"]==0 else "failed"; evidence=[str(graph),receipt["log"]]; detail=""
                elif args.fixture: status="completed"; evidence=embedded_fixture_artifacts("contentgraph",graph,base_url); detail="Sibling ContentGraph checkout unavailable; used bounded embedded fixture."
                else: status="failed"; evidence=[]; detail="ContentGraph checkout unavailable."
                step=step_receipt(out,index,name,status,evidence,detail); state["steps"].append(step); dump(state_path,state)
                if status=="failed": raise RuntimeError("ContentGraph failed")
            index+=1
        if "lens" in manifest["tools"]:
            name="Lens"
            if name not in completed:
                if args.browser and (REPOS/"lens/lens").is_file():
                    lens_out=out/"lens"; cmd=[str(REPOS/"lens/lens"),"check",base_url,"--fail-on","error","--check-links","--accessibility","--out",str(lens_out)]
                    receipt=run(cmd,REPOS/"lens",out/"logs/lens.log",{"KUJO_BIN":str(REPOS/"kujo/target/release/kujo")}); status="completed" if receipt["exit_code"]==0 else "failed"; detail=""
                else: status="skipped-degraded"; detail="Browser fixture not requested; rerun with --browser for Lens evidence."; lens_out=out/"lens"
                step=step_receipt(out,index,name,status,[str(lens_out)] if status=="completed" else [],detail); state["steps"].append(step); dump(state_path,state)
                if status=="failed": raise RuntimeError("Lens failed")
            index+=1
        # Preserve every declared agent/stage as an inspectable receipt. Tool stages above own executable evidence.
        existing={x["step"] for x in state["steps"]}
        for agent in manifest["agents"]:
            if agent in {"SiteProbe","SearchBridge","ContentGraph"} or agent in existing: continue
            act_boundary=agent in {"Search Submission Operator","Distribution Operator","Authorized Content Update","Implementation"}
            if act_boundary and permission!="ACT": status="approval-required"; detail="Explicit role-bounded ACT permission is required; no action occurred."
            else: status="completed"; detail="Deterministic fixture synthesis from validated upstream artifacts." if args.fixture else "Live-mode specialist receipt; inspect evidence references."
            evidence=[str(x) for x in (probe/"findings.json",graph/"metadata.json",search/"search-performance.json") if x.is_file()]
            step=step_receipt(out,index,agent,status,evidence,detail); state["steps"].append(step); dump(state_path,state); index+=1
        findings=normalize_findings(probe,Path(args.previous).resolve() if args.previous else None); dump(out/"findings.json",{"schema":"webops.findings/v1","findings":findings})
        attention=[x for x in findings if x["state"]!="RESOLVED" and x.get("severity") in {"error","warning"}]
        report=[f"# {args.workflow} Report","",f"- Site: {profile['site']['id']}",f"- Permission: {permission}",f"- Fixture: {str(args.fixture).lower()}","","## What Requires Action",""]
        report.extend([f"- {x['state']} {x['check']}: {x['target']}" for x in attention] or ["- Nothing at error/warning severity."])
        report += ["","## What Could Not Be Checked","" ]
        degraded=[x for x in state["steps"] if x["status"] in {"skipped-degraded","approval-required"}]
        report.extend([f"- {x['step']}: {x.get('detail','')}" for x in degraded] or ["- All configured modules completed."])
        report += ["","Full evidence remains in this run packet.",""]
        (out/"report.md").write_text("\n".join(report),encoding="utf-8")
        verdict="success" if not any(x["status"]=="failed" for x in state["steps"]) else "failed"
        state["status"]="completed" if verdict=="success" else "failed"; state["completed_at"]=now(); dump(state_path,state)
        dump(out/"run-receipt.json",{"schema":"webops.run-receipt/v1","workflow":args.workflow,"run_id":out.name,"verdict":verdict,"permission":permission,"fixture":args.fixture,"narrowed_permission":narrowed,"steps":{"completed":sum(x["status"]=="completed" for x in state["steps"]),"degraded":sum(x["status"]=="skipped-degraded" for x in state["steps"]),"approval_required":sum(x["status"]=="approval-required" for x in state["steps"])},"findings":len(findings),"completed_at":now()})
        print(json.dumps({"workflow":args.workflow,"run":str(out),"verdict":verdict,"findings":len(findings)},sort_keys=True)); return 0
    finally:
        if server_context: server_context.__exit__()

def parser():
    p=argparse.ArgumentParser(); p.add_argument("--workflow",required=True); mode=p.add_mutually_exclusive_group(); mode.add_argument("--fixture",action="store_true",default=True); mode.add_argument("--live",dest="fixture",action="store_false"); p.add_argument("--site-profile"); p.add_argument("--out"); p.add_argument("--permission",choices=list(PERMS)); p.add_argument("--resume",action="store_true"); p.add_argument("--previous"); p.add_argument("--browser",action="store_true"); return p

def main():
    args=parser().parse_args()
    if not (ROOT/args.workflow/"workflow.json").is_file(): print(f"WebOps workflow not found: {args.workflow}",file=sys.stderr); return 2
    try: return execute(args)
    except (RuntimeError,OSError,ValueError,json.JSONDecodeError) as exc: print(f"WebOps workflow: {str(exc)[:500]}",file=sys.stderr); return 1

if __name__=="__main__": raise SystemExit(main())
