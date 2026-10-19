import json
import unittest
from collections import Counter
from pathlib import Path

from scripts.generate_site import PublicArticleText


ROOT = Path(__file__).resolve().parents[1]


class SearchAndEvidenceAuditTest(unittest.TestCase):
    def test_index_is_exactly_public_reader_article_text(self):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        index = json.loads((ROOT / "site/readers/search-index.json").read_text())
        self.assertEqual(index["schema"], "ghostmesh-public-reader-text-v1")
        self.assertEqual(index["readerCount"], len(catalog["readers"]))
        self.assertEqual(len(index["readers"]), len(catalog["readers"]))
        self.assertEqual({entry["url"] for entry in index["readers"]},
                         {f"/{reader['slug']}/" for reader in catalog["readers"]})
        for entry in index["readers"]:
            parser = PublicArticleText()
            parser.feed((ROOT / "site" / entry["url"].strip("/") / "index.html").read_text())
            self.assertEqual(entry["text"], parser.text())
            self.assertNotIn("<iframe", entry["text"])
            self.assertNotIn("<script", entry["text"])
        new_reader = next(entry for entry in index["readers"]
                          if entry["id"] == "reader:the-fleet-does-not-prove-the-forecast")
        body_only_phrase = "false positives and useful work lost"
        self.assertIn(body_only_phrase, new_reader["text"])
        self.assertNotIn(body_only_phrase, (ROOT / "content/catalog.json").read_text())
        self.assertNotIn(body_only_phrase, (ROOT / "site/readers/index.html").read_text())

    def test_existing_claim_status_breakdown_is_explicit(self):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        baseline = json.loads((ROOT / "docs/baseline-audit.json").read_text())
        historical_slugs = {reader["slug"] for reader in baseline["readers"]}
        claims = [claim for reader in catalog["readers"] if reader["slug"] in historical_slugs
                  for claim in reader["claims"]]
        self.assertEqual(Counter(claim["status"] for claim in claims),
                         {"unverified": 131, "partially corroborated": 14,
                          "corroborated": 2, "contradicted": 1})
        unverified = [claim for claim in claims if claim["status"] == "unverified"]
        self.assertEqual(sum(c["kind"] == "historical-ledger-entry" for c in unverified), 64)
        self.assertEqual(sum(c["kind"] == "material-prose-claim" for c in unverified), 33)
        self.assertEqual(sum(bool(c["references"]) for c in claims), 16)
        self.assertEqual(sum(bool(c["counterevidence"]) for c in claims), 6)
        knowledge = (ROOT / "site/knowledge/index.html").read_text()
        current_unverified = sum(c["status"] == "unverified"
                                 for reader in catalog["readers"] for c in reader["claims"])
        self.assertIn(f"<strong>{current_unverified}</strong><span>still labeled unverified", knowledge)
        self.assertIn("64 are historical-ledger entries and 33 are material-prose claims", knowledge)


if __name__ == "__main__":
    unittest.main()
