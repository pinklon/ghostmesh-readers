import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_capability_delta_preview import render
def fixture():
 return {"schema":"scout-capability-delta-triage-v0","publication_authorized":False,"outreach_authorized":False,
 "total_trails":1,"trails_with_potential_delta":0,"potential_delta_links":0,
 "rows":[{"attribution":"<script>bad</script>","trail_kind":"github_same_account_repository","status":"NO_METADATA_EVIDENCE","work_title":"Safe title","work_url":"https://github.com/a/b","identity_verified":False,"outreach_authorized":False,"candidates":[]}]}
class DeltaPreviewTests(unittest.TestCase):
 def test_escaped_private(self):
  x=render(fixture());self.assertIn("noindex,nofollow",x);self.assertIn("&lt;script&gt;",x);self.assertNotIn("<script>bad",x)
 def test_refuse_authority(self):
  x=fixture();x["publication_authorized"]=True
  with self.assertRaises(ValueError):render(x)
if __name__=="__main__":unittest.main()
