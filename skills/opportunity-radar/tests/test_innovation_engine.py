import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from innovation_engine import evaluate,markdown

def fixture():
 return {
  "subject":"SYNTHETIC EXAMPLE — not a market finding",
  "sources":[{"id":"s1","url":"https://example.org/one","review_status":"manually_checked"},
             {"id":"s2","url":"https://example.net/two","review_status":"manually_checked"},
             {"id":"s3","url":"https://example.com/three","review_status":"manually_checked"}],
  "findings":[{"id":"f1","source_ids":["s1"],"statement":"Synthetic pain"}],
  "competitors":[{"id":"a","name":"A","source_ids":["s1"],"attributes":{"price":"unknown"}},
                 {"id":"b","name":"B","source_ids":["s2"],"attributes":{"price":"unknown"}},
                 {"id":"c","name":"C","source_ids":["s3"],"attributes":{"price":"unknown"}}],
  "jtbd":[{"statement":"Avoid synthetic error","finding_ids":["f1"]}],
  "ck_nodes":[{"space":"C","statement":"Could work be eliminated?","finding_ids":["f1"]},
              {"space":"K","statement":"Unknown API limits","finding_ids":[]}],
  "concepts":[{"id":"i1","name":"Hypothetical product","finding_ids":["f1"]}],
  "tests":[{"concept_id":"i1","target_customer":"Synthetic user",
            "test_method":"Price commitment interview","success_threshold":"5 actual commitments",
            "stop_rule":"Stop after 10 noes","duration":"7 days","cost_ceiling":"0 EUR"}],
  "contradictions":[{"improve":"speed","worsen":"accuracy"}],
  "blue_ocean_factors":[{"eliminate":"manual exports","raise":"control"}]
 }

class InnovationTests(unittest.TestCase):
 def test_benchmark_requires_three_checked(self):
  self.assertTrue(evaluate(fixture())["benchmark_complete"])
  d=fixture();d["sources"][2]["review_status"]="unchecked"
  self.assertFalse(evaluate(d)["benchmark_complete"])
 def test_missing_sources_not_benchmark(self):
  d=fixture();d["competitors"][0]["source_ids"]=[]
  self.assertFalse(evaluate(d)["benchmark_complete"])
 def test_unknown_references_rejected(self):
  d=fixture();d["concepts"][0]["finding_ids"]=["absent"]
  with self.assertRaises(ValueError):evaluate(d)
 def test_invalid_url_rejected(self):
  d=fixture();d["sources"][0]["url"]="file:///etc/passwd"
  with self.assertRaises(ValueError):evaluate(d)
 def test_duplicate_competitors_rejected(self):
  d=fixture();d["competitors"][1]["id"]="a"
  with self.assertRaises(ValueError):evaluate(d)
 def test_ck_keeps_hypothesis_distinct(self):
  r=evaluate(fixture())
  self.assertEqual(r["ck_nodes"][0]["status"],"concept_hypothesis")
  self.assertEqual(r["ck_nodes"][1]["status"],"knowledge_to_verify")
  self.assertIn("not validated",r["concepts"][0]["status"])
 def test_test_card_not_payment_proof(self):
  r=evaluate(fixture())
  self.assertTrue(r["tests"][0]["preregistered"])
  self.assertIn("UNKNOWN",r["tests"][0]["actual_outcome"])
  self.assertIn("not automatically verified",markdown(r))
 def test_missing_test_threshold_is_incomplete(self):
  d=fixture();del d["tests"][0]["success_threshold"]
  self.assertFalse(evaluate(d)["tests"][0]["preregistered"])
 def test_method_routing(self):
  r=evaluate(fixture())
  self.assertEqual(r["method_catalog"]["ck"]["stage"],"strategy")
  self.assertEqual(r["method_catalog"]["benchmark"]["stage"],"research")
if __name__=="__main__":unittest.main()
