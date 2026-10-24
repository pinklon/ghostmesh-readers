import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_run_library import build
from scout_manual_operator import run_once
CAT={"schema":"scout-watch-catalog-v0","watches":[],"publication_authorized":False,"outreach_authorized":False}
def intake(stamp):
 return {"schema":"scout-multisource-intake-v0","sampled_leads":[],"diagnostics":[],"captured_utc":stamp,"publication_authorized":False,"outreach_authorized":False}
class RunLibraryTests(unittest.TestCase):
 def test_links_verified_runs_newest_first(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/"runs"
   run_once(root,"older",CAT,intake=intake("2026-10-22T10:00:00Z"))
   run_once(root,"newer",CAT,intake=intake("2026-10-23T10:00:00Z"))
   html,summary=build(root,Path(tmp)/"private-index.html")
   self.assertEqual(summary["verified_runs"],2)
   self.assertEqual(summary["latest_run"],"newer")
   self.assertLess(html.index("newer"),html.index("older"))
   self.assertIn("noindex,nofollow",html)
 def test_reject_corrupted_run(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/"runs"
   run_once(root,"one",CAT,intake=intake("2026-10-23T10:00:00Z"))
   (root/"one"/"intake.json").write_text("oops")
   with self.assertRaises(ValueError):build(root,Path(tmp)/"index.html")
 def test_index_not_inside_root(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/"runs"
   run_once(root,"one",CAT,intake=intake("2026-10-23T10:00:00Z"))
   with self.assertRaises(ValueError):build(root,root/"index.html")
if __name__=="__main__":unittest.main()
