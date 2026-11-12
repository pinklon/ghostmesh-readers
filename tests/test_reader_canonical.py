"""Forward visual and graph presentation checks for Reader #56 and later."""

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reader_canonical import errors  # noqa: E402
from generate_site import governed_reader_connections, evidence  # noqa: E402


class CanonicalReaderContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        cls.byid = {r["id"]: r for r in catalog["readers"]}
        cls.reference = next(r for r in catalog["readers"] if r["slug"] == "replacing-cowork-is-a-test-not-a-title")
        cls.html = (ROOT / "site" / cls.reference["slug"] / "index.html").read_text()
        cls.authored = (ROOT / "content/readers" / (cls.reference["slug"] + ".html")).read_text()

    def future(self, **extra):
        return {**self.reference, "slug": "future-reader-56", "published": "2026-11-12",
                "editorialOrder": 55, **extra}

    def test_approved_reference_satisfies_contract(self):
        self.assertEqual([], errors(self.reference, self.html))

    def test_future_reader_cannot_drop_back_matter(self):
        damaged = self.html.replace('class="gm-source-list"', 'class="plain-list"', 1)
        self.assertIn("class=gm-source-list", " ".join(errors(self.future(), damaged)))

    def test_missing_reader_work_section_cannot_silently_pass(self):
        damaged = self.html.replace('id="shareplane-thinking"', 'id="missing-shareplane-thinking"', 1)
        self.assertIn("id=shareplane-thinking", " ".join(errors(self.future(), damaged)))
        damaged = self.html.replace('id="related-thinking"', 'id="missing-related-thinking"', 1)
        self.assertIn("id=related-thinking", " ".join(errors(self.future(), damaged)))

    def test_admitted_edge_must_render_and_match_catalog(self):
        damaged = self.html.replace('class="gm-related-copy"', 'class="missing-reader-copy"', 1)
        self.assertIn("catalog-matched Reader connection card count", " ".join(errors(self.future(), damaged)))
        damaged = self.html.replace('class="gm-work-kind"', 'class="missing-work-kind"', 1)
        self.assertIn("catalog-matched SharePlane Work connection count", " ".join(errors(self.future(), damaged)))

    def test_reviewed_zero_stays_valid_but_visible(self):
        r = self.future(relationships=[], sharePlaneRelationships=[])
        page = governed_reader_connections(self.authored, r, self.byid).replace("<!--GM_EVIDENCE-->", evidence(r))
        self.assertIn('class="gm-route-empty"', page)
        self.assertEqual([], errors(r, page))
        damaged = page.replace('class="gm-route-empty"', 'class="missing-empty-receipt"', 1)
        self.assertIn("explicit reviewed-zero connection disposition", " ".join(errors(r, damaged)))

    def test_one_layer_can_be_empty_while_other_links(self):
        r = self.future(sharePlaneRelationships=[])
        page = governed_reader_connections(self.authored, r, self.byid).replace("<!--GM_EVIDENCE-->", evidence(r))
        self.assertEqual([], errors(r, page))
        self.assertIn("No SharePlane Work connection admitted", page)

    def test_paper_independent_study_is_not_mistaken_for_a_reader_edge(self):
        paper = self.future(source={"kind": "paper"}, references=[
            {"sourceType": "independent-different-construct-study"}])
        html = self.html.replace('<div class="gm-cards">', '<div class="gm-cards">'
                                 '<article><div class="gm-related-copy">Independent study</div></article>', 1)
        self.assertEqual([], errors(paper, html))

    def test_nonvideo_provenance_can_still_render_both_graph_planes(self):
        article = self.authored.replace('id="reasonpack-provenance"', 'id="paper-provenance"', 1)
        paper = self.future(source={"kind": "paper"})
        rendered = governed_reader_connections(article, paper, self.byid)
        self.assertIn('id="shareplane-thinking"', rendered)
        self.assertIn('id="paper-provenance"', rendered)

    def test_future_reader_needs_exactly_three_styled_brief_moves(self):
        self.assertEqual([], errors(self.future(), self.html))
        damaged = self.html.replace('class="gm-brief-point"', 'class="plain-brief-point"', 1)
        self.assertIn("exactly three styled brief moves", " ".join(errors(self.future(), damaged)))

    def test_future_reader_rejects_unstyled_table(self):
        plain = self.html.replace('</article>', '<table><tr><td>A</td><td>B</td><td>C</td></tr></table></article>', 1)
        self.assertIn("unstyled table", " ".join(errors(self.future(), plain)))
        styled = plain.replace('<table>', '<table class="comparison">', 1)
        self.assertIn("unstyled table", " ".join(errors(self.future(), styled)))
        wrapped = self.html.replace('</article>', '<div class="table-wrap"><table class="comparison">'
                                    '<tr><td>A</td><td>B</td><td>C</td></tr></table></div></article>', 1)
        self.assertEqual([], errors(self.future(), wrapped))

    def test_historical_reader_is_not_retroactively_blocked(self):
        old = self.future(slug="historical-reader", published="2026-11-09", editorialOrder=30)
        self.assertEqual([], errors(old, "<html></html>"))


if __name__ == "__main__":
    unittest.main()
