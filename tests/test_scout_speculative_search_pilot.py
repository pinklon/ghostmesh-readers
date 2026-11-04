import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_speculative_search_pilot import benchmark,run_task,BUDGET,TASK_TARGETS,SEEDS
class PilotTests(unittest.TestCase):
 def test_exact_budget_all_policies(self):
  for strategy in ("random","success_only","failure_aware"):
   result=run_task(9,3,strategy)
   self.assertEqual(result["evaluations"],BUDGET)
   self.assertLessEqual(result["duplicate_evaluations"],BUDGET)
 def test_reproducible(self):
  self.assertEqual(benchmark()["strategies"],benchmark()["strategies"])
 def test_no_production_authority(self):
  result=benchmark()
  self.assertFalse(result["publication_authorized"])
  self.assertEqual(result["production_adoption"],"NOT_AUTHORIZED")
  self.assertEqual(len(result["rows"]),len(TASK_TARGETS)*len(SEEDS)*3)
 def test_bad_policy(self):
  with self.assertRaises(ValueError):run_task(3,0,"remote-agent")
if __name__=="__main__":unittest.main()
