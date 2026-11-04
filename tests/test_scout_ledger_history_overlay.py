import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_ledger_history_overlay import render
def fixture():
 return {"schema":"scout-reconciliation-v0","publication_authorized":False,"outreach_authorized":False,
 "ingestion_summary":{"accepted":1,"duplicate_revisions":0,"unverified_reobservations":0},
 "ingestion_receipts":[{"state":"ACCEPTED","source_identity":"<script>alert(1)</script>",
   "revision":None,"person_identity":"UNRESOLVED","outreach_authorized":False}]}
class OverlayTests(unittest.TestCase):
 def test_escaped_private(self):
  result=render('<meta content="noindex,nofollow"><main></main>',fixture())
  self.assertIn("&lt;script&gt;",result)
  self.assertNotIn("<script>alert",result)
 def test_bad_totals(self):
  x=fixture();x["ingestion_summary"]["accepted"]=2
  with self.assertRaises(ValueError):render('<meta content="noindex,nofollow"><main></main>',x)
 def test_authority_rejected(self):
  x=fixture();x["outreach_authorized"]=True
  with self.assertRaises(ValueError):render('<meta content="noindex,nofollow"><main></main>',x)
if __name__=="__main__":unittest.main()
