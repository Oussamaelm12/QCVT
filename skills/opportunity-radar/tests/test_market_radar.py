import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from market_radar import plan,scan,SECTORS,STRATEGY_LENSES
class RadarTests(unittest.TestCase):
 def test_diversity(self):
  q=plan(max_queries=16)
  self.assertEqual(len(q),16)
  self.assertEqual(len({x["sector"] for x in q}),16)
 def test_weekly_rotation(self):
  first=plan(max_queries=5,rotation=0)
  next_week=plan(max_queries=5,rotation=1)
  self.assertNotEqual(first,next_week)
  self.assertEqual(len(next_week),5)
 def test_rotation_validation(self):
  with self.assertRaises(ValueError):plan(rotation=-1)
 def test_explicit_empty_sectors(self):
  with self.assertRaises(ValueError):plan([])
 def test_coverage_counts(self):
  def fake(q,**kw):return {"app_count":2,"hn_discussions":3,"review_count":4,"errors":[]}
  r=scan(max_queries=6,run_fn=fake,pause=0,rotation=2)
  self.assertEqual(r["observed_counts"],{"apps":4,"discussions":6,"reviews":8})
  self.assertEqual(r["completed_batches"],2)
 def test_all_domains(self):
  self.assertGreaterEqual(len(SECTORS),15)
  self.assertGreaterEqual(len(STRATEGY_LENSES),15)
 def test_invalid_sector(self):
  with self.assertRaises(ValueError):plan(["unknown"])
 def test_batching_and_no_fake_validation(self):
  calls=[]
  def fake(q,**kw):
   calls.append(q)
   return {"app_count":0,"hn_discussions":0,"review_count":0,"errors":[]}
  result=scan(max_queries=12,run_fn=fake,pause=0)
  self.assertEqual(len(calls),3)
  self.assertEqual([len(q) for q in calls],[5,5,2])
  self.assertEqual(result["validated_opportunities"],0)
 def test_partial_failure(self):
  def broken(q,**kw):raise OSError("offline")
  r=scan(max_queries=3,run_fn=broken,pause=0)
  self.assertEqual(len(r["errors"]),1)
if __name__=="__main__":unittest.main()
