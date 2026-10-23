import sys,tempfile,unittest,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_integrated_run import build_run,commit_run
def data():
 lead={"id":"x","source":"fixture","lane":"community","title":"Independent project","url":"https://example.org/study","description":"Evidence and provenance for agents","published":"","metrics":{},"status":"UNREVIEWED_LEAD","ghostmesh_relevance":"UNKNOWN","outreach_authorized":False}
 intake={"schema":"scout-multisource-intake-v0","sampled_leads":[lead],"diagnostics":[],"captured_utc":"2026-10-23T12:00:00Z","publication_authorized":False,"outreach_authorized":False}
 catalog={"schema":"scout-watch-catalog-v0","watches":[],"publication_authorized":False,"outreach_authorized":False}
 return intake,catalog
class IntegratedRunTests(unittest.TestCase):
 def test_build_complete_offline(self):
  a,b=data();o=build_run(a,b)
  self.assertEqual(len(o),7)
  self.assertIn(b"Complete methodology and limitations",o["methodology.html"])
  self.assertIn(b"methodology.html",o["index.html"])
  self.assertIn(b"noindex,nofollow",o["index.html"])
  self.assertEqual(json.loads(o["intake.json"])["sampled_leads"][0]["url"],a["sampled_leads"][0]["url"])
 def test_manifest_hashes_and_no_overwrite(self):
  a,b=data();o=build_run(a,b)
  with tempfile.TemporaryDirectory() as tmp:
   m=commit_run(o,Path(tmp),"trial1")
   self.assertEqual(m["sha256"]["index.html"],hashlib.sha256(o["index.html"]).hexdigest())
   self.assertTrue((Path(tmp)/"trial1"/"manifest.json").exists())
   with self.assertRaises(FileExistsError):commit_run(o,Path(tmp),"trial1")
 def test_reject_unauthorized(self):
  a,b=data();a["publication_authorized"]=True
  with self.assertRaises(ValueError):build_run(a,b)
 def test_reject_unsafe_id(self):
  a,b=data()
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):commit_run(build_run(a,b),Path(tmp),"../bad")
 def test_reject_incomplete(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):commit_run({"index.html":b"test"},Path(tmp),"bad")
 def test_full_workspace_marks_historical_views(self):
  a,b=data()
  names=("relationships","history","claims","people","replay","theses","trails","differences")
  views={x:"<!doctype html><html><head><meta name=\"robots\" content=\"noindex,nofollow\"></head><body>"+x+"</body></html>" for x in names}
  outputs=build_run(a,b,historical_views=views)
  self.assertEqual(len(outputs),10)
  self.assertIn(b"PINNED",outputs["workspace.html"].upper())
  self.assertIn(b"methodology.html",outputs["workspace.html"])
  with tempfile.TemporaryDirectory() as tmp:
   receipt=commit_run(outputs,Path(tmp),"allviews")
   self.assertEqual(receipt["workspace_view_status"]["discovery"],"CURRENT_RUN")
   self.assertEqual(len(receipt["sha256"]),10)
   self.assertEqual(receipt["workspace_view_status"]["claims"],"UNVERIFIED_CURRENT_RUN_QUEUE")
   self.assertEqual(receipt["workspace_view_status"]["trails"],"OBSERVED_LINKS_NOT_EXPANDED")
   self.assertEqual(receipt["workspace_view_status"]["relationships"],"CURRENT_RUN")
 def test_full_workspace_with_two_snapshots_and_evidence_queues(self):
  a,b=data()
  prior=json.loads(json.dumps(a))
  prior["captured_utc"]="2026-10-22T12:00:00Z"
  names=("relationships","history","claims","people","replay","theses","trails","differences")
  views={x:"<!doctype html><html><head><meta name=\\"robots\\" content=\\"noindex,nofollow\\"></head><body>"+x+"</body></html>" for x in names}
  outputs=build_run(a,b,prior,historical_views=views)
  self.assertIn("history.json",outputs)
  self.assertIn("evidence_queues.json",outputs)
  with tempfile.TemporaryDirectory() as temp:
   receipt=commit_run(outputs,Path(temp),"all-current")
   self.assertEqual(len(receipt["sha256"]),11)
   self.assertEqual(receipt["workspace_view_status"]["history"],"TWO_SNAPSHOT_REBUILT")
 def test_historical_views_must_be_complete(self):
  a,b=data()
  with self.assertRaises(ValueError):build_run(a,b,historical_views={"history":"some html"})
 def test_previous_snapshot(self):
  a,b=data();o=build_run(a,b,a)
  x=json.loads(o["reconciliation.json"])
  self.assertEqual(x["new_to_sample"],0)
if __name__=="__main__":unittest.main()
