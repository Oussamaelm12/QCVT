import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from provider_policy import select
class ProviderPolicyTests(unittest.TestCase):
 def test_no_paid_by_default(self):
  x=select()
  self.assertTrue(all(not a["enabled"] or a["upfront_usd"]=="0" for a in x))
  self.assertFalse(next(a for a in x if a["provider"]=="dataforseo")["eligible"])
 def test_cost_not_authorization(self):
  x=select("50")
  self.assertTrue(next(a for a in x if a["provider"]=="dataforseo")["eligible"])
  self.assertFalse(next(a for a in x if a["provider"]=="dataforseo")["enabled"])
 def test_negative(self):
  with self.assertRaises(ValueError):select("-1")
if __name__=="__main__":unittest.main()
