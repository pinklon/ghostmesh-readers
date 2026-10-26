import copy
from datetime import datetime, timezone
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scout_research import validate_research, research_page, research_graph, publication_label, LEGACY_PUBLIC_BY_IDS
from check_scout_routine_release import check_delta


class ScoutResearchTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((ROOT/'content/scout-research.json').read_text())
        self.scout = json.loads((ROOT/'content/scout-public.json').read_text())
        self.events = json.loads((ROOT/'content/public-release-events.json').read_text())

    def validate(self, source):
        return validate_research(source, self.scout, self.events, ROOT)

    def test_standing_release_requires_independent_source_bound_public_copy(self):
        day = datetime.now(timezone.utc).date().isoformat()
        slug = 'synthetic-official-change'
        url = 'https://example.org/official/release'
        page = ('<!doctype html><html><head><link rel="canonical" '
                'href="https://youtube.shareplane.malott.ai/scout/essays/' + slug + '/"></head>'
                '<body><article data-scout-source-report="v1"><h1>Official change</h1>'
                '<p>Source-reported; not independently tested</p><a href="' + url + '">'
                'Primary source</a><time datetime="' + day + '">' + day + '</time>'
                '</article></body></html>')
        item = {'id': 'report:' + slug, 'slug': slug, 'type': 'source-report',
                'status': 'published', 'title': 'Official change',
                'url': '/scout/essays/' + slug + '/',
                'sourcePath': 'site/scout/essays/' + slug + '/index.html',
                'provenance': url, 'evidenceLimits': 'Source announcement only; no test.',
                'summary': 'The source reports a change.', 'topics': ['research'],
                'reviewedOn': day, 'releaseEventId': 'scout:' + slug + ':first-public-release',
                'relatedIds': [], 'standingRelease': 'routine-source-report-v1'}
        event = {'id': item['releaseEventId'], 'kind': 'new-scout-research',
                 'subjectId': slug, 'url': 'https://youtube.shareplane.malott.ai' + item['url'],
                 'title': item['title'], 'summary': item['summary'], 'publicDate': day}
        review = {'schema': 'ghostmesh-scout-source-report-review-v1',
                  'policy': 'routine-source-report-v1', 'researchId': item['id'],
                  'sourceUrl': url, 'observedOn': day, 'reviewedOn': day,
                  'sourceMethod': 'official-release-note',
                  'sourceSha256': hashlib.sha256(page.encode()).hexdigest(),
                  'reviewerTask': 'independent-reviewer', 'publisherTask': 'sole-publisher',
                  'decision': 'accept', 'sourceReportedOnly': True,
                  'noNewRecommendation': True, 'noExecutionOrEntitlementClaim': True,
                  'publicSafe': True, 'title': item['title'],
                  'summary': item['summary'], 'evidenceLimits': item['evidenceLimits'],
                  'topics': item['topics']}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_file = root/item['sourcePath']
            review_file = root/f'content/scout/release-reviews/{slug}.json'
            source_file.parent.mkdir(parents=True)
            review_file.parent.mkdir(parents=True)
            source_file.write_text(page)
            review_file.write_text(json.dumps(review))
            source = {'schema': 'ghostmesh-scout-research-v1', 'records': [item]}
            events = {'events': [event]}
            self.assertEqual(validate_research(source, {'reviews': []}, events, root), source)
            item['summary'] = 'Unreviewed recommendation.'
            with self.assertRaisesRegex(ValueError, 'review binding'):
                validate_research(source, {'reviews': []}, events, root)
            item['summary'] = event['summary']
            event['summary'] = 'Unreviewed RSS recommendation.'
            with self.assertRaisesRegex(ValueError, 'event copy differs'):
                validate_research(source, {'reviews': []}, events, root)
            event['summary'] = item['summary']
            item['id'] = 'essay:' + slug
            with self.assertRaisesRegex(ValueError, 'report identity'):
                validate_research(source, {'reviews': []}, events, root)
            item['id'] = review['researchId']
            invisible_pages = (
                page.replace('<p>Source-reported; not independently tested</p>',
                             '<p hidden>Source-reported; not independently tested</p>'),
                page.replace('<p>Source-reported; not independently tested</p>',
                             '<p style="visibility: hidden">Source-reported; not independently tested</p>'),
                page.replace('>Primary source</a>', '></a>'),
                page.replace('>' + day + '</time>', '></time>'),
            )
            for invisible in invisible_pages:
                source_file.write_text(invisible)
                review['sourceSha256'] = hashlib.sha256(invisible.encode()).hexdigest()
                review_file.write_text(json.dumps(review))
                with self.assertRaisesRegex(ValueError, 'public wrapper'):
                    validate_research(source, {'reviews': []}, events, root)
            source_file.write_text(page)
            review['sourceSha256'] = hashlib.sha256(page.encode()).hexdigest()
            review_file.write_text(json.dumps(review))
            review['reviewerTask'] = review['publisherTask']
            review_file.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, 'reviewer independence'):
                validate_research(source, {'reviews': []}, events, root)
            review['reviewerTask'] = 'independent-reviewer'
            review_file.write_text(json.dumps(review))
            event['publicDate'] = '2020-01-01'
            with self.assertRaisesRegex(ValueError, 'release before review'):
                validate_research(source, {'reviews': []}, events, root)
            event['publicDate'] = day
            review['noNewRecommendation'] = False
            review_file.write_text(json.dumps(review))
            with self.assertRaisesRegex(ValueError, 'review binding'):
                validate_research(source, {'reviews': []}, events, root)
            review['noNewRecommendation'] = True
            review_file.write_text(json.dumps(review))
            source_file.write_text(page.replace('not independently tested', 'independently tested'))
            with self.assertRaisesRegex(ValueError, 'review binding'):
                validate_research(source, {'reviews': []}, events, root)
            source_file.write_text(page)
            item['releaseEventId'] = 'scout:other:first-public-release'
            with self.assertRaisesRegex(ValueError, 'release event mismatch'):
                validate_research(source, {'reviews': []}, events, root)
            item['releaseEventId'] = event['id']
            item['relatedIds'] = ['journal:research-journal']
            with self.assertRaisesRegex(ValueError, 'cannot infer relationships'):
                validate_research(source, {'reviews': []}, events, root)
            item['relatedIds'] = []
            item['standingRelease'] = 'unbounded'
            with self.assertRaisesRegex(ValueError, 'standing release class'):
                validate_research(source, {'reviews': []}, events, root)

    def test_standing_release_scope_excludes_previous_edits_and_unrelated_paths(self):
        slug = 'synthetic-report'
        item = {'id': 'report:' + slug, 'slug': slug, 'type': 'source-report',
                'standingRelease': 'routine-source-report-v1',
                'title': 'Official change', 'summary': 'Source reported a change.',
                'sourcePath': f'site/scout/essays/{slug}/index.html',
                'releaseEventId': f'scout:{slug}:first-public-release'}
        event = {'id': item['releaseEventId'], 'kind': 'new-scout-research',
                 'title': item['title'], 'summary': item['summary']}
        changed = {'content/scout-research.json', 'content/public-release-events.json',
                   item['sourcePath'], f'content/scout/release-reviews/{slug}.json',
                   'site/scout/research/index.html', 'site/feed.xml'}
        old = [{'id': 'essay:old', 'title': 'Original'}]
        ledger = [{'id': 'scout:old:first-public-release', 'title': 'Original'}]
        self.assertEqual(check_delta(old, old + [item], ledger, ledger + [event], changed), item)
        with self.assertRaisesRegex(ValueError, 'Previously published research changed'):
            check_delta(old, [{'id': 'essay:old', 'title': 'Rewritten'}, item], ledger, ledger + [event], changed)
        with self.assertRaisesRegex(ValueError, 'Existing release events changed'):
            check_delta(old, old + [item], [{'id': 'scout:old:first-public-release', 'title': 'Other'}], ledger + [event], changed)
        with self.assertRaisesRegex(ValueError, 'outside one report'):
            check_delta(old, old + [item], ledger, ledger + [event], changed | {'site/other-reader/index.html'})
        with self.assertRaisesRegex(ValueError, 'one new routine'):
            check_delta(old, old + [item, {'id': 'essay:extra'}], ledger, ledger + [event], changed)

    def test_published_works_and_synthesis_journal_are_reachable(self):
        self.validate(self.source)
        records = self.source['records']
        self.assertEqual(len(records), 12)
        self.assertEqual(sum(item['type'] == 'investigation' for item in records), 3)
        self.assertEqual(sum(item['type'] == 'essay' for item in records), 7)
        self.assertEqual(sum(item['type'] == 'method' for item in records), 1)
        self.assertEqual(sum(item['type'] == 'journal' for item in records), 1)
        rendered = (ROOT/'site/scout/research/index.html').read_text()
        self.assertEqual(rendered.count('data-research-card'), 12)
        for item in records:
            self.assertIn('href="' + item['url'] + '"', rendered)
            self.assertTrue((ROOT/'site'/item['url'].strip('/')/'index.html').is_file())
        self.assertIn('scout-research.js', rendered)
        journal = next(item for item in records if item['type'] == 'journal')
        self.assertIn('href="' + journal['url'] + '"', (ROOT/'site/scout/index.html').read_text())
        self.assertIn(journal['url'], (ROOT/'site/sitemap.xml').read_text())
        self.assertIn('Research Journal', (ROOT/'site/scout/method/index.html').read_text())
        self.assertIn(journal['url'], (ROOT/'site/feed.xml').read_text())

    def test_two_new_works_link_only_to_approved_journal_and_appear_in_feed(self):
        for slug, kind in (('what-survives-a-checkpoint', 'essay'),
                           ('before-the-model-sees-the-spreadsheet', 'method')):
            item = next(r for r in self.source['records'] if r['slug'] == slug)
            self.assertEqual(item['type'], kind)
            self.assertEqual(item['relatedIds'], ['journal:research-journal'])
            self.assertIn('href="' + item['url'] + '"', (ROOT/'site/scout/essays/index.html').read_text())
            page = (ROOT/item['sourcePath']).read_text()
            self.assertNotIn('Editorial candidate', page)
            self.assertNotIn('noindex', page)
            self.assertIn('<link rel="canonical" href="https://youtube.shareplane.malott.ai' + item['url'] + '">', page)
            self.assertIn('https://youtube.shareplane.malott.ai' + item['url'], (ROOT/'site/sitemap.xml').read_text())
            matches = [e for e in self.events['events'] if e['id'] == item['releaseEventId']]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]['kind'], 'new-scout-research')
            self.assertEqual(matches[0]['url'], 'https://youtube.shareplane.malott.ai' + item['url'])
            self.assertIn(item['releaseEventId'], (ROOT/'site/feed.xml').read_text())

    def test_future_tranche_and_private_status_fail_closed(self):
        source = copy.deepcopy(self.source)
        future = copy.deepcopy(next(item for item in source['records'] if item['slug'] == 'what-survives-a-checkpoint'))
        future.update(id='essay:synthetic-next-tranche', slug='synthetic-next-tranche',
                      url='/scout/essays/synthetic-next-tranche/',
                      sourcePath='site/scout/essays/synthetic-next-tranche/index.html')
        source['records'].append(future)
        with self.assertRaisesRegex(ValueError, 'source path'):
            self.validate(source)
        future['status'] = 'under-review'
        with self.assertRaisesRegex(ValueError, 'fields/status'):
            self.validate(source)
        future['status'] = 'published'
        future['url'] = next(item['url'] for item in source['records'] if item['type'] == 'essay')
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.validate(source)

    def test_publication_dates_keep_review_and_first_publication_distinct(self):
        self.validate(self.source)
        events = {event['id']: event for event in self.events['events']}
        cards = research_page(self.source, self.events)
        self.assertEqual(cards.count('class="gm-scout-date"'), len(self.source['records']))
        self.assertNotIn('Historical essay / release date not asserted', cards)
        for item in self.source['records']:
            label = publication_label(item, events)
            self.assertIn(label, cards)
            if item['id'] in LEGACY_PUBLIC_BY_IDS:
                self.assertEqual(item['publicByOn'], '2026-10-23')
                self.assertEqual(item['publicByEvidenceUrl'],
                                 'https://github.com/pinklon/ghostmesh-readers/pull/72')
                self.assertIn('Public by', label)
                self.assertIn('First-publication day unverified', label)
                self.assertIsNone(item['reviewedOn'])
            else:
                self.assertEqual(events[item['releaseEventId']]['publicDate'],
                                 label.split('datetime="', 1)[1].split('"', 1)[0])
                self.assertIn('Published', label)
            if item['type'] in {'essay', 'method'}:
                page = (ROOT/item['sourcePath']).read_text()
                hero = page.split('<section class="hero">', 1)[1].split('</section>', 1)[0]
                self.assertIn(label, hero)
                self.assertIn(label.split(' · <a href=', 1)[0],
                              (ROOT/'site/scout/essays/index.html').read_text())

    def test_future_publication_requires_source_bound_first_release_event(self):
        source = copy.deepcopy(self.source)
        item = next(r for r in source['records'] if r['slug'] == 'what-survives-a-checkpoint')
        item['releaseEventId'] = None
        with self.assertRaisesRegex(ValueError, 'first-publication event required'):
            self.validate(source)
        item['releaseEventId'] = 'scout:research-journal:first-public-release'
        with self.assertRaisesRegex(ValueError, 'release event mismatch'):
            self.validate(source)
        item['releaseEventId'] = 'scout:what-survives-a-checkpoint:first-public-release'
        self.validate(source)

    def test_later_review_does_not_change_first_publication_date(self):
        source = copy.deepcopy(self.source)
        item = next(r for r in source['records'] if r['slug'] == 'research-journal')
        item['reviewedOn'] = '2026-10-25'
        self.validate(source)
        events = {event['id']: event for event in self.events['events']}
        label = publication_label(item, events)
        self.assertIn('Published <time datetime="2026-10-23">', label)
        self.assertIn('Reviewed <time datetime="2026-10-25">', label)

    def test_relationships_require_explicit_existing_ids(self):
        source = copy.deepcopy(self.source)
        source['records'][0]['relatedIds'] = ['private:unknown']
        with self.assertRaisesRegex(ValueError, 'relationship target'):
            self.validate(source)
        self.assertNotIn('private:unknown', research_page(self.source, self.events))

    def test_public_graph_projects_every_approved_link_not_just_anchors(self):
        self.validate(self.source)
        graph = research_graph(self.source)
        generated = json.loads((ROOT/'site/scout/research/relationships.json').read_text())
        self.assertEqual(graph, generated)
        self.assertEqual(graph['recordCount'], len(self.source['records']))
        self.assertEqual(graph['relationshipCount'], len(graph['edges']))
        expected = {('scout:' + item['id'], 'scout:' + target)
                    for item in self.source['records'] for target in item['relatedIds']}
        self.assertEqual({(edge['from'], edge['to']) for edge in graph['edges']}, expected)
        for slug, kind in (('what-survives-a-checkpoint', 'essay'),
                           ('before-the-model-sees-the-spreadsheet', 'method')):
            item = next(r for r in self.source['records'] if r['slug'] == slug)
            self.assertEqual(item['id'], kind + ':' + slug)
            self.assertIn(('scout:' + item['id'], 'scout:journal:research-journal'), expected)
        self.assertTrue(all(node['id'] == 'scout:' + node['sourceId'] for node in graph['nodes']))
        self.assertTrue(all(node['url'].startswith('https://youtube.shareplane.malott.ai/scout/')
                            for node in graph['nodes']))
        self.assertIn('/scout/research/relationships.json', (ROOT/'site/scout/research/index.html').read_text())
        self.assertIn('/scout/research/relationships.json', (ROOT/'site/map/index.html').read_text())

    def test_graph_rejects_private_record_and_home_names_new_public_work(self):
        source = copy.deepcopy(self.source)
        source['records'][-1]['status'] = 'under-review'
        with self.assertRaisesRegex(ValueError, 'Nonpublic'):
            research_graph(source)
        home = (ROOT/'site/scout/index.html').read_text()
        self.assertIn('Recently reviewed Scout research', home)
        self.assertIn('Latest tool-review edition / reviewed 2026-10-22', home)
        for slug in ('what-survives-a-checkpoint', 'before-the-model-sees-the-spreadsheet'):
            self.assertIn('href="/scout/essays/' + slug + '/"', home)
        journal = (ROOT/'site/scout/research-journal/index.html').read_text()
        self.assertIn('See the current public Research Library', journal)
        self.assertNotIn('Search article text from all 33 public Readers', journal)


if __name__ == '__main__':
    unittest.main()
