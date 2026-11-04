"""Focused research-only report renderer tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_connection_report import render


class ScoutConnectionReportTests(unittest.TestCase):
    def setUp(self):
        self.good = dict(
            id="test", source_url="https://example.org/paper",
            original_contribution="Novel method", evidence="Abstract only",
            ghostmesh_gap="Missing capability", connection_thesis="Complementary approach",
            proposed_experiment="Run controlled case", strongest_objection="May duplicate work",
            recommendation="INVESTIGATE", outreach_authorized=False,
        )

    def test_all_fields_and_caveats(self):
        text = render([self.good])
        for fragment in (
            "Novel method", "Missing capability", "Complementary approach",
            "May duplicate work", "Run controlled case", "Abstract only",
            "https://example.org/paper", "Outreach authorized: no",
            "No independent ratings",
        ):
            self.assertIn(fragment, text)

    def test_rejects_outreach(self):
        with self.assertRaises(ValueError):
            render([dict(self.good, outreach_authorized=True)])

    def test_rejects_duplicate_identity(self):
        with self.assertRaises(ValueError):
            render([self.good, self.good])

    def test_rejects_malformed_input(self):
        with self.assertRaises(ValueError):
            render({"candidates": [self.good]})


if __name__ == "__main__":
    unittest.main()
