import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPOS = Path(os.environ.get("KUJO_REPOS", ROOT.parent))
HAS_RUNTIME = Path(os.environ.get("KUJO_BIN", REPOS / "kujo/target/release/kujo")).is_file() and all(
    (REPOS / name).is_dir()
    for name in ["dispatch", "agents-sdk", "kujo-agents", "kujo-skills", "storydesk", "dossier", "galleypack", "bluepencil", "versionseal", "presswire", "readersignal", "assetworks"]
)


class PublishingHouseIntegrationTests(unittest.TestCase):
    @unittest.skipUnless(HAS_RUNTIME, "Publishing House runtime dependencies are not available")
    def test_all_eleven_offline_fixture(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                ["bash", "scripts/run-publishing-house-fixture.sh", "--out", str(Path(temp) / "proof")],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=300,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            envelope = json.loads(result.stdout)
            self.assertTrue(envelope["ok"])
            proof = json.loads(Path(envelope["proof"]).read_text())
            self.assertEqual(proof["workflow_count"], 11)
            self.assertEqual(proof["package_checksum"], proof["publication_checksum"])
            self.assertEqual(proof["network_calls"], 0)
            self.assertEqual(proof["tool_contract_preflights_checked"], 34)
            self.assertEqual(proof["agent_receipts_checked"], 38)
            self.assertEqual(proof["revision_loop"], "passed")
            self.assertEqual(proof["approval_pause_resume"], "passed")
            self.assertEqual(proof["idempotency"], "passed")


if __name__ == "__main__":
    unittest.main()
