import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_persistent_receipt_overlay import render
def fixture():
 return ({"schema":"scout-persistent-ingestion-state-v0","runs":1,"seen_keys":[["a","v1"]],"pending":[],"publication_authorized":False,"outreach_authorized":False},
 [{"schema":"scout-persistent-ingestion-run-v0","publication_authorized":False,"outreach_authorized":False,"run_number":1,"accepted":0,"deferred":1,"duplicate_revisions":0,"source_receipts":[],"failure_receipts":[{"url":"https://example.org/<script>bad</script>","error_code":"HTTP_TIMEOUT","attempts":1}]}])
class OverlayTests(unittest.TestCase):
 def test_escape_and_private(self):
  state,runs=fixture();h=render('<meta content="noindex,nofollow"><main></main>',runs,state)
  self.assertIn("&lt;script&gt;",h);self.assertNotIn("<script>bad",h)
 def test_no_public_authority(self):
  state,runs=fixture();runs[0]["outreach_authorized"]=True
  with self.assertRaises(ValueError):render('<meta content="noindex,nofollow"><main></main>',runs,state)
if __name__=="__main__":unittest.main()
