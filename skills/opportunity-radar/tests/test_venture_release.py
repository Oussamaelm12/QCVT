import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from venture_release import deliver,load_json,build
from test_venture_studio import sample
from test_innovation_engine import fixture

class ReleaseTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  self.selection=self.root/"selection.json"
  self.selection.write_text(json.dumps(sample()))
 def test_release_manifest_and_checksums(self):
  import hashlib
  dest=self.root/"out"
  result=deliver(self.selection,dest)
  self.assertEqual(result["gate"],"HUMAN_REVIEW_REQUIRED")
  self.assertEqual(result["network_calls_performed"],0)
  self.assertEqual(result["costs_incurred_by_program_eur"],0)
  self.assertFalse(json.loads((dest/"PROGRESS.json").read_text())["commercially_validated"])
  for name,entry in result["files"].items():
   self.assertEqual(hashlib.sha256((dest/name).read_bytes()).hexdigest(),entry["sha256"])
 def test_no_overwrite_existing_research(self):
  dest=self.root/"out";deliver(self.selection,dest)
  before=(dest/"RESEARCH_BRIEF.md").read_bytes()
  with self.assertRaises(FileExistsError):deliver(self.selection,dest)
  self.assertEqual((dest/"RESEARCH_BRIEF.md").read_bytes(),before)
 def test_optional_innovation_integration(self):
  i=fixture();i["subject"]=sample()["subject"]
  innovation=self.root/"innovation.json";innovation.write_text(json.dumps(i))
  result=deliver(self.selection,self.root/"out",innovation)
  self.assertIn("INNOVATION_DOSSIER.md",result["files"])
  self.assertEqual(result["gate"],"HUMAN_REVIEW_REQUIRED")
 def test_reject_subject_mismatch_before_writing(self):
  innovation=self.root/"innovation.json";innovation.write_text(json.dumps(fixture()))
  with self.assertRaises(ValueError):deliver(self.selection,self.root/"out",innovation)
  self.assertFalse((self.root/"out").exists())
 def test_research_gate_blocks_empty_evidence(self):
  d=sample();d["sources"]=[];d["findings"]=[];d["competitors"]=[];d["concepts"]=[]
  self.selection.write_text(json.dumps(d))
  result=deliver(self.selection,self.root/"out")
  self.assertEqual(result["gate"],"RESEARCH_BLOCKED")
 def test_reject_oversize_input(self):
  p=self.root/"large.json";p.write_text(" "*2_000_001)
  with self.assertRaises(ValueError):load_json(p)
 def test_invalid_json_does_not_create_output(self):
  self.selection.write_text("{")
  with self.assertRaises(json.JSONDecodeError):deliver(self.selection,self.root/"out")
  self.assertFalse((self.root/"out").exists())
if __name__=="__main__":unittest.main()
