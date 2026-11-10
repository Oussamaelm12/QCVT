import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from strategic_brain import analyze,record_decision,validate_portfolio

def fixture():
 return {"businesses":[
  {"id":"alpha","market":{"title":"Synthetic A","ratings":{"pain":5,"demand":4,"distribution":3,"economics":3,"feasibility":3,"competition":2,"risk":2},"evidence":[]}},
  {"id":"beta","market":{"title":"Synthetic B","ratings":{"pain":2,"demand":2,"distribution":2,"economics":2,"feasibility":2,"competition":2,"risk":2},"evidence":[]}}
 ]}

class StrategicBrainTests(unittest.TestCase):
 def test_market_rank_independent_of_constraints(self):
  d=fixture()
  baseline=analyze(d)["market_ranking"]
  c1={"budget_eur":0,"hours_per_week":1,"estimates":{"alpha":{"estimated_test_cost_eur":1000,"estimated_test_hours":40}}}
  c2={"budget_eur":100000,"hours_per_week":100,"estimates":{"alpha":{"estimated_test_cost_eur":1000,"estimated_test_hours":40}}}
  self.assertEqual(baseline,analyze(d,c1)["market_ranking"])
  self.assertEqual(baseline,analyze(d,c2)["market_ranking"])
  self.assertFalse(analyze(d,c1)["execution_feasibility"]["alpha"]["budget_fit"])
  self.assertTrue(analyze(d,c2)["execution_feasibility"]["alpha"]["budget_fit"])
 def test_no_false_go(self):
  r=analyze(fixture())
  self.assertEqual(r["market_ranking"][0]["market_status"],"UNSUPPORTED")
  self.assertNotIn("GO",r["market_ranking"][0]["recommendation"])
 def test_personal_profile_rejected(self):
  d=fixture();d["businesses"][0]["personal_profile"]={"skills":["x"]}
  with self.assertRaises(ValueError):validate_portfolio(d)
 def test_duplicate_business_rejected(self):
  d=fixture();d["businesses"][1]["id"]="alpha"
  with self.assertRaises(ValueError):analyze(d)
 def test_invalid_constraints(self):
  for x in (-1,float("nan"),"100"):
   with self.assertRaises(ValueError):analyze(fixture(),{"budget_eur":x})
 def test_journal_chain(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/"journal.jsonl"
   entry={"business_id":"alpha","decision":"RESEARCH","reason":"Evidence missing",
          "evidence_refs":[],"next_review":"2026-11-17"}
   a=record_decision(path,entry)
   b=record_decision(path,entry)
   self.assertIsNone(a["previous_record_sha256"])
   self.assertIsNotNone(b["previous_record_sha256"])
   self.assertEqual(len(path.read_text().splitlines()),2)
 def test_journal_requires_reason_and_date(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):
    record_decision(Path(td)/"x",{"business_id":"alpha","decision":"GO","reason":"",
                   "evidence_refs":[],"next_review":"today"})
if __name__=="__main__":unittest.main()
