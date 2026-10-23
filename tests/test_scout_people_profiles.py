import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_people_profiles import profiles,render
class PeopleTests(unittest.TestCase):
 def base(self):
  return {"schema":"scout-work-first-discovery-v0","publication_authorized":False,"outreach_authorized":False,"entries":[{"id":"one","kind":"public_author_name","label":"A. Example","work_url":"https://arxiv.org/abs/2610.28686","basis":"arxiv byline","identity_verified":False,"contact_authorized":False,"work_title":"<script>alert(1)</script>"},{"id":"two","kind":"public_author_name","label":"A. Example","work_url":"https://arxiv.org/abs/2610.28687","basis":"arxiv byline","identity_verified":False,"contact_authorized":False}]}
 def test_names_not_merged(self):
  x=profiles(self.base())
  self.assertEqual(len(x["profiles"]),2)
  self.assertFalse(x["profiles"][0]["same_named_person_merge"])
 def test_html_escapes(self):
  s=render(profiles(self.base()))
  self.assertIn("&lt;script&gt;",s)
  self.assertNotIn("<script>alert",s)
  self.assertIn("noindex,nofollow",s)
 def test_no_contact_authority(self):
  a=self.base();a["entries"][0]["contact_authorized"]=True
  with self.assertRaises(ValueError):profiles(a)
 def test_duplicate_attribution_id_rejected(self):
  a=self.base();a["entries"][1]["id"]="one"
  with self.assertRaises(ValueError):profiles(a)
if __name__=="__main__":unittest.main()
