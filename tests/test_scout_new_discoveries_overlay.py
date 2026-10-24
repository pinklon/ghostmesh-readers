import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_new_discoveries_overlay import render
def doc():
 x={k:"source evidence" for k in ("id","title","source_claim","ghostmesh_existing","surprise","transfer","counterevidence","test","disposition")}
 x.update(article="https://dev.to/u/p",repo="https://github.com/u/r",identity_status="UNVERIFIED",runtime_status="NOT_RUN")
 return {"schema":"scout-new-discovery-deep-review-v0","publication_authorized":False,"outreach_authorized":False,"cases":[x]}
class NewDiscoveryOverlayTests(unittest.TestCase):
 def test_private_escape(self):
  d=doc();d["cases"][0]["title"]="<script>alert(1)</script>"
  h=render('<meta content="noindex,nofollow"><main></main>',d)
  self.assertIn("&lt;script&gt;",h)
  self.assertNotIn("<script>alert",h)
 def test_no_outreach(self):
  d=doc();d["outreach_authorized"]=True
  with self.assertRaises(ValueError):render('<meta content="noindex,nofollow"><main></main>',d)
 def test_no_verified_identity(self):
  d=doc();d["cases"][0]["identity_status"]="VERIFIED"
  with self.assertRaises(ValueError):render('<meta content="noindex,nofollow"><main></main>',d)
 def test_no_insecure_link(self):
  d=doc();d["cases"][0]["repo"]="https://evil.example/spoof"
  with self.assertRaises(ValueError):render('<meta content="noindex,nofollow"><main></main>',d)
if __name__=="__main__":unittest.main()
