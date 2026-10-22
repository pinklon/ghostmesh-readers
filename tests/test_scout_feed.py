import copy
import hashlib
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scout_feed import feed_xml, scout_body, scout_report_html, validate_events, validate_scout


class ScoutFeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / 'content/catalog.json').read_text())

    def review(self):
        rating = {'value': 'mixed', 'rationale': 'A source-linked, bounded assessment.',
                  'evidenceUrls': ['https://example.org/source?a=1&b=2']}
        return {'id': 'fixture-tool', 'title': 'Tool <fixture>', 'sourceUrl': 'https://example.org/tool',
                'reviewedOn': '2026-10-21', 'method': 'source-inspected', 'confidence': 'low',
                'identity': 'A developer tool <fixture> for code review.',
                'scope': 'Read its public source; no execution.',
                'summary': 'A bounded review <not a runtime test>.', 'unknowns': 'Runtime behavior remains unknown.',
                'ratings': {name: copy.deepcopy(rating) for name in
                            ('ghostmeshFit', 'everydayUse', 'evidenceStrength', 'adoptionEffort')}}

    def test_first_report_preview_binds_reviewed_sources_without_release_event(self):
        card_bytes = (ROOT / 'content/scout-public.json').read_bytes()
        source = json.loads(card_bytes)
        self.assertEqual(hashlib.sha256(card_bytes).hexdigest(), 'a8d75dd8b1470f421277aff83c885299b7d1e8d4be8e251297bf3a179ca5893e')
        self.assertEqual([r['id'] for r in source['reviews']],
                         ['cloudflare-security-audit-skill', 'graphify-labs-graphify', 'nvidia-openshell'])
        self.assertEqual([r['method'] for r in source['reviews']],
                         ['source-inspected', 'metadata-reviewed', 'metadata-reviewed'])
        report = (ROOT / 'content/scout-first-report.md').read_bytes()
        self.assertEqual(hashlib.sha256(report).hexdigest(), 'cbd35c1fd13707a869b1f8834b6a131776415696c83cc2405fd9181a73adfcfd')
        html = (ROOT / 'site/scout/index.html').read_text()
        self.assertIn('Borrow the discipline. Make the machinery earn its place.', html)
        self.assertLess(html.index('id="cloudflare-security-audit-skill"'),
                        html.index('id="graphify-labs-graphify"'))
        self.assertLess(html.index('id="graphify-labs-graphify"'),
                        html.index('id="nvidia-openshell"'))
        self.assertEqual(html.count('class="gm-scout-card"'), 3)
        self.assertIn('Ratings, rationale and limits', html)
        self.assertIn('FIRST LOOK / THREE PROJECTS', html)
        for review in source['reviews']:
            card = html.split('id="' + review['id'] + '"', 1)[1].split('</article>', 1)[0]
            self.assertLess(card.index('gm-scout-identity'), card.index('gm-scout-recommendation'))
            self.assertLess(card.index('gm-scout-scope'), card.index('gm-scout-recommendation'))
            self.assertNotIn(review['summary'], card)
            analysis = 'report-' + review['title'].lower().replace(' ', '-')
            self.assertIn('href="#' + analysis + '"', card)
            self.assertIn('id="' + analysis + '"', html)
        self.assertIn('No candidate was installed or executed', html)
        self.assertNotIn('Three independently identified repositories, reviewed at the linked revisions.', html)
        self.assertIn('href="/feed.xml"', html)
        self.assertIn('aria-labelledby="follow-scout-title"', html)
        self.assertIn('New Readers, meaningful Reader updates and published Scout reviews', html)
        self.assertIn('class="gm-scout-subscribe" href="/feed.xml"', html)
        self.assertIn('grid-template-columns:1fr;gap:28px', (ROOT / 'site/assets/scout.css').read_text())
        self.assertNotIn('/Users/', html)
        self.assertNotIn('private scout artifact', html.lower())
        self.assertEqual(validate_scout(source), source)
        self.assertEqual(json.loads((ROOT / 'content/public-release-events.json').read_text())['events'], [])

    def test_report_renderer_escapes_html_and_rejects_missing_cards(self):
        rendered = scout_report_html('# Title\n\n## Example\n\n**Recommendation:** [Read](https://example.org/?a=1&b=2) <script>')
        self.assertIn('href="https://example.org/?a=1&amp;b=2"', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)
        with self.assertRaisesRegex(ValueError, 'requires reviewed cards'):
            scout_body({'reviews': []}, rendered)

    def test_review_requires_source_linked_rationale_and_escapes_markup(self):
        source = {'schema': 'ghostmesh-public-scout-v1', 'reviews': [self.review()]}
        validate_scout(source)
        html = scout_body(source)
        self.assertIn('Tool &lt;fixture&gt;', html)
        self.assertNotIn('Tool <fixture>', html)
        self.assertIn('a=1&amp;b=2', html)
        self.assertIn('source inspected', html)
        self.assertIn('A developer tool &lt;fixture&gt;', html)
        self.assertIn('Read its public source; no execution.', html)
        bad = copy.deepcopy(source)
        bad['reviews'][0]['ratings']['everydayUse']['evidenceUrls'] = []
        with self.assertRaisesRegex(ValueError, 'source links required'):
            validate_scout(bad)
        bad = copy.deepcopy(source)
        bad['reviews'][0]['summary'] = '/Users/private/transcript.txt'
        with self.assertRaisesRegex(ValueError, 'private text'):
            validate_scout(bad)
        bad = copy.deepcopy(source)
        bad['reviews'][0]['method'] = 'runtime-tested'
        with self.assertRaisesRegex(ValueError, 'method'):
            validate_scout(bad)

    def test_stable_distinct_release_ids_do_not_change_on_rebuild(self):
        reader = self.catalog['readers'][0]
        host = self.catalog['host']
        first = {'id': reader['id'] + ':first-public-release', 'kind': 'new-reader',
                 'subjectId': reader['id'], 'url': host + '/' + reader['slug'] + '/',
                 'title': 'New Reader & source', 'summary': 'A reviewed reading <not a transcript>.',
                 'publicDate': '2026-10-19'}
        second = {**first, 'id': reader['id'] + ':substantive-revision-one',
                  'kind': 'material-reader-update', 'publicDate': '2026-10-20',
                  'releasedAt': '2026-10-20T11:45:00Z'}
        source = {'schema': 'ghostmesh-public-release-events-v1', 'events': [first, second]}
        scout = {'schema': 'ghostmesh-public-scout-v1', 'reviews': []}
        validate_events(source, self.catalog, scout)
        rendered = feed_xml(source, host)
        self.assertEqual(rendered, feed_xml(source, host))
        parsed = ET.fromstring(rendered)
        items = parsed.findall('./channel/item')
        self.assertEqual(len(items), 2)
        self.assertEqual(len({item.findtext('guid') for item in items}), 2)
        self.assertEqual(len([item for item in items if item.find('pubDate') is not None]), 1)
        self.assertIn('New Reader &amp; source', rendered)
        self.assertIn('&lt;not a transcript&gt;', rendered)
        duplicate = copy.deepcopy(source)
        duplicate['events'].append(first)
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            validate_events(duplicate, self.catalog, scout)
        repeated_first = copy.deepcopy(source)
        repeated_first['events'].append({**first, 'id': reader['id'] + ':another-first',
                                         'publicDate': '2026-10-20'})
        with self.assertRaisesRegex(ValueError, 'Duplicate first public release'):
            validate_events(repeated_first, self.catalog, scout)
        control = copy.deepcopy(source)
        control['events'][0]['summary'] = 'invalid\x00XML'
        with self.assertRaisesRegex(ValueError, 'private text'):
            validate_events(control, self.catalog, scout)
        mismatch = copy.deepcopy(source)
        mismatch['events'][0]['url'] = host + '/other/'
        with self.assertRaisesRegex(ValueError, 'Reader identity'):
            validate_events(mismatch, self.catalog, scout)
        moved = copy.deepcopy(source)
        moved['events'][1]['releasedAt'] = '2026-10-19T11:45:00Z'
        with self.assertRaisesRegex(ValueError, 'match public date'):
            validate_events(moved, self.catalog, scout)

    def test_one_first_scout_review_per_subject(self):
        scout = {'schema': 'ghostmesh-public-scout-v1', 'reviews': [self.review()]}
        host = self.catalog['host']
        first = {'id': 'scout:fixture-tool:first-review', 'kind': 'new-scout-review',
                 'subjectId': 'fixture-tool', 'url': host + '/scout/#fixture-tool',
                 'title': 'First review', 'summary': 'A bounded public assessment.',
                 'publicDate': '2026-10-20'}
        source = {'schema': 'ghostmesh-public-release-events-v1', 'events': [first]}
        validate_events(source, self.catalog, scout)
        source['events'].append({**first, 'id': 'scout:fixture-tool:other-first'})
        with self.assertRaisesRegex(ValueError, 'Duplicate first public release'):
            validate_events(source, self.catalog, scout)

    def test_static_projection_links_scout_and_rss_without_event_churn(self):
        site = ROOT / 'site'
        for route in ('index.html', 'readers/index.html', 'the-inbox-was-a-boundary/index.html'):
            page = (site / route).read_text()
            self.assertIn('href="/scout/"', page)
            self.assertIn('type="application/rss+xml"', page)
        self.assertIn(self.catalog['host'] + '/scout/', (site / 'sitemap.xml').read_text())
        self.assertEqual(ET.parse(site / 'feed.xml').getroot().findall('./channel/item'), [])
        self.assertIn('Content-Type: application/rss+xml', (site / '_headers').read_text())


if __name__ == '__main__':
    unittest.main()
