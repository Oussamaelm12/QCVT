import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from venture_studio import assess, render, run, validate, domain

def sample():
    return {
        "subject":"Synthetic business category (TEST FIXTURE ONLY)",
        "market":"Example-market",
        "research_questions":["Which workflow is costly?","Which alternatives exist?"],
        "sources":[
          {"id":"s1","title":"Synthetic source one","url":"https://example.org/a","kind":"primary","review_status":"manually_checked","reviewed_at":"2026-11-10"},
          {"id":"s2","title":"Synthetic source two","url":"https://example.net/b","kind":"review","review_status":"manually_checked","reviewed_at":"2026-11-10"}
        ],
        "findings":[{"id":"f1","statement":"Synthetic observation, NOT a real market claim",
                     "classification":"observed","source_ids":["s1","s2"]}],
        "competitors":[{"name":"Synthetic incumbent","url":"https://example.com","price":"unknown"}],
        "concepts":[{"id":"c1","name":"Hypothetical utility","target_user":"Example operator",
                     "finding_ids":["f1"],"differentiation_hypothesis":"One-click setup",
                     "smallest_test":"Prototype trial","success_criterion":"Five signed test commitments"}]
    }

class VentureStudioTests(unittest.TestCase):
    def test_corrobated_links_only_manual_not_factual_proof(self):
        r=assess(sample())
        self.assertTrue(r["research_ready_for_human_review"])
        self.assertEqual(r["corroborated_observations"],1)
        self.assertFalse(r["commercially_validated"])
        self.assertTrue(r["concepts"][0]["test_ready"])
    def test_same_host_not_two_independent_hosts(self):
        d=sample();d["sources"][1]["url"]="https://example.org/another"
        self.assertFalse(assess(d)["research_ready_for_human_review"])
    def test_unchecked_sources_not_corroboration(self):
        d=sample();d["sources"][1]["review_status"]="unchecked"
        self.assertFalse(assess(d)["research_ready_for_human_review"])
    def test_hypotheses_not_corrobated_as_observed(self):
        d=sample();d["findings"][0]["classification"]="hypothesis"
        self.assertFalse(assess(d)["research_ready_for_human_review"])
    def test_untrusted_url_rejected(self):
        for url in ("http://example.org","file:///etc/passwd","https://user:pass@example.org","https://"):
            d=sample();d["sources"][0]["url"]=url
            with self.assertRaises(ValueError):validate(d)
    def test_dangling_reference_rejected(self):
        d=sample();d["concepts"][0]["finding_ids"]=["not_here"]
        with self.assertRaises(ValueError):validate(d)
    def test_invalid_review_date(self):
        d=sample();d["sources"][0]["reviewed_at"]="yesterday"
        with self.assertRaises(ValueError):validate(d)
    def test_artifacts_created_and_no_claim_of_validation(self):
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)/"input.json"
            src.write_text(json.dumps(sample()),encoding="utf-8")
            state=run(src,Path(td)/"out")
            assert state["research_ready_for_human_review"]
            names={p.name for p in (Path(td)/"out").iterdir()}
            self.assertEqual(names,{"RESEARCH_BRIEF.md","STRATEGY_LAB.md","BUILD_PLAN.md",
                                     "PROGRESS.json","EVIDENCE_ASSESSMENT.json"})
            progress=json.loads((Path(td)/"out"/"PROGRESS.json").read_text())
            self.assertEqual(progress["status"],"HUMAN_REVIEW_REQUIRED")
            self.assertIsNone(progress["actual_revenue_eur"])
            plan=(Path(td)/"out"/"BUILD_PLAN.md").read_text()
            self.assertIn("NOT APPROVED",plan)
    def test_no_synthetic_concepts_generated(self):
        d=sample();d["concepts"]=[]
        self.assertEqual(assess(d)["concepts"],[])
        self.assertIn("NO ideas are ranked",render(d,assess(d))["STRATEGY_LAB.md"])
if __name__=="__main__":unittest.main()
