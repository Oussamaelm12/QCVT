import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from pipeline import search, research

class FakeResponse:
    def __init__(self,data): self.data=data
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def read(self,n): return self.data[:n]

class PipelineTests(unittest.TestCase):
    def test_search(self):
        raw=json.dumps({"results":[{"wrapperType":"software","trackId":7,"trackName":"A"},{"wrapperType":"artist","trackId":8}]}).encode()
        r=search("meal planner",opener=lambda request,timeout:FakeResponse(raw))
        self.assertEqual([a["id"] for a in r["apps"]],[7])
        self.assertNotIn("revenue",r["apps"][0])
    def test_deduplication(self):
        def fake(q,country,limit): return {"source_url":"https://itunes.apple.com/search?term="+q,"apps":[{"id":10,"name":"Same","rating_count":2}]}
        r=research(["habit tracker","daily habits"],pause=0,search_fn=fake)
        self.assertEqual(r["unique_apps"],1)
        self.assertEqual(len(r["apps"][0]["matched_queries"]),2)
    def test_partial_failure(self):
        def fake(q,country,limit):
            if q=="bad": raise OSError("offline")
            return {"source_url":"https://itunes.apple.com/search","apps":[]}
        self.assertEqual(len(research(["good","bad"],pause=0,search_fn=fake)["failed_queries"]),1)
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): search("x")
        with self.assertRaises(ValueError): search("valid",country="../")
        with self.assertRaises(ValueError): research(["same","SAME"],pause=0)
    def test_size_limit(self):
        with self.assertRaises(ValueError): search("valid",opener=lambda request,timeout:FakeResponse(b"x"*2000001))

if __name__=="__main__": unittest.main()
