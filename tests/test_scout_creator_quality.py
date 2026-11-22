import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_relevance_triage import classify,quality_screen
class CreatorQualityTests(unittest.TestCase):
 def test_sensational_title_is_only_caution(self):
  item={"title":"5 Steps on How to Not Lose at a Hackathon","description":"Some advice","url":"https://dev.to/a/b","source":"dev-community"}
  r=classify(item)
  self.assertEqual(r["signal_quality"]["quality_review"],"CAUTION")
  self.assertEqual(r["evidence_status"],"SOURCE_METADATA_ONLY")
  self.assertFalse(r["outreach_authorized"])
 def test_unconventional_work_not_suppressed(self):
  x=quality_screen({"title":"I built a local model to sort saved articles","description":"Local code and evaluation","source":"dev-community"})
  self.assertEqual(x["quality_review"],"NORMAL_UNVERIFIED")
  self.assertFalse(x["source_checked"])
 def test_other_community_unaffected_by_broad_heuristic(self):
  x=quality_screen({"title":"Top 10 research challenges","description":"Observations","source":"arxiv-ml"})
  self.assertEqual(x["flags"],[])
if __name__=="__main__":unittest.main()
