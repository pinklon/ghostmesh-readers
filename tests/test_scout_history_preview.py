import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_history_preview import render
class HistoryPreviewTests(unittest.TestCase):
 def sample(self):
  history={"schema":"scout-source-history-v0","publication_authorized":False,"outreach_authorized":False,
    "snapshots":["a","b"],"counts":{"distinct_sources":1,"seen_in_multiple_snapshots":1,"not_in_latest_sample":0},
    "sources":[{"url":"https://example.org/a","title":"</script><img src=x onerror=1>","observation_count":2,
      "observations":[{"captured_utc":"a","topics":[]},{"captured_utc":"b","topics":[]}],
      "changes":[],"current_sample_state":"PRESENT"}]}
  graph={"schema":"scout-relations-v0","publication_authorized":False,"outreach_authorized":False,
    "nodes":[{"kind":"source","url":"https://example.org/a"}],"edges":[]}
  return history,graph
 def test_encoded_and_filter_controls(self):
  h,g=self.sample();html=render(h,g)
  self.assertNotIn("</script><img",html)
  self.assertIn("NOT_IN_LATEST_SAMPLE",html)
  self.assertIn("Sample status",html)
 def test_rejects_authority(self):
  h,g=self.sample();h["outreach_authorized"]=True
  with self.assertRaises(ValueError):render(h,g)
 def test_rejects_unreconciled_source(self):
  h,g=self.sample();g["nodes"]=[]
  with self.assertRaises(ValueError):render(h,g)
if __name__=="__main__":unittest.main()
