import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_source_review_overlay import enrich
def data():
 return {"schema":"scout-source-reviewed-deltas-v0","publication_authorized":False,"outreach_authorized":False,"cases":[{"id":"test","source_url":"https://github.com/a/repo","observed_documentation":["<script>bad</script>"],"existing_ghostmesh":"Known","specific_difference":"May differ","transfer_question":"Why?","strongest_objection":"Maybe not","minimum_test":"Offline fixture","status":"FOLLOW","source_review":"README_INSPECTED","runtime_verified":False,"identity_verified":False}]}
class OverlayTests(unittest.TestCase):
 def test_sanitization(self):
  h=enrich('<!doctype html><meta name="robots" content="noindex,nofollow"><main></main>',data())
  self.assertIn("&lt;script&gt;",h)
  self.assertNotIn("<script>bad",h)
  self.assertIn("RUNTIME NOT VERIFIED",h)
 def test_no_privilege(self):
  x=data();x["outreach_authorized"]=True
  with self.assertRaises(ValueError):enrich('<main></main>',x)
 def test_identity_not_verified(self):
  x=data();x["cases"][0]["identity_verified"]=True
  with self.assertRaises(ValueError):enrich('<meta content="noindex,nofollow"><main></main>',x)
if __name__=="__main__":unittest.main()
