#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IDS={"webops-site-bootstrap","webops-weekly-site-health","webops-weekly-search-intelligence","webops-weekly-content-intelligence","webops-post-publish","webops-content-refresh","webops-monthly-seo-review","webops-quarterly-content-portfolio","webops-ai-visibility-benchmark","webops-finding-to-fix"}

class WebOpsWorkflowTests(unittest.TestCase):
    def test_manifests_and_offline_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            for workflow in sorted(IDS):
                with self.subTest(workflow=workflow):
                    folder=ROOT/workflow; manifest=json.loads((folder/"workflow.json").read_text())
                    self.assertEqual("webops.workflow/v1",manifest["schema"]); self.assertTrue(manifest["fixture_mode"]); self.assertTrue(manifest["agents"]); self.assertTrue(manifest["skills"])
                    out=Path(tmp)/workflow
                    result=subprocess.run(["bash",str(folder/"scripts/run.sh"),"--fixture","--out",str(out)],cwd=ROOT,text=True,capture_output=True)
                    self.assertEqual(0,result.returncode,result.stderr+result.stdout)
                    receipt=json.loads((out/"run-receipt.json").read_text()); self.assertEqual("success",receipt["verdict"])
                    state=json.loads((out/"state.json").read_text()); self.assertEqual("completed",state["status"]); self.assertTrue(state["steps"])
                    findings=json.loads((out/"findings.json").read_text())["findings"]
                    for finding in findings: self.assertRegex(finding["id"],r"^WF-[A-F0-9]{20}$")
                    self.assertTrue((out/"report.md").is_file())

    def test_resume_and_stable_finding_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=ROOT/"webops-site-bootstrap"; first=Path(tmp)/"first"; second=Path(tmp)/"second"
            for out in (first,second):
                result=subprocess.run(["bash",str(folder/"scripts/run.sh"),"--fixture","--out",str(out)],cwd=ROOT,text=True,capture_output=True); self.assertEqual(0,result.returncode,result.stderr)
            ids1={x["id"] for x in json.loads((first/"findings.json").read_text())["findings"]}; ids2={x["id"] for x in json.loads((second/"findings.json").read_text())["findings"]}; self.assertEqual(ids1,ids2)
            resume=subprocess.run(["bash",str(folder/"scripts/run.sh"),"--fixture","--out",str(first),"--resume"],cwd=ROOT,text=True,capture_output=True); self.assertEqual(0,resume.returncode,resume.stderr)

    def test_live_mode_never_substitutes_search_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path=Path(tmp)
            profile=tmp_path/"profile.json"
            profile.write_text(json.dumps({
                "schema":"webops.site-profile/v1",
                "site":{"id":"local-live","url":"http://127.0.0.1:9"},
                "capabilities":{"website":True},
                "integrations":{},
                "permissions":{"default":"OBSERVE"},
                "credential_references":{},
            }))
            out=tmp_path/"run"
            result=subprocess.run([
                "bash",str(ROOT/"webops-ai-visibility-benchmark/scripts/run.sh"),
                "--live","--site-profile",str(profile),"--out",str(out),
            ],cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(0,result.returncode,result.stderr+result.stdout)
            state=json.loads((out/"state.json").read_text())
            search=next(step for step in state["steps"] if step["step"]=="SearchBridge")
            self.assertEqual("skipped-degraded",search["status"])
            self.assertIn("not fabricated",search["detail"])
            self.assertFalse((out/"search").exists())

if __name__=="__main__": unittest.main(verbosity=2)
