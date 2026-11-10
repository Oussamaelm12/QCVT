import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from decision_engine import evaluate,rank
class DecisionTests(unittest.TestCase):
 def test_unsubstantiated_high_rating_capped(self):
  r=evaluate({"title":"Big idea","ratings":{x:5 for x in ("pain","demand","distribution","economics","feasibility","competition","risk")}})
  self.assertEqual(r["score"],35)
  self.assertEqual(r["status"],"UNSUPPORTED")
 def test_single_source_is_not_independent(self):
  e=[{"kind":"review","url":"https://example.com/a","observed_at":"2026-11-10"},{"kind":"review","url":"https://example.com/b","observed_at":"2026-11-10"}]
  r=evaluate({"title":"A","evidence":e})
  self.assertEqual(r["independent_domains"],1)
  self.assertEqual(r["status"],"DISCOVERY")
 def test_two_sources_no_sales_not_validated(self):
  e=[{"kind":"review","url":"https://one.com/a","observed_at":"2026-11-10"},{"kind":"community_post","url":"https://two.com/b","observed_at":"2026-11-10"}]
  r=evaluate({"title":"A","evidence":e,"ratings":{"pain":5}})
  self.assertEqual(r["status"],"RESEARCH")
  self.assertLessEqual(r["score"],65)
 def test_bad_evidence_rejected(self):
  r=evaluate({"title":"A","evidence":[{"kind":"review","url":"http://localhost","observed_at":"today"}]})
  self.assertEqual(len(r["accepted_evidence"]),0)
 def test_invalid_rating(self):
  with self.assertRaises(ValueError):evaluate({"title":"A","ratings":{"demand":9}})
 def test_rank_deterministic(self):
  self.assertEqual([x["title"] for x in rank([{"title":"Z"},{"title":"A"}])],["A","Z"])
if __name__=="__main__":unittest.main()
