"""Focused offline tests for the Scout research-only shadow module."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_connection_thesis import validate, compare

class ScoutConnectionTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(id="x", source_url="https://example.org/research", original_contribution="A",
            evidence="Unverified description", ghostmesh_gap="B", connection_thesis="C",
            proposed_experiment="Test a fixed synthetic fixture", strongest_objection="D",
            recommendation="INVESTIGATE", outreach_authorized=False)

    def test_valid(self):
        self.assertEqual(validate(self.good), [])
    def test_no_outreach(self):
        x = dict(self.good, outreach_authorized=True)
        self.assertTrue(any("outreach" in e for e in validate(x)))
    def test_reject_bad_source(self):
        self.assertTrue(validate(dict(self.good, source_url="http://example.org")))
    def test_reject_empty_thesis(self):
        self.assertTrue(validate(dict(self.good, connection_thesis=" ")))
    def test_malformed_recommendation_type(self):\n        self.assertIn("invalid recommendation", validate(dict(self.good, recommendation=[])))\n    def test_malformed_experiment_type(self):\n        self.assertTrue(validate(dict(self.good, recommendation="CONSIDER_INTRODUCTION", proposed_experiment=[])))\n    def test_no_invented_accuracy(self):
        self.assertIsNone(compare([self.good])["measured_accuracy"])
    def test_no_vacuous_introduction(self):
        x = dict(self.good, recommendation="CONSIDER_INTRODUCTION", proposed_experiment="unknown")
        self.assertTrue(validate(x))

if __name__ == "__main__":
    unittest.main()
