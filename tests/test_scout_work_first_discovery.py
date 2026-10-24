import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_work_first_discovery import build,arxiv_creators,github_contributors
RSS=b'<rss xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><item><title>Independent work</title><link>https://arxiv.org/abs/2610.28686</link><dc:creator>Ada Example, B. Test</dc:creator></item></channel></rss>'
class WorkFirstTests(unittest.TestCase):
 def test_arxiv_bylines_not_people(self):
  x=arxiv_creators(RSS)
  self.assertEqual(len(x),2)
  self.assertEqual(x[0]["kind"],"public_author_name")
  self.assertFalse(x[0]["identity_verified"])
 def test_github_handle_not_maintainer_rank(self):
  def get(url):return json.dumps([{"login":"some-builder","type":"User","contributions":19},
                                  {"login":"dependency-bot","type":"Bot","contributions":300}]).encode()
  x=github_contributors("org","repo",get)
  self.assertEqual(len(x),1)
  self.assertFalse(x[0]["identity_verified"])
  self.assertNotIn("contributions",x[0])
 def test_fail_soft_and_distinct_identities(self):
  result=build(RSS,[("a","b")],lambda u: b'invalid json')
  self.assertEqual(len(result["entries"]),2)
  self.assertEqual(result["coverage"][1]["status"],"ERROR")
  self.assertFalse(result["outreach_authorized"])
 def test_reject_bad_repo(self):
  with self.assertRaises(ValueError):github_contributors("bad/owner","repo")
 def test_reject_oversize(self):
  with self.assertRaises(ValueError):arxiv_creators(b"x"*2500001)
if __name__=="__main__":unittest.main()
