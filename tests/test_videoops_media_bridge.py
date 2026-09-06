"""Exercise the Kujo production bridge with a non-network runtime stub."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class MediaBridgeTests(unittest.TestCase):
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
