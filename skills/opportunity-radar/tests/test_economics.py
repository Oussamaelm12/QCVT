import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from economics import model

class EconomicsTest(unittest.TestCase):
    def test_subscription_scenario(self):
        result = model(20, conversion_fraction=0.02)
        self.assertEqual(result["paying_customers_required"], 500)
        self.assertEqual(result["qualified_visitors_required_at_assumed_conversion"], 25000)
        self.assertEqual(result["contribution_after_listed_costs_eur"], 8480)
        self.assertEqual(result["status"], "SCENARIO, NOT FORECAST")
    def test_bad_input(self):
        with self.assertRaises(ValueError): model(0)
        with self.assertRaises(ValueError): model(20, conversion_fraction=0)

if __name__ == "__main__": unittest.main()
