import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_failure_ledger_ablation import trial,benchmark,BUDGET
class LedgerAblationTests(unittest.TestCase):
 def test_matched_budget(self):
  for ledger in (False,True):
   a=trial(8,1,ledger)
   self.assertEqual(a["evaluations"],BUDGET)
 def test_ledger_never_repeats(self):
  for t in (0,15,63):
   for seed in range(12):
    self.assertEqual(trial(t,seed,True)["duplicate_evaluations"],0)
 def test_same_stream_reproducible(self):
  self.assertEqual(benchmark()["summary"],benchmark()["summary"])
 def test_proposal_overhead_visible(self):
  result=benchmark()
  self.assertGreaterEqual(result["summary"]["ledger"]["total_proposals_examined"],result["summary"]["ledger"]["total_evaluations"])
  self.assertFalse(result["publication_authorized"])
if __name__=="__main__":unittest.main()
