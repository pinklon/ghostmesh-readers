import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from scout_research import validate_research, research_page


class ScoutResearchTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((ROOT/'content/scout-research.json').read_text())
        self.scout = json.loads((ROOT/'content/scout-public.json').read_text())
        self.events = json.loads((ROOT/'content/public-release-events.json').read_text())

    def validate(self, source):
        return validate_research(source, self.scout, self.events, ROOT)

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
            self.assertNotIn('Editorial candidate', (ROOT/item['sourcePath']).read_text())
            matches = [e for e in self.events['events'] if e['id'] == item['releaseEventId']]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]['kind'], 'new-scout-research')
            self.assertEqual(matches[0]['url'], 'https://youtube.shareplane.malott.ai' + item['url'])
            self.assertIn(item['releaseEventId'], (ROOT/'site/feed.xml').read_text())

    def test_future_tranche_and_private_status_fail_closed(self):
        source = copy.deepcopy(self.source)
        future = copy.deepcopy(next(item for item in source['records'] if item['type'] == 'essay'))
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

    def test_relationships_require_explicit_existing_ids(self):
        source = copy.deepcopy(self.source)
        source['records'][0]['relatedIds'] = ['private:unknown']
        with self.assertRaisesRegex(ValueError, 'relationship target'):
            self.validate(source)
        self.assertNotIn('private:unknown', research_page(self.source))


if __name__ == '__main__':
    unittest.main()
