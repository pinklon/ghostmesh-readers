import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_work_complementarity import screen,matches
RSS=b'<rss><channel><item><title>Calibrated confidence for agent evaluation</title><link>https://arxiv.org/abs/2610.28686</link><description>Uncertainty calibration for multi-agent review.</description></item></channel></rss>'
def p():return {"schema":"scout-private-work-profiles-v0","publication_authorized":False,"outreach_authorized":False,
 "profiles":[{"id":"a","display_label":"Name","source_work":"https://arxiv.org/abs/2610.28686","identity_verified":False,"contact_authorized":False},
             {"id":"b","display_label":"Handle","source_work":"https://github.com/org/repo","identity_verified":False,"contact_authorized":False}]}
class ScreenTests(unittest.TestCase):
 def test_matches_are_not_verdicts(self):
  x=screen(p(),RSS)
  self.assertEqual(x["metadata_candidates"],1)
  self.assertEqual(x["results"][0]["collaboration_merit"],"NOT_EVALUATED")
  self.assertEqual(x["results"][1]["state"],"SOURCE_CONTEXT_MISSING")
 def test_unmatched_safe(self):
  self.assertFalse(matches("Landscape art","A photograph of clouds"))
 def test_reject_identity(self):
  x=p();x["profiles"][0]["identity_verified"]=True
  with self.assertRaises(ValueError):screen(x,RSS)
 def test_reject_outreach(self):
  x=p();x["outreach_authorized"]=True
  with self.assertRaises(ValueError):screen(x,RSS)
if __name__=="__main__":unittest.main()
