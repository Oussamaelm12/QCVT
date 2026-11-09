import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from hackernews import fetch

class FakeResponse:
    def __init__(self,raw): self.stream=io.BytesIO(raw)
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self,n): return self.stream.read(n)

class HackerNewsTests(unittest.TestCase):
    def test_discussion_link_and_fields(self):
        data={"hits":[{"objectID":"123","title":"Ask HN: Need a better budget planner","points":11,"num_comments":7,"created_at":"2026-11-01T12:00:00Z"},{"objectID":"bad","title":"Ignore"}]}
        out=fetch("budget planner",opener=lambda req,timeout:FakeResponse(json.dumps(data).encode()))
        self.assertEqual(len(out["results"]),1)
        self.assertEqual(out["results"][0]["discussion_url"],"https://news.ycombinator.com/item?id=123")
        self.assertNotIn("revenue",out["results"][0])
    def test_bad_inputs(self):
        with self.assertRaises(ValueError): fetch("x")
        with self.assertRaises(ValueError): fetch("valid",hits=101)
    def test_size_guard(self):
        with self.assertRaises(ValueError): fetch("valid",opener=lambda req,timeout:FakeResponse(b"z"*2000001))
    def test_unexpected_payload(self):
        with self.assertRaises(ValueError): fetch("valid",opener=lambda req,timeout:FakeResponse(b"{}"))

if __name__=="__main__": unittest.main()
