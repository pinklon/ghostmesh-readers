import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_relationship_preview import render
class PreviewTests(unittest.TestCase):
 def base(self):
  return {"schema":"scout-relations-v0","publication_authorized":False,"outreach_authorized":False,
    "nodes":[{"id":"source:1","kind":"source","url":"https://example.org/a","title":"<img src=x onerror=alert(1)>","sample_state":"NEW_TO_SAMPLE"},
             {"id":"topic:memory","kind":"topic","label":"agent-memory"}],
    "edges":[{"from":"source:1","to":"topic:memory","relation":"METADATA_TOPIC_MATCH"}]}
 def test_script_data_not_markup(self):
  s=render(self.base())
  self.assertIn('\\u003cimg',s)
  self.assertNotIn("<img src=x",s)
  self.assertIn("graph-data",s)
  self.assertIn("LIGHT / DARK",s)
 def test_reject_disallowed_edges(self):
  d=self.base();d["edges"][0]["relation"]="SAME_PERSON"
  with self.assertRaises(ValueError):render(d)
 def test_reject_authority(self):
  d=self.base();d["publication_authorized"]=True
  with self.assertRaises(ValueError):render(d)
if __name__=="__main__":unittest.main()
