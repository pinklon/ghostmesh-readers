"""An article may cite multiple public records without masquerading as media."""
import copy
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import catalog_design
import generate_site
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
            self.raw.replace('<section id="sources">', '<section id="sources" hidden>'),
            self.raw.replace('<section id="sources">', '<section id="sources" style="display:none">'),
            self.raw.replace('<section id="sources">', '<section id="sources" aria-hidden="true">'),
            self.raw.replace('<a href="https://example.net/response">',
                             '<a hidden href="https://example.net/response">'),
            self.raw.replace('<a href="https://example.net/response">',
                             '<a style="visibility:hidden" href="https://example.net/response">'),
            self.raw.replace('<section id="sources">', '<div hidden><section id="sources">').replace('</section></main>', '</section></div></main>'),
            self.raw.replace('<section id="sources">', '<details><section id="sources">').replace('</section></main>', '</section></details></main>'),
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

    def test_analysis_flows_through_catalog_and_static_projections(self):
        """A temporary nineteenth article reaches every public route without changing the repository."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            shutil.copytree(ROOT / 'content', target / 'content')
            catalog_path = target / 'content/catalog.json'
            catalog = __import__('json').loads(catalog_path.read_text())
            old_slugs = {reader['slug'] for reader in catalog['readers']}
            article = copy.deepcopy(catalog['readers'][-1])
            article.update({
                'id': 'reader:source-analysis-fixture', 'slug': 'source-analysis-fixture',
                'title': 'A test of the records', 'published': '2026-10-20',
                'updated': '2026-10-20T00:00:00Z', 'editorialOrder': len(old_slugs),
                'overview': 'Two public records set up one bounded question.',
                'whyItMatters': 'Readers need to know where the evidence ends.',
                'ghostMeshTakeaway': 'Inspect both records before acting.',
                'source': copy.deepcopy(self.source), 'relationships': [],
                'relationshipDisposition': 'No local relationship is admitted.',
                'legacyReceipt': None,
            })
            article['source']['sourceReferenceIds'] = [article['references'][0]['id']]
            source_url = article['references'][0]['url']
            (target / 'content/readers/source-analysis-fixture.html').write_text(
                '<!doctype html><html lang="en"><head><title>A test of the records</title><!--GM_HEAD--></head>'
                '<body><header>Site header</header><main><h1>A test of the records</h1><!--GM_BRIEF-->'
                f'<section id="sources"><h2>Public records</h2><a href="{source_url}">Original record</a></section>'
                '<p>This is an original fixture about comparing a public record with its reported limits.</p>'
                '<!--GM_EVIDENCE--><!--GM_RELATED--></main><footer>Site footer</footer></body></html>'
            )
            catalog['readers'].append(article)
            catalog_path.write_text(__import__('json').dumps(catalog))
            old_root = generate_site.ROOT
            old_call = catalog_design.CALLS.get(article['slug'])
            try:
                generate_site.ROOT = target
                catalog_design.CALLS[article['slug']] = ('Inspect the records', 'Compare the cited public records.')
                pages = generate_site.projections()
            finally:
                generate_site.ROOT = old_root
                if old_call is None:
                    catalog_design.CALLS.pop(article['slug'], None)
                else:
                    catalog_design.CALLS[article['slug']] = old_call
            rendered = pages['source-analysis-fixture/index.html']
            self.assertIn('What the records establish', rendered)
            self.assertIn('id="sources"', rendered)
            self.assertIn(source_url, rendered)
            self.assertNotIn('data-gm-aspect', rendered)
            self.assertIn('/source-analysis-fixture/#sources', pages['index.html'])
            self.assertIn('/source-analysis-fixture/#sources', pages['readers/index.html'])
            self.assertIn('reader:source-analysis-fixture', pages['source-analysis-fixture/receipt.json'])
            self.assertIn('/source-analysis-fixture/', pages['readers/search-index.json'])
            self.assertIn('/source-analysis-fixture/', pages['sitemap.xml'])
            self.assertTrue({slug + '/index.html' for slug in old_slugs} <= set(pages))

if __name__ == "__main__":
    unittest.main()
