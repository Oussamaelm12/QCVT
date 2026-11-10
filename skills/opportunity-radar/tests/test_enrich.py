import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from enrich import enrich

class EnrichTests(unittest.TestCase):
    def test_no_paid_calls_without_approval(self):
        with self.assertRaises(PermissionError):
            enrich({"queries":["budget planner"]},trends=True)
    def test_optional_sources(self):
        x=enrich({"queries":["budget planner"],"country":"fr"},reddit=True,trends=True,allow_paid=True,
            reddit_fn=lambda q:{"source":"Reddit OAuth API","posts":[]},
            trends_fn=lambda q,geography,allow_paid:{"source":"Google Trends via SerpApi","points":[]})
        self.assertEqual(len(x["source_results"]),2)
        self.assertEqual(x["validated_opportunities"],0)
    def test_failure_is_reported(self):
        def broken(q):raise RuntimeError("API unavailable")
        x=enrich({"queries":["budget planner"]},reddit=True,reddit_fn=broken)
        self.assertEqual(len(x["errors"]),1)
if __name__=="__main__":unittest.main()
