import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from production import markdown

class ProductionTests(unittest.TestCase):
    def test_report_contains_sources_and_limitations(self):
        dossier={"queries":["budget planner"],"country":"fr","generated_at":"2026-11-10T00:00:00Z",
            "app_count":1,"hn_discussions":1,"review_count":0,"errors":[],
            "app_results":[{"name":"Budget App","url":"https://apps.apple.com/app/id1"}],
            "discussion_results":[{"title":"Ask HN","discussion_url":"https://news.ycombinator.com/item?id=123"}],
            "review_results":[]}
        out=markdown(dossier)
        self.assertIn("Budget App",out)
        self.assertIn("not validated opportunities",out)
        self.assertIn("No verified market size",out)
if __name__=="__main__":unittest.main()
