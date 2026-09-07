"""Exercise the Kujo production bridge with a non-network runtime stub."""
import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MediaBridgeTests(unittest.TestCase):
    def test_default_discovers_agents_tools_without_standalone_repo(self):
        kujo = os.environ.get("KUJO_BIN")
        if not kujo:
            self.skipTest("set KUJO_BIN to exercise native bridge")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workflows = root / "kujo-workflows"
            shutil.copytree(ROOT / "videoops-media-generation", workflows / "videoops-media-generation")
            shutil.copytree(ROOT / "lib", workflows / "lib")
            agents = root / "kujo-agents"
            runtime = agents / "videoops/tools"
            (runtime / "videoops").mkdir(parents=True)
            (runtime / "videoops/__init__.py").write_text("")
            (runtime / "videoops/cli.py").write_text(
                "import json,os\nprint(json.dumps({'runtime':os.getcwd()}))\n")
            request = root / "request.json"
            request.write_text('{}')
            command = [str(workflows / "videoops-media-generation/bin/run"), "--media",
                       "--operation", "import", "--workspace", str(root / "production"),
                       "--request", str(request)]
            env = dict(os.environ, KUJO_BIN=kujo)
            result = subprocess.run(command, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(json.loads(result.stdout)['runtime']).resolve(), runtime.resolve())
            self.assertFalse((root / "kujo-videoops").exists())
            moved = root / "custom-agents"
            agents.rename(moved)
            result = subprocess.run(command, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            result = subprocess.run(command + ["--agents-root", str(moved)], env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(json.loads(result.stdout)['runtime']).resolve(), (moved / "videoops/tools").resolve())

    def test_dispatch_and_fixture_separation(self):
        kujo = os.environ.get("KUJO_BIN")
        if not kujo:
            self.skipTest("set KUJO_BIN to exercise native bridge")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = root / "runtime"
            (runtime / "videoops").mkdir(parents=True)
            (runtime / "videoops" / "__init__.py").write_text("")
            (runtime / "videoops" / "cli.py").write_text(
                "import json,sys\nprint(json.dumps({'argv':sys.argv[1:],'fixture':False}))\n")
            request = root / "request.json"
            request.write_text('{}')
            workspace = root / "arbitrary-release"
            base = [str(ROOT / "videoops-media-generation/bin/run"), "--media",
                    "--operation", "import", "--workspace", str(workspace),
                    "--request", str(request), "--runtime-root", str(runtime)]
            env = dict(os.environ, KUJO_BIN=kujo)
            result = subprocess.run(base, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads(result.stdout)
            self.assertEqual(receipt['argv'], ['media','import','--workspace',str(workspace),'--request',str(request)])
            self.assertFalse(receipt['fixture'])
            conflict = subprocess.run(base + ['--fixture'], env=env, text=True, capture_output=True)
            self.assertEqual(conflict.returncode, 2)
            self.assertFalse(workspace.exists(), 'bridge must not initialize fixture content')
            invalid = subprocess.run([*base[:2], '--operation', 'arbitrary-command', *base[4:]], env=env, text=True, capture_output=True)
            self.assertEqual(invalid.returncode, 2)

if __name__ == '__main__':
    unittest.main()
