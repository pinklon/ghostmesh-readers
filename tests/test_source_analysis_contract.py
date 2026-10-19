"""An article may cite multiple public records without masquerading as media."""
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from catalog_design import analysis_cover, _poster
from generate_site import brief, home_card, validate_analysis_source


class SourceAnalysisContractTests(unittest.TestCase):
    def setUp(self):
        self.reader = {
            "slug": "source-analysis-fixture", "title": "A test of the records",
            "category": "Science", "published": "2026-10-19", "rank": 18,
            "overview": "The records make two limited claims.",
            "whyItMatters": "The choice depends on both records.",
            "ghostMeshTakeaway": "Compare evidence before acting.",
            "verdict": "Worth studying", "evidenceState": "mixed", "architectureImpact": "none",
            "tags": ["Evidence"], "claims": [{"status": "unverified"}],
            "references": [
                {"id": "primary", "url": "https://example.org/study"},
                {"id": "counter", "url": "https://example.net/response"},
            ],
        }
        self.source = {
            "kind": "analysis", "identity": "analysis:source-analysis-fixture",
            "sourceReferenceIds": ["primary", "counter"],
        }
        self.reader["source"] = self.source
        self.raw = ('<main><section id="at-a-glance"></section>'
                    '<section id="sources"><h2>Public records</h2>'
                    '<a href="https://example.org/study">Study</a>'
                    '<a href="https://example.net/response">Response</a></section>'
                    '</main><script src="/assets/reader-share.js" defer></script>')

    def test_declared_records_need_exact_links_in_one_source_section(self):
        validate_analysis_source(self.raw, self.source, self.reader)
        for raw in (
            self.raw.replace('id="sources"', 'id="background"'),
            self.raw.replace('https://example.net/response', 'https://example.net/other'),
            self.raw.replace('</section></main>', '</section><section id="sources"></section></main>'),
            self.raw.replace('<a href="https://example.net/response">Response</a>',
                             '</section><a href="https://example.net/response">Response</a>'),
        ):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                validate_analysis_source(raw, self.source, self.reader)

    def test_rejects_identity_confusion_and_unsafe_references(self):
        for change in (
            {"identity": "analysis:other"}, {"sourceReferenceIds": ["primary", "missing"]},
            {"sourceReferenceIds": ["primary", "primary"]}, {"platform": "YouTube"},
            {"mediaAspect": "unknown"}, {"pdfUrl": "https://example.org/file.pdf"},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_analysis_source(self.raw, {**self.source, **change}, self.reader)
        for url in ("http://example.org/study", "https://name:pass@example.org/study", "javascript:alert(1)"):
            reader = copy.deepcopy(self.reader)
            reader["references"][0]["url"] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_analysis_source(self.raw, self.source, reader)

    def test_source_analysis_has_no_media_or_active_document(self):
        for marker in (
            '<iframe src="https://example.org/study"></iframe>',
            '<video src="/assets/clip.mp4"></video>',
            '<img src="https://example.org/page.png" alt="">',
            '<script src="https://example.org/code.js"></script>',
            '<button data-home-play type="button">Play</button>',
        ):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                validate_analysis_source(self.raw + marker, self.source, self.reader)

    def test_brief_and_catalog_route_are_analysis_specific(self):
        self.assertIn("What the records establish", brief(self.reader))
        self.assertNotIn("What the video is about", brief(self.reader))
        self.assertIn("SOURCE ANALYSIS", analysis_cover())
        self.assertEqual(_poster(self.reader), analysis_cover())
        card = home_card(self.reader, 1)
        self.assertIn('/source-analysis-fixture/#sources', card)
        self.assertIn('Inspect source records', card)
        self.assertNotIn('data-home-player', card)
        self.assertNotIn('Original paper', card)

if __name__ == "__main__":
    unittest.main()
