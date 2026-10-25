"""Written sources retain their identity and direct route without invented media."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from generate_site import validate_article_source


class WrittenArticleSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        cls.record = next(r for r in catalog["readers"] if r["slug"] == "the-commit-is-not-the-control")
        cls.source = cls.record["source"]
        cls.raw = (ROOT / "content/readers/the-commit-is-not-the-control.html").read_text()

    def test_exact_original_and_no_fabricated_player(self):
        self.assertEqual("article", self.source["kind"])
        self.assertEqual("2026-10-13", self.source["publicationDate"])
        self.assertEqual("2026-10-15", self.source["updatedDate"])
        self.assertEqual("https://www.anthropic.com/research/redesigning-source-control", self.source["url"])
        self.assertNotIn("transcript", self.raw.lower())
        self.assertNotIn("<iframe", self.raw.lower())
        validate_article_source(self.raw, self.source)

    def test_active_embed_wrong_original_and_false_date_are_rejected(self):
        cases = [
            (self.raw + '<iframe src="https://example.org"></iframe>', self.source),
            (self.raw, {**self.source, "url": "https://example.org/different"}),
            (self.raw, {**self.source, "updatedDate": "2026-10-12"}),
            (self.raw, {**self.source, "mediaAspect": "16:9"}),
        ]
        for raw, source in cases:
            with self.subTest(source=source, active="iframe" in raw), self.assertRaises(ValueError):
                validate_article_source(raw, source)

    def test_generated_route_is_written_source_only(self):
        page = (ROOT / "site/the-commit-is-not-the-control/index.html").read_text()
        self.assertIn("What the article argues", page)
        self.assertIn('href="https://www.anthropic.com/research/redesigning-source-control"', page)
        self.assertNotIn("data-home-player", page)
        self.assertNotIn("gm-media-frame", page)
        self.assertNotIn("data-paper-frame", page)

    def test_living_documentation_can_disclose_unknown_first_publication(self):
        source = {**self.source, "publicationDate": "unknown", "dateNote": "Original publication date unknown; the inspected revision was dated later."}
        validate_article_source(self.raw, source)
        with self.assertRaises(ValueError):
            validate_article_source(self.raw, {**source, "dateNote": "Inspected revision date only."})


if __name__ == "__main__":
    unittest.main()
