import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_visual_preview import CSS,RECONCILED
class VisualTests(unittest.TestCase):
 def test_scoped_theme(self):
  self.assertIn("html[data-theme=light]",CSS)
  self.assertIn("gm-scout",CSS)
 def test_review_decisions(self):
  self.assertEqual(RECONCILED["sensemaking"][0],"FOLLOW")
  self.assertEqual(RECONCILED["negative-control"][0],"NO_CONNECTION_JUSTIFIED")
if __name__=="__main__":unittest.main()
