import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_public_trails import arxiv_trail,github_trail,collect
XML=b'''<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>https://arxiv.org/abs/2610.11111v1</id><title>Beyond the first paper</title><author><name>Example Author</name></author></entry></feed>'''
class TrailTests(unittest.TestCase):
 def test_bylines_are_not_verified_people(self):
  rows=arxiv_trail("Example Author","https://arxiv.org/abs/2610.22222",lambda u:XML)
  self.assertEqual(len(rows),1)
  self.assertFalse(rows[0]["same_real_person_confirmed"])
 def test_reject_similar_but_wrong_bylines(self):
  self.assertEqual(arxiv_trail("Different Author","https://arxiv.org/abs/2610.22222",lambda u:XML),[])
 def test_github_account_continuity_only(self):
  payload=[{"private":False,"fork":False,"owner":{"login":"sam"},"html_url":"https://github.com/sam/new-work","full_name":"sam/new-work"},
           {"private":False,"fork":False,"owner":{"login":"other"},"html_url":"https://github.com/other/bad"}]
  r=github_trail("sam","https://github.com/sam/origin",lambda u:json.dumps(payload).encode())
  self.assertEqual(len(r),1)
  self.assertFalse(r[0]["same_real_person_confirmed"])
 def test_no_outreach(self):
  data={"schema":"scout-work-first-discovery-v0","publication_authorized":False,"outreach_authorized":False,
   "entries":[{"kind":"public_author_name","label":"Example Author","work_url":"https://arxiv.org/abs/2610.22222"}]}
  report=collect(data,lambda u:XML)
  self.assertEqual(len(report["trails"]),1)
  self.assertFalse(report["outreach_authorized"])
if __name__=="__main__":unittest.main()
