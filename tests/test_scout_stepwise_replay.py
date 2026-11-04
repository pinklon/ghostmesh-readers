import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_stepwise_replay import replay,run,BUDGET
class StepwiseTests(unittest.TestCase):
 def test_predecision_state_only(self):
  d=replay(5,0,0.3,"adaptive")
  for step in d["trace"]:
   before=step["before_decision"]
   self.assertNotIn("target",before)
   self.assertNotIn("injected_noise",before)
   self.assertNotIn("wrong_hints",before)
   self.assertNotIn("observed_candidate",before)
 def test_baseline_never_receives_hints(self):
  self.assertEqual(replay(5,0,.5,"ledger")["final"]["hints"],0)
 def test_bounded_costs(self):
  for policy in ("ledger","adaptive"):
   a=replay(5,0,.3,policy)["final"]
   self.assertLessEqual(a["evaluations"],BUDGET)
   self.assertGreaterEqual(a["cost_units"],a["evaluations"])
 def test_reproducible(self):
  self.assertEqual(replay(5,2,.5,"adaptive"),replay(5,2,.5,"adaptive"))
 def test_research_authority(self):
  a=run()
  self.assertEqual(len(a["pairs"]),12*12*4)
  self.assertFalse(a["model_invocation_authorized"])
  self.assertFalse(a["publication_authorized"])
if __name__=="__main__":unittest.main()
