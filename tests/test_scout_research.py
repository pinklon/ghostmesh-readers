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

    def test_nine_approved_public_works_are_reachable(self):
        self.validate(self.source)
        records = self.source['records']
        self.assertEqual(len(records), 9)
        self.assertEqual(sum(item['type'] == 'investigation' for item in records), 3)
        self.assertEqual(sum(item['type'] == 'essay' for item in records), 6)
        rendered = (ROOT/'site/scout/research/index.html').read_text()
        self.assertEqual(rendered.count('data-research-card'), 9)
        for item in records:
            self.assertIn('href="' + item['url'] + '"', rendered)
            self.assertTrue((ROOT/'site'/item['url'].strip('/')/'index.html').is_file())
        self.assertIn('scout-research.js', rendered)

    def test_future_tranche_and_private_status_fail_closed(self):
        source = copy.deepcopy(self.source)
        future = copy.deepcopy(source['records'][3])
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
        future['url'] = source['records'][3]['url']
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
