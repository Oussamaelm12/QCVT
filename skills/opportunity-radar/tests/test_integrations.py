import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from integrations import google_trends,reddit_search

class Response:
    def __init__(self,data): self.stream=io.BytesIO(json.dumps(data).encode())
    def __enter__(self):return self
    def __exit__(self,*a):return False
    def read(self,n):return self.stream.read(n)

class IntegrationsTest(unittest.TestCase):
    def test_trends_requires_approval(self):
        with self.assertRaises(PermissionError):google_trends("budget planner",api_key="x")
    def test_trends_relative_not_volume(self):
        payload={"interest_over_time":{"timeline_data":[{"date":"Nov 1","values":[{"extracted_value":44}]}]}}
        result=google_trends("budget planner",allow_paid=True,api_key="test",opener=lambda req,timeout:Response(payload))
        self.assertEqual(result["points"][0]["relative_index"],44)
        self.assertNotIn("test",result["source_url"])
    def test_reddit_requires_credentials(self):
        with self.assertRaises(RuntimeError):reddit_search("budget planner",token="",user_agent="")
    def test_reddit_post_provenance(self):
        payload={"data":{"children":[{"data":{"id":"abc12","title":"Help","permalink":"/r/test/comments/abc12/help/","selftext":"missing tool"}}]}}
        r=reddit_search("budget planner",token="test",user_agent="OpportunityRadar-test",opener=lambda req,timeout:Response(payload))
        self.assertEqual(r["posts"][0]["id"],"abc12")
        self.assertTrue(r["posts"][0]["url"].startswith("https://www.reddit.com/r/"))
if __name__=="__main__":unittest.main()
