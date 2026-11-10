import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from score import evaluate

def ev(url,claim="specific pain",days=0):
    return {"url":url,"claim":claim,"geography":"FR","type":"observed","captured_at":(date.today()-timedelta(days=days)).isoformat()}

SCORES={"pain":3,"distribution":3,"monetization":3,"competition_gap":3,"feasibility":3,"retention":3,"risk":3}
def idea(evidence,**kwargs):
    return {"name":"A","scores":SCORES,"distribution_channel":"Organic search","test":{"metric":"20 qualified visitors"},"evidence":evidence,**kwargs}

class ScoreGuardTests(unittest.TestCase):
    def test_independent_recent_observations(self):
        x=evaluate(idea([ev("https://a.example/1"),ev("https://a.example/2","another pain"),ev("https://b.example/3","third pain")]))
        self.assertTrue(x["evidence_ready"])
    def test_duplicate_cannot_count_as_three(self):
        x=evaluate(idea([ev("https://a.example/1"),ev("https://a.example/1"),ev("https://b.example/2","other")]))
        self.assertFalse(x["evidence_ready"])
    def test_stale_excluded(self):
        x=evaluate(idea([ev("https://a.example/1",days=366),ev("https://a.example/2","another"),ev("https://b.example/3","third")]))
        self.assertFalse(x["evidence_ready"])
    def test_http_not_accepted(self):
        x=evaluate(idea([ev("http://a.example/1"),ev("https://a.example/2","another"),ev("https://b.example/3","third")]))
        self.assertFalse(x["evidence_ready"])
    def test_missing_test_cannot_recommend(self):
        i=idea([ev("https://a.example/1"),ev("https://a.example/2","another"),ev("https://b.example/3","third")])
        i["test"]=None
        x=evaluate(i)
        self.assertEqual(x["recommendation"],"INSUFFICIENT EVIDENCE")
    def test_missing_claim_rejected(self):
        e=ev("https://a.example/1");e["claim"]=""
        x=evaluate(idea([e,ev("https://a.example/2","another"),ev("https://b.example/3","third")]))
        self.assertFalse(x["evidence_ready"])

if __name__=="__main__":unittest.main()
