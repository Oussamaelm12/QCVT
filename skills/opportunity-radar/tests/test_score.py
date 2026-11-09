import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "score.py"
EXAMPLE = ROOT / "examples" / "ideas.json"

class ScoreTest(unittest.TestCase):
    def test_unvalidated_example_does_not_pass(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), str(EXAMPLE)], capture_output=True, text=True, check=True)
        data = json.loads(proc.stdout)
        self.assertFalse(data["results"][0]["evidence_ready"])
        self.assertEqual(data["results"][0]["recommendation"], "INSUFFICIENT EVIDENCE")

if __name__ == "__main__":
    unittest.main()
