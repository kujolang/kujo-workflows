from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationValidationTests(unittest.TestCase):
    def test_public_documentation_and_release_metadata(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_docs.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("documentation validation: PASS", result.stdout)


if __name__ == "__main__":
    unittest.main()
