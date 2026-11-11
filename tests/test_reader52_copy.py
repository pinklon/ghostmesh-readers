"""Reader52 full-copy/source-map preflight using the existing reusable checks."""
from pathlib import Path
import json,re,unittest
from test_reader46_creative_lock import normal,missing_locked_blocks,ordered_blocks_present,missing_link_targets
ROOT=Path(__file__).resolve().parents[1]
SLUG='better-models-still-need-boundaries'
class Reader52Coverage(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.md=(ROOT/'content/drafts'/f'{SLUG}.md').read_text()
  cls.page=(ROOT/'site'/SLUG/'index.html').read_text()
  cls.blocks=[b.lstrip('# ') for b in cls.md.strip().split('\n\n') if not b.startswith('#')]
  cls.links=re.findall(r'\]\((https://[^)]+)\)',cls.md)
 def test_complete_ordered_copy_and_links(self):
  self.assertEqual(missing_locked_blocks(self.blocks,self.page),[])
  self.assertTrue(ordered_blocks_present(self.blocks,self.page))
  self.assertEqual(missing_link_targets(self.links,self.page),[])
 def test_coverage_rejects_missing_and_reordered_copy(self):
  short='<p>first substantive paragraph</p><p>second substantive paragraph</p>'
  self.assertFalse(ordered_blocks_present(['second substantive paragraph','first substantive paragraph'],short))
  self.assertEqual(missing_locked_blocks(['missing final limitation'],short),['missing final limitation'])
  self.assertEqual(missing_link_targets(['https://example.com/required'],short),['https://example.com/required'])
 def test_no_graph_admission_or_false_source_verification(self):
  r=next(r for r in json.loads((ROOT/'content/catalog.json').read_text())['readers'] if r['slug']==SLUG)
  self.assertEqual(r['relationships'],[]);self.assertEqual(r['sharePlaneRelationships'],[])
  self.assertEqual(r['source']['videoId'],'OEY-vm7qRHc')
  self.assertIn('No listening check, frame inspection',self.md)
  self.assertIn('This article supplies a proposed test',self.md)
  self.assertEqual(r['editorialOrder'],51)
  self.assertTrue(r['archiveCall']['text'])
