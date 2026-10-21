import copy
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scout_feed import feed_xml, scout_body, validate_events, validate_scout


class ScoutFeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads((ROOT / 'content/catalog.json').read_text())

    def review(self):
        rating = {'value': 'mixed', 'rationale': 'A source-linked, bounded assessment.',
                  'evidenceUrls': ['https://example.org/source?a=1&b=2']}
        return {'id': 'fixture-tool', 'title': 'Tool <fixture>', 'sourceUrl': 'https://example.org/tool',
                'reviewedOn': '2026-10-21', 'method': 'source-inspected', 'confidence': 'low',
                'summary': 'A bounded review <not a runtime test>.', 'unknowns': 'Runtime behavior remains unknown.',
                'ratings': {name: copy.deepcopy(rating) for name in
                            ('ghostmeshFit', 'everydayUse', 'evidenceStrength', 'adoptionEffort')}}

    def test_initial_public_page_is_honest_and_no_private_watchlist_is_ingested(self):
        source = json.loads((ROOT / 'content/scout-public.json').read_text())
        self.assertEqual(source['reviews'], [])
        html = (ROOT / 'site/scout/index.html').read_text()
        self.assertIn('No Scout candidate review has been approved', html)
        self.assertIn('href="/feed.xml"', html)
        self.assertNotIn('Cloudflare security-audit-skill', html)
        self.assertEqual(validate_scout(source), source)

    def test_review_requires_source_linked_rationale_and_escapes_markup(self):
        source = {'schema': 'ghostmesh-public-scout-v1', 'reviews': [self.review()]}
        validate_scout(source)
        html = scout_body(source)
        self.assertIn('Tool &lt;fixture&gt;', html)
        self.assertNotIn('Tool <fixture>', html)
        self.assertIn('a=1&amp;b=2', html)
        self.assertIn('source inspected', html)
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
        mismatch = copy.deepcopy(source)
        mismatch['events'][0]['url'] = host + '/other/'
        with self.assertRaisesRegex(ValueError, 'Reader identity'):
            validate_events(mismatch, self.catalog, scout)
        moved = copy.deepcopy(source)
        moved['events'][1]['releasedAt'] = '2026-10-19T11:45:00Z'
        with self.assertRaisesRegex(ValueError, 'match public date'):
            validate_events(moved, self.catalog, scout)

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
