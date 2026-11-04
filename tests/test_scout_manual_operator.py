import sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_manual_operator import run_once,latest_verified

def data(stamp):
 return {"schema":"scout-multisource-intake-v0","sampled_leads":[],
         "captured_utc":stamp,"diagnostics":[],
         "publication_authorized":False,"outreach_authorized":False}
CAT={"schema":"scout-watch-catalog-v0","watches":[],
     "publication_authorized":False,"outreach_authorized":False}
class ManualOperatorTests(unittest.TestCase):
 def test_first_then_subsequent(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/"runs"
   a=run_once(root,"one",CAT,intake=data("2026-10-23T09:00:00Z"))
   self.assertIsNone(a["previous_run"])
   self.assertEqual(a["history_status"],"AWAITING_PRIOR_SNAPSHOT")
   b=run_once(root,"two",CAT,intake=data("2026-10-23T10:00:00Z"))
   self.assertEqual(b["previous_run"],"one")
   self.assertEqual(b["history_status"],"TWO_SNAPSHOT_REBUILT")
 def test_does_not_accept_time_travel(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/"runs"
   run_once(root,"one",CAT,intake=data("2026-10-23T10:00:00Z"))
   with self.assertRaises(ValueError):run_once(root,"two",CAT,intake=data("2026-10-23T09:00:00Z"))
 def test_reject_missing_integrity(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/"runs"
   run_once(root,"one",CAT,intake=data("2026-10-23T09:00:00Z"))
   (root/"one"/"intake.json").write_text("corrupted")
   with self.assertRaises(ValueError):latest_verified(root)
 def test_duplicate_no_overwrite(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/"runs"
   run_once(root,"one",CAT,intake=data("2026-10-23T09:00:00Z"))
   with self.assertRaises(FileExistsError):run_once(root,"one",CAT,intake=data("2026-10-23T10:00:00Z"))
if __name__=="__main__":unittest.main()
