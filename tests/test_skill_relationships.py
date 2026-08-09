from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tests/skill_relationship_contracts.sh"


def missing_relationship_dependencies() -> list[Path]:
    repos = Path(os.environ.get("KUJO_REPOS", ROOT.parent))
    kujo = Path(os.environ.get("KUJO_BIN", repos / "kujo/target/release/kujo"))
    required = [
        kujo,
        repos / "spec/scripts/spec",
        repos / "scout/scout.kujo",
        repos / "scent/scent.kujo",
        repos / "lens/lens",
        repos / "casefile/casefile.kujo",
        repos / "packwrite/bin/packwrite",
        repos / "runledger/bin/runledger",
    ]
    return [path for path in required if not path.exists()]


class SkillRelationshipContractTests(unittest.TestCase):
    def test_under_tested_relationships_have_positive_and_negative_boundary_evidence(self) -> None:
        missing = missing_relationship_dependencies()
        if missing:
            self.skipTest(
                "requires sibling Kujo tool checkouts: " + ", ".join(str(path) for path in missing)
            )
        result = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS skill relationship contracts", result.stdout)


if __name__ == "__main__":
    unittest.main()
