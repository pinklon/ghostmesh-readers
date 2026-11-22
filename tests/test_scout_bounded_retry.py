import sys,unittest,urllib.error,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_bounded_retry import execute,safe_url,MAX_TOTAL_ATTEMPTS
from scout_persistent_ledger import empty_state
def pending(url="https://arxiv.org/abs/2610.28686v1",attempts=1):
 s=empty_state();s["pending"]=[{"url":url,"error_code":"HTTP_TIMEOUT","attempts":attempts}]
 return s
class RetryTests(unittest.TestCase):
 def test_recovers_and_hashes_captured_bytes(self):
  def collector(url,snapshot_callback):
   snapshot_callback(b"fixed source bytes")
   return {"source_url":url}
  state,receipt=execute(pending(),collector)
  self.assertEqual(state["pending"],[])
  self.assertEqual(receipt["accepted"],1)
  self.assertEqual(receipt["source_receipts"][0]["revision"],"v1")
  self.assertEqual(receipt["retry_execution"]["attempted"],1)
 def test_failed_stays_pending(self):
  def collector(url,snapshot_callback):raise TimeoutError("test timeout")
  state,receipt=execute(pending(),collector)
  self.assertEqual(state["pending"][0]["attempts"],2)
  self.assertEqual(receipt["failure_receipts"][0]["error_code"],"HTTP_TIMEOUT")
 def test_exhausted_no_network(self):
  def collector(url,snapshot_callback):self.fail("Unexpected network call")
  state,receipt=execute(pending(attempts=MAX_TOTAL_ATTEMPTS),collector)
  self.assertEqual(receipt["retry_execution"]["attempted"],0)
  self.assertEqual(len(receipt["retry_execution"]["exhausted"]),1)
 def test_limit_three(self):
  s=empty_state();s["pending"]=[{"url":"https://arxiv.org/abs/2610."+str(28680+i)+"v1",
          "error_code":"HTTP_429","attempts":1} for i in range(5)]
  calls=[]
  def collector(url,snapshot_callback):calls.append(url);snapshot_callback(b"real captured payload")
  state,receipt=execute(s,collector)
  self.assertEqual(len(calls),3)
  self.assertEqual(receipt["pending_after"],2)
 def test_no_host_bypass(self):
  for url in ("http://arxiv.org/abs/2610.28686","https://localhost/a",
              "https://evil.example/a","https://user:pass@arxiv.org/abs/2610.28686"):
   with self.assertRaises(ValueError):safe_url(url)
 def test_validate_before_fetch(self):
  s=pending("https://evil.example/file")
  def collector(url,snapshot_callback):self.fail("No request expected")
  with self.assertRaises(ValueError):execute(s,collector)
 def test_no_schedule_or_outreach(self):
  state,receipt=execute(pending(attempts=3),lambda *args,**kwargs:None)
  self.assertFalse(receipt["retry_execution"]["automatic_future_retry"])
  self.assertFalse(state["outreach_authorized"])
if __name__=="__main__":unittest.main()
