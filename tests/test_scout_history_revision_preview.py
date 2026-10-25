import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_history_revision_preview import render,file_hint
class PreviewTests(unittest.TestCase):
 def data(self):
  hist={"schema":"scout-source-history-v0","publication_authorized":False,"outreach_authorized":False,
   "snapshots":["a","b"],"counts":{"distinct_sources":1,"seen_in_multiple_snapshots":1,"not_in_latest_sample":0},
   "sources":[{"url":"https://example.org/a","title":"x","observation_count":2,"observations":[{"captured_utc":"a","topics":[]},{"captured_utc":"b","topics":[]}],"changes":[],"current_sample_state":"PRESENT"}]}
  relations={"schema":"scout-relations-v0","publication_authorized":False,"outreach_authorized":False,
             "nodes":[{"kind":"source","url":"https://example.org/a"}],"edges":[]}
  change={"schema":"scout-github-change-evidence-v0","publication_authorized":False,"outreach_authorized":False,
          "identity":"someone/repo","before_revision":"a"*40,"after_revision":"b"*40,
          "provider_status":"ahead","files":[{"path":"<script>.py","status":"modified"}]}
  return hist,relations,change
 def test_render_and_escape(self):
  h,r,c=self.data();out=render(h,r,[c])
  self.assertIn("Changed upstream",out)
  self.assertIn("&lt;script&gt;.py",out)
  self.assertNotIn("<script>.py",out)
  self.assertIn("IMPLEMENTATION OR TEST CANDIDATE",out)
 def test_authority(self):
  h,r,c=self.data();c["outreach_authorized"]=True
  with self.assertRaises(ValueError):render(h,r,[c])
 def test_reject_schema(self):
  h,r,c=self.data();c["schema"]="imagined"
  with self.assertRaises(ValueError):render(h,r,[c])
if __name__=="__main__":unittest.main()
