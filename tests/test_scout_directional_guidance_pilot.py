import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_directional_guidance_pilot import trial,benchmark,BUDGET,TARGETS,SEEDS
class DirectionalTests(unittest.TestCase):
 def test_same_budget_and_no_duplicate(self):
  for target in TARGETS:
   for guided in (True,False):
    r=trial(target,0,guided)
    self.assertEqual(r["evaluations"],BUDGET)
    self.assertEqual(r["duplicate_evaluations"],0)
 def test_deterministic(self):
  self.assertEqual(trial(5,1,True),trial(5,1,True))
 def test_extra_information_accounted(self):
  b=benchmark()
  self.assertEqual(b["summary"]["ledger_only"]["directional_hints_used"],0)
  self.assertGreater(b["summary"]["directional"]["directional_hints_used"],0)
  self.assertFalse(b["publication_authorized"])
 def test_out_of_scope_fixture(self):
  with self.assertRaises(ValueError):trial(6,1,True)
if __name__=="__main__":unittest.main()
