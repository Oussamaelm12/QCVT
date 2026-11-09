import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from itunes import fetch

class FakeResponse:
    def __init__(self, data): self.stream = io.BytesIO(data)
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, size): return self.stream.read(size)

class ITunesTests(unittest.TestCase):
    def test_extracts_metadata_without_inventing_revenue(self):
        payload = {"results": [
            {"wrapperType":"software","trackId":123,"trackName":"Example","price":0,"averageUserRating":4.5,"trackViewUrl":"https://apps.apple.com/example"},
            {"wrapperType":"artist","trackName":"Ignore"}]}
        result = fetch("habit tracker", opener=lambda request, timeout: FakeResponse(json.dumps(payload).encode()))
        self.assertEqual(len(result["apps"]), 1)
        self.assertEqual(result["apps"][0]["app_id"], 123)
        self.assertNotIn("revenue", result["apps"][0])
        self.assertIn("term=habit+tracker", result["source_url"])
    def test_rejects_bad_inputs(self):
        with self.assertRaises(ValueError): fetch("x", limit=100)
        with self.assertRaises(ValueError): fetch("x", country="../../")
        with self.assertRaises(ValueError): fetch(" ")
    def test_limits_response_size(self):
        with self.assertRaises(ValueError):
            fetch("x", opener=lambda request, timeout: FakeResponse(b"x" * 2_000_001))

if __name__ == "__main__": unittest.main()
