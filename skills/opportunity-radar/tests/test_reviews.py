import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from reviews import fetch_reviews

class FakeResponse:
    def __init__(self,raw): self.stream=io.BytesIO(raw)
    def __enter__(self): return self
    def __exit__(self,*args): return False
    def read(self,n): return self.stream.read(n)

class ReviewsTest(unittest.TestCase):
    def test_reviews_excludes_feed_metadata(self):
        data={"feed":{"entry":[
            {"id":{"label":"metadata"},"title":{"label":"app"},"im:name":{"label":"app"}},
            {"id":{"label":"r1"},"im:rating":{"label":"2"},"title":{"label":"Broken reminders"},"content":{"label":"I missed my reminder"},"updated":{"label":"2026-11-01"}}
        ]}}
        out=fetch_reviews(123,opener=lambda req,timeout:FakeResponse(json.dumps(data).encode()))
        self.assertEqual(len(out["reviews"]),1)
        self.assertEqual(out["reviews"][0]["rating"],2)
        self.assertEqual(out["reviews"][0]["text"],"I missed my reminder")
    def test_empty_feed(self):
        out=fetch_reviews(123,opener=lambda req,timeout:FakeResponse(b'{"feed":{}}'))
        self.assertEqual(out["reviews"],[])
    def test_input_validation(self):
        with self.assertRaises(ValueError): fetch_reviews("123/../../x")
        with self.assertRaises(ValueError): fetch_reviews(123,page=11)
    def test_size_limit(self):
        with self.assertRaises(ValueError):
            fetch_reviews(123,opener=lambda req,timeout:FakeResponse(b"x"*2000001))

if __name__=="__main__": unittest.main()
