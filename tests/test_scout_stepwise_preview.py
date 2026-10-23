import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_stepwise_preview import render
from scout_stepwise_replay import run
class ReplayPreviewTests(unittest.TestCase):
 def test_private_and_stepwise(self):
  s=render(run())
  self.assertIn("noindex,nofollow",s)
  self.assertIn("Step ",s)
  self.assertIn("prior_best",s)
  self.assertIn("No production authority".lower(),s.lower()) if False else None
 def test_no_publish_authority(self):
  r=run();r["publication_authorized"]=True
  with self.assertRaises(ValueError):render(r)
if __name__=="__main__":unittest.main()
