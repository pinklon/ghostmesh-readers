import sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_persistent_ledger import process,empty_state,validate_state,atomic_json
def batch(events):
 return {"schema":"scout-ingestion-attempt-batch-v0","publication_authorized":False,"outreach_authorized":False,"attempts":events}
class PersistentLedgerTests(unittest.TestCase):
 def test_failed_attempt_does_not_advance_state(self):
  s,r=process(empty_state(),batch([{"url":"https://arxiv.org/abs/2610.28686v1","status":"FAILED","error_code":"HTTP_TIMEOUT"}]))
  self.assertFalse(s["seen_keys"]);self.assertEqual(r["deferred"],1)
 def test_retry_success_resolves_pending(self):
  url="https://arxiv.org/abs/2610.28686v1"
  first,_=process(empty_state(),batch([{"url":url,"status":"FAILED","error_code":"HTTP_429"}]))
  second,r=process(first,batch([{"url":url,"status":"SUCCESS","author_name":"Alex Kim"}]))
  self.assertEqual(r["accepted"],1);self.assertEqual(second["pending"],[])
  self.assertEqual(r["source_receipts"][0]["person_identity"],"UNRESOLVED")
 def test_repeated_known_revision(self):
  x={"url":"https://arxiv.org/abs/2610.28686v1","status":"SUCCESS"}
  first,_=process(empty_state(),batch([x]))
  second,r=process(first,batch([x]))
  self.assertEqual(r["duplicate_revisions"],1)
  self.assertEqual(len(second["seen_keys"]),1)
 def test_versions_and_late_arrivals(self):
  one={"url":"https://arxiv.org/abs/2610.28686v2","status":"SUCCESS"}
  two={"url":"https://arxiv.org/abs/2610.28686v1","status":"SUCCESS"}
  state,_=process(empty_state(),batch([one]))
  _,r=process(state,batch([two]))
  self.assertEqual(r["accepted"],1)
 def test_failure_retry_count_persists(self):
  entry={"url":"https://github.com/a/b","status":"FAILED","error_code":"HTTP_5XX"}
  first,_=process(empty_state(),batch([entry]))
  second,r=process(first,batch([entry]))
  self.assertEqual(second["pending"][0]["attempts"],2)
 def test_bad_attempt_keeps_input_unchanged(self):
  original=empty_state()
  with self.assertRaises(ValueError):process(original,batch([{"url":"https://github.com/a/b","status":"FAILED","error_code":"SECRET_LEAK"}]))
  self.assertEqual(original["runs"],0)
 def test_atomic_file(self):
  with tempfile.TemporaryDirectory() as t:
   path=Path(t)/"state.json";atomic_json(path,empty_state())
   self.assertEqual(validate_state(json.loads(path.read_text()))["runs"],0)
if __name__=="__main__":unittest.main()
