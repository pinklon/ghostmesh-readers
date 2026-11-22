import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_signal_reconcile import canonical_url,reconcile

def snap(leads):
 return {"schema":"scout-multisource-intake-v0","captured_utc":"2026-10-22T10:00:00Z","sampled_leads":leads}

def lead(url,source="a",title="A",description="Desc"):
 return {"url":url,"source":source,"lane":"engineering","title":title,
         "description":description,"status":"UNREVIEWED_LEAD"}

class ReconcileTests(unittest.TestCase):
 def test_tracking_dedupe_and_cross_source(self):
  data=snap([lead("https://example.org/work?utm_source=feed","a"),
             lead("https://example.org/work","b")])
  r=reconcile(data)
  self.assertEqual(r["canonical_leads"],1)
  self.assertEqual(r["cross_source_count"],1)
  self.assertEqual(r["leads"][0]["sources"],["a","b"])
  self.assertEqual(r["leads"][0]["trend"],"NOT_MEASURED")
 def test_youtube_variants(self):
  self.assertEqual(canonical_url("https://youtu.be/abc123"),
                   canonical_url("https://www.youtube.com/watch?v=abc123&utm_source=x"))
 def test_temporal_change_and_absence(self):
  before=snap([lead("https://example.org/a",title="old"),lead("https://example.org/b")])
  after=snap([lead("https://example.org/a",title="new")])
  r=reconcile(after,before)
  self.assertEqual(r["metadata_changed"],1)
  self.assertEqual(r["missing_from_current_sample"],1)
  self.assertIn("missing is not deleted",r["limits"][0])
 def test_same_title_distinct_urls_not_merged(self):
  a=snap([lead("https://example.org/a"),lead("https://example.org/b")])
  self.assertEqual(reconcile(a)["canonical_leads"],2)
 def test_rejects_authorized_or_insecure(self):
  with self.assertRaises(ValueError):reconcile(snap([dict(lead("https://example.org/a"),status="APPROVED")]))
  with self.assertRaises(ValueError):canonical_url("http://localhost/a")
 def test_same_again(self):
  a=snap([lead("https://example.org/a")])
  self.assertEqual(reconcile(a,a)["leads"][0]["state"],"SEEN_AGAIN")
if __name__=="__main__":unittest.main()
