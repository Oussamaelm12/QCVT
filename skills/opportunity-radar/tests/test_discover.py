import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from discover import run

def apps(queries,country,limit,pause):
    return {"apps":[{"id":12,"name":"Sample","url":"https://apps.apple.com/app/id12"}],"failed_queries":[]}
def hn(q,hits):
    return {"source":"Hacker News via Algolia public API","results":[{"id":"123","title":"A discussion","discussion_url":"https://news.ycombinator.com/item?id=123"}]}
def reviews(app_id,country):
    return {"reviews":[{"rating":2,"text":"missing feature"}]}
class DiscoveryTests(unittest.TestCase):
    def test_end_to_end_mocked(self):
        result=run(["budget planner"],app_fn=apps,hn_fn=hn,review_fn=reviews,pause=0)
        self.assertEqual(result["app_count"],1)
        self.assertEqual(result["hn_discussions"],1)
        self.assertEqual(result["review_count"],1)
        self.assertEqual(result["inventory"]["source_count"],2)
        self.assertEqual(result["validated_opportunities"],0)
    def test_partial_failure(self):
        def broken(q,hits): raise OSError("unavailable")
        result=run(["budget planner"],app_fn=apps,hn_fn=broken,review_fn=reviews,pause=0)
        self.assertEqual(result["app_count"],1)
        self.assertEqual(len(result["errors"]),1)
    def test_input_restrictions(self):
        with self.assertRaises(ValueError):run(["x"],app_fn=apps,hn_fn=hn,review_fn=reviews,pause=0)
        with self.assertRaises(ValueError):run(["valid"],country="../../",app_fn=apps,hn_fn=hn,review_fn=reviews,pause=0)
if __name__=="__main__":unittest.main()
