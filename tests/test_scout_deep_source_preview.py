import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_deep_source_preview import render
def sample():
 return {"schema":"scout-deep-source-comparisons-v0","publication_authorized":False,"outreach_authorized":False,
 "assessments":[{"id":"one","title":"<script>alert(1)</script>","source_urls":["https://example.com/work"],"source_version_note":"test","source_observations":["source metadata"],"ghostmesh_problem":"review","unexpected_connection":"surprise","strongest_objection":"uncertain","disposition":"FOLLOW","small_test":"offline"}]}
class DeepSourcePreviewTests(unittest.TestCase):
 def test_private_and_escaped(self):
  v=render(sample())
  self.assertIn("noindex,nofollow",v)
  self.assertIn("&lt;script&gt;",v)
  self.assertNotIn("<script>alert(1)</script>",v)
 def test_requires_private_authority(self):
  x=sample();x["outreach_authorized"]=True
  with self.assertRaises(ValueError):render(x)
 def test_reject_urls(self):
  x=sample();x["assessments"][0]["source_urls"]=["javascript:alert(1)"]
  with self.assertRaises(ValueError):render(x)
if __name__=="__main__":unittest.main()
