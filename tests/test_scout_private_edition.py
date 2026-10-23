import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_private_edition import edition,markdown

class EditionTests(unittest.TestCase):
 def test_watch_and_unknown_kept_distinct(self):
  intake={"schema":"scout-multisource-intake-v0","sampled_leads":[
   {"url":"https://simonwillison.net/post/a","title":"Builder work","source":"independent-builder","lane":"builder","description":""},
   {"url":"https://example.org/b","title":"Guillaume Bolduc mention","source":"community","lane":"community","description":""}]}
  triage={"schema":"scout-relevance-triage-v0","entries":[
   {"url":"https://simonwillison.net/post/a","topics":[],"ghostmesh_questions":[]},
   {"url":"https://example.org/b","topics":[],"ghostmesh_questions":[]}]}
  catalog={"schema":"scout-watch-catalog-v0","publication_authorized":False,"outreach_authorized":False,"watches":[
   {"id":"simon","source_host":"simonwillison.net"},
   {"id":"guillaume","keywords":["guillaume bolduc"]}]}
  result=edition(intake,triage,catalog)
  self.assertEqual(result["candidate_count"],2)
  self.assertFalse(result["publication_authorized"])
  self.assertEqual(result["candidates"][0]["editorial_judgment"],"NOT_ASSESSED")
  self.assertIn("unreviewed reading queue",markdown(result))
 def test_refuse_public_authority(self):
  with self.assertRaises(ValueError):
   edition({"schema":"scout-multisource-intake-v0","sampled_leads":[]},
      {"schema":"scout-relevance-triage-v0","entries":[]},
      {"schema":"scout-watch-catalog-v0","publication_authorized":True,"outreach_authorized":False})
if __name__=="__main__":unittest.main()
