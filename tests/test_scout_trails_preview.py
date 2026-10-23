import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_trails_preview import annotate,render
def sample():
 return {"schema":"scout-public-contribution-trails-v0","publication_authorized":False,"outreach_authorized":False,"identity_verified":False,"trails":[{"kind":"github_same_account_repository","label":"builder","work_url":"https://github.com/builder/tool","work_title":"<script>Test</script> code review","description":"Code review","origin_work":"https://github.com/source/repo","support":"same public GitHub account","contact_authorized":False,"same_real_person_confirmed":False}]}
class PreviewTests(unittest.TestCase):
 def test_private_html(self):
  x=render(sample())
  self.assertIn("noindex,nofollow",x)
  self.assertIn("&lt;script&gt;",x)
  self.assertNotIn("<script>Test</script>",x)
 def test_never_verified_identity(self):
  r=annotate(sample())
  self.assertEqual(r["items"][0]["personal_identity"],"NOT_VERIFIED")
  self.assertIn("review-workflows",r["items"][0]["topic_matches"])
 def test_refuse_outreach(self):
  x=sample();x["outreach_authorized"]=True
  with self.assertRaises(ValueError):annotate(x)
 def test_refuse_claimed_person_match(self):
  x=sample();x["trails"][0]["same_real_person_confirmed"]=True
  with self.assertRaises(ValueError):annotate(x)
if __name__=="__main__":unittest.main()
