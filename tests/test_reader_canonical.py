"""Prevent future Readers from silently regressing to raw manuscript back matter."""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reader_canonical import errors  # noqa: E402


class CanonicalReaderContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        cls.reference = next(r for r in catalog["readers"] if r["slug"] == "when-every-ai-website-looks-good")
        cls.html = (ROOT / "site" / cls.reference["slug"] / "index.html").read_text()

    def test_approved_reference_satisfies_contract(self):
        self.assertEqual([], errors(self.reference, self.html))

    def test_future_reader_cannot_drop_back_matter(self):
        future = {**self.reference, "slug": "future-reader", "published": "2026-11-11"}
        damaged = self.html.replace('class="gm-source-list"', 'class="plain-list"', 1)
        self.assertIn("class=gm-source-list", " ".join(errors(future, damaged)))

    def test_existing_reader_is_not_retroactively_blocked(self):
        old = {**self.reference, "slug": "historical-reader", "published": "2026-11-09"}
        self.assertEqual([], errors(old, "<html></html>"))


if __name__ == "__main__":
    unittest.main()
