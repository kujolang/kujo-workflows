import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ContractValidationTests(unittest.TestCase):
    def test_contracts_and_examples(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_contracts.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("schemas=5", result.stdout)
        self.assertIn("examples=5", result.stdout)


if __name__ == "__main__":
    unittest.main()
