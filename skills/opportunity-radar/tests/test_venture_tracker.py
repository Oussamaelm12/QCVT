import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from venture_studio import run
from venture_tracker import add_event,summary
from test_venture_studio import sample

class TrackingTests(unittest.TestCase):
 def test_record_and_preserve_across_rerun(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/"in.json";src.write_text(json.dumps(sample()))
   output=Path(td)/"out";run(src,output)
   progress=output/"PROGRESS.json"
   add_event(progress,"research","in_progress","Checked original problem reports","https://example.org/a")
   add_event(progress,"strategy","blocked","Waiting on test evidence")
   run(src,output)
   state=json.loads(progress.read_text())
   self.assertEqual(len(state["events"]),2)
   self.assertEqual({p["id"]:p["status"] for p in state["phases"]}["strategy"],"blocked")
   self.assertEqual(summary(progress)["reported_events"],2)
   self.assertIsNone(summary(progress)["actual_revenue_eur"])
 def test_critical_completions_require_evidence(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/"in.json";src.write_text(json.dumps(sample()))
   output=Path(td)/"out";run(src,output)
   with self.assertRaises(ValueError):
    add_event(output/"PROGRESS.json","validate","completed","Claim validated")
 def test_other_subject_cannot_overwrite_progress(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/"in.json";src.write_text(json.dumps(sample()))
   output=Path(td)/"out";run(src,output)
   d=sample();d["subject"]="Different study";src.write_text(json.dumps(d))
   with self.assertRaises(ValueError):run(src,output)
 def test_url_validation(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/"in.json";src.write_text(json.dumps(sample()))
   output=Path(td)/"out";run(src,output)
   with self.assertRaises(ValueError):
    add_event(output/"PROGRESS.json","research","completed","Claim reviewed","http://example.org")
if __name__=="__main__":unittest.main()
