"""Canonical Reader and SharePlane map layers, without inferred cross-site admission."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReaderMapLayersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / "content/catalog.json").read_text())
        cls.graph = json.loads((ROOT / "site/map/relationships.json").read_text())
        cls.html = (ROOT / "site/map/index.html").read_text()

    def test_canonical_counts_and_separate_namespace(self):
        readers = self.catalog["readers"]
        self.assertEqual(self.graph["readerCount"], len(readers))
        self.assertEqual(self.graph["relationshipCount"], sum(len(r["relationships"]) for r in readers))
        external = sum(len(r.get("sharePlaneRelationships", [])) for r in readers)
        self.assertEqual(self.graph["sharePlaneRelationshipCount"], external)
        self.assertEqual(len(self.graph["sharePlaneEdges"]), external)
        self.assertGreaterEqual(external, 3)
        self.assertEqual(self.graph["sharePlaneReviewCount"], sum(bool(r.get("sharePlaneReview")) for r in readers))

    def test_new_editions_require_both_reviews(self):
        for reader in self.catalog["readers"]:
            if reader["editorialOrder"] < 40:
                continue
            self.assertIn("sharePlaneReview", reader)
            self.assertEqual(reader["sharePlaneReview"]["decision"], "linked" if reader["sharePlaneRelationships"] else "none")
            self.assertEqual(reader["relationshipReview"]["decision"], "linked" if reader["relationships"] else "none")

    def test_local_reader_edges_are_not_external_graph_edges(self):
        self.assertTrue(all(edge["to"].startswith("reader:") for edge in self.graph["edges"]))
        self.assertTrue(all(edge["url"].startswith("https://shareplane.malott.ai/artifacts/") for edge in self.graph["sharePlaneEdges"]))
        self.assertIn("Reader connections", self.html)
        self.assertIn("SharePlane Works", self.html)
        self.assertIn("not automatically admitted into the SharePlane graph", self.html)


if __name__ == "__main__":
    unittest.main()
