import copy
import hashlib
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scout_feed import feed_xml, validate_events, validate_scout
from scout_pages import validate_editions, prose_html, review_page, archive_page


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
                'sourceType': 'repository', 'topic': 'code-review', 'audience': 'Developers',
                'recommendation': 'watch', 'selectionRationale': 'Compare its evidence rules.',
                'discovery': {'route': 'explicit-research-priority',
                              'evidenceUrl': 'https://youtube.shareplane.malott.ai/scout/method/#priority',
                              'retainedHistoryUrl': 'https://youtube.shareplane.malott.ai/scout/method/#history',
                              'firstRetainedObservation': '2026-10-21T14:30:55+00:00',
                              'originalDiscovery': 'not-recorded'}, 'priorReviews': [],
                'ratings': {name: copy.deepcopy(rating) for name in
                            ('ghostmeshFit', 'everydayUse', 'evidenceStrength', 'adoptionEffort')}}

    def test_first_report_binds_reviewed_sources_and_release_events(self):
        card_bytes = (ROOT / 'content/scout-public.json').read_bytes()
        source = json.loads(card_bytes)
        self.assertEqual(hashlib.sha256(card_bytes).hexdigest(), '5f8f5ec602f097f4b0fca7d76fc55167d344301c03fbf8fcfb07125f361ec0b9')
        self.assertEqual([r['id'] for r in source['reviews']],
                         ['cloudflare-security-audit-skill', 'graphify-labs-graphify', 'nvidia-openshell'])
        self.assertEqual([r['method'] for r in source['reviews']],
                         ['source-inspected', 'metadata-reviewed', 'metadata-reviewed'])
        editions = validate_editions(json.loads((ROOT / 'content/scout-editions.json').read_text()), source)
        self.assertEqual(editions['editions'][0]['reviewIds'], [r['id'] for r in source['reviews']])
        html = (ROOT / 'site/scout/index.html').read_text()
        self.assertIn('Borrow the discipline. Make the machinery earn its place.', html)
        self.assertEqual(html.count('class="gm-scout-feature"'), 3)
        self.assertIn('href="/scout/archive/"', html)
        self.assertIn('href="/scout/method/"', html)
        self.assertNotIn('Ratings with their limits', html)
        self.assertIn('href="/feed.xml"', html)
        for review in source['reviews']:
            path = ROOT / 'site/scout/reviews' / review['id'] / 'index.html'
            detail = path.read_text()
            self.assertIn(review['title'], detail)
            self.assertLess(detail.index('01 / What it is'), detail.index('03 / Our provisional call'))
            self.assertIn('original discovery circumstances were not recorded', detail)
            self.assertIn('Current editorial rationale', detail)
            self.assertIn('href="/scout/method/#section-how-a-candidate-enters-view"', detail)
            self.assertIn('Ratings with their limits', detail)
            self.assertIn('No earlier Scout review record.', detail)
            self.assertIn(review['sourceUrl'], detail)
            self.assertNotIn('/Users/', detail)
            self.assertNotIn('pinklon/skills', detail)
        edition = (ROOT / 'site/scout/editions/2026-10-22-first-look/index.html').read_text()
        self.assertIn('What would change our recommendations?', edition)
        self.assertEqual(edition.count('class="gm-scout-prose-identity"'), 0)
        archive = (ROOT / 'site/scout/archive/index.html').read_text()
        self.assertEqual(archive.count('class="gm-scout-archive-card"'), 3)
        self.assertIn('id="scout-query"', archive)
        self.assertIn('id="scout-topic"', archive)
        self.assertIn('id="scout-call"', archive)
        self.assertIn('scout-archive.js', archive)
        method = (ROOT / 'site/scout/method/index.html').read_text()
        self.assertIn('explicit priorities', method)
        self.assertIn('not retained', method)
        self.assertNotIn('pinklon/skills', method)
        self.assertEqual(validate_scout(source), source)
        events = json.loads((ROOT / 'content/public-release-events.json').read_text())
        self.assertEqual(validate_events(events, self.catalog, source), events)
        self.assertEqual([event['subjectId'] for event in events['events'] if event['kind'] == 'new-scout-review'],
                         [review['id'] for review in source['reviews']])
        self.assertEqual(sum(event['kind'] == 'new-reader' and event['subjectId'] == 'reader:what-a-swarm-makes-us-see'
                             for event in events['events']), 1)
        wsj_id = 'reader:the-missing-step-is-not-more-intelligence:first-public-release'
        wsj_events = [event for event in events['events'] if event['id'] == wsj_id]
        self.assertEqual(len(wsj_events), 1)
        self.assertEqual(wsj_events[0]['releasedAt'], '2026-10-24T14:24:37.701Z')
        orca_id = 'reader:the-fleet-needs-a-control-plane:first-public-release'
        orca_events = [event for event in events['events'] if event['id'] == orca_id]
        self.assertEqual(len(orca_events), 1)
        self.assertEqual(orca_events[0]['publicDate'], '2026-10-24')
        self.assertNotIn('releasedAt', orca_events[0])
        webhook_id = 'reader:when-a-successful-run-is-still-waiting:first-public-release'
        webhook_events = [event for event in events['events'] if event['id'] == webhook_id]
        self.assertEqual(len(webhook_events), 1)
        self.assertEqual(webhook_events[0]['publicDate'], '2026-10-25')
        self.assertEqual(webhook_events[0]['summary'],
                         next(reader for reader in self.catalog['readers']
                              if reader['id'] == webhook_events[0]['subjectId'])['overview'])
        self.assertNotIn('releasedAt', webhook_events[0])
        earlier = [event for event in events['events'] if event['id'] not in {wsj_id, orca_id, webhook_id}]
        self.assertEqual({event['publicDate'] for event in earlier}, {'2026-10-22', '2026-10-23'})
        self.assertTrue(all('releasedAt' not in event for event in earlier))

    def test_report_renderer_escapes_html_and_rejects_missing_cards(self):
        rendered = prose_html('# Title\n\n## Example\n\n**Recommendation:** [Read](https://example.org/?a=1&b=2) <script>')
        self.assertIn('href="https://example.org/?a=1&amp;b=2"', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)
        with self.assertRaisesRegex(ValueError, 'title required'):
            prose_html('No title')

    def test_editions_and_discovery_fail_closed(self):
        scout = validate_scout(json.loads((ROOT / 'content/scout-public.json').read_text()))
        editions = json.loads((ROOT / 'content/scout-editions.json').read_text())
        invalid = copy.deepcopy(editions)
        invalid['editions'][0]['reviewIds'].append('missing-review')
        with self.assertRaisesRegex(ValueError, 'edition reviews'):
            validate_editions(invalid, scout)
        invalid = copy.deepcopy(scout)
        invalid['reviews'][0]['discovery']['route'] = 'popular-winner'
        with self.assertRaisesRegex(ValueError, 'discovery provenance'):
            validate_scout(invalid)
        invalid = copy.deepcopy(scout)
        invalid['reviews'][0]['recommendation'] = 'adopt-now'
        with self.assertRaisesRegex(ValueError, 'classification'):
            validate_scout(invalid)

    def test_review_requires_source_linked_rationale_and_escapes_markup(self):
        source = {'schema': 'ghostmesh-public-scout-v1', 'reviews': [self.review()]}
        validate_scout(source)
        html = review_page(self.review(), '# Fixture\n\nA public analysis.')
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
                 'subjectId': 'fixture-tool', 'url': host + '/scout/reviews/fixture-tool/',
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
        items = ET.parse(site / 'feed.xml').getroot().findall('./channel/item')
        events = json.loads((ROOT / 'content/public-release-events.json').read_text())['events']
        self.assertEqual(len(items), len(events))
        self.assertEqual(len({item.findtext('guid') for item in items}), len(events))
        self.assertEqual(sum(item.find('pubDate') is not None for item in items),
                         sum('releasedAt' in event for event in events))
        wsj_guid = 'urn:ghostmesh-readers:release:reader:the-missing-step-is-not-more-intelligence:first-public-release'
        wsj_items = [item for item in items if item.findtext('guid') == wsj_guid]
        self.assertEqual(len(wsj_items), 1)
        self.assertEqual(wsj_items[0].findtext('pubDate'), 'Sat, 24 Oct 2026 14:24:37 +0000')
        self.assertEqual({item.findtext('link') for item in items}, {event['url'] for event in events})
        self.assertIn('Content-Type: application/rss+xml', (site / '_headers').read_text())


if __name__ == '__main__':
    unittest.main()
