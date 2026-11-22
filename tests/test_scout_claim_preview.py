import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_claim_preview import render
class ClaimPreviewTests(unittest.TestCase):
 def setup_data(self):
  reg={"schema":"scout-claim-register-v0","publication_authorized":False,"outreach_authorized":False,"claims":[{"id":"one","source_identity":"x","source_revision":"v1","source_url":"https://example.org/v1","claim":"<script>alert(1)</script>","editorial_interpretation":"hypothesis","disposition":"FOLLOW"}]}
  impact={"schema":"scout-claim-impact-v0","publication_authorized":False,"outreach_authorized":False,"counts":{"claims":1,"matched":1,"revision_review":0},"observations":[{"claim_id":"one","source_identity":"x","pinned_revision":"v1","observed_revision":"v1","state":"REVISION_MATCH","editorial_disposition":"FOLLOW","disposition_changed":False,"recommended_action":"NO_REVISION_TRIGGER"}]}
  return impact,reg
 def test_private_safe_markup(self):
  a,b=self.setup_data();h=render(a,b)
  self.assertIn("&lt;script&gt;",h)
  self.assertNotIn("<script>alert",h)
  self.assertIn("noindex,nofollow",h)
 def test_disposition_mismatch(self):
  a,b=self.setup_data();a["observations"][0]["disposition_changed"]=True
  with self.assertRaises(ValueError):render(a,b)
 def test_authority(self):
  a,b=self.setup_data();a["publication_authorized"]=True
  with self.assertRaises(ValueError):render(a,b)
if __name__=="__main__":unittest.main()
