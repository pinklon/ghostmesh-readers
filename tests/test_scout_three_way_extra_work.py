import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_three_way_extra_work import evaluate_path,benchmark,CHECKPOINT,PROBE_STEPS
from scout_heldout_stop_stress import trajectory
class ThreeWayTests(unittest.TestCase):
 def test_probe_has_same_decision_despite_later_outcomes(self):
  a=[.8]*CHECKPOINT+[.8]*PROBE_STEPS+[1.0]*6
  b=[.8]*CHECKPOINT+[.8]*PROBE_STEPS+[.0]*6
  self.assertEqual(evaluate_path(a,"probe_then_decide")["decision"],evaluate_path(b,"probe_then_decide")["decision"])
 def test_stop_misses_later_breakthrough(self):
  x=trajectory("late_breakthrough",100)
  self.assertLess(evaluate_path(x,"stop")["reward"],evaluate_path(x,"continue")["reward"])
 def test_charges_probe(self):
  x=trajectory("flat_noise",100)
  r=evaluate_path(x,"probe_then_decide")
  self.assertTrue(r["probe_review_charged"])
  self.assertGreater(r["total_cost"],r["steps_used"]*.00305)
 def test_full_coverage_and_no_dispatch(self):
  r=benchmark()
  self.assertEqual(len(r["rows"]),4*20*3)
  self.assertFalse(r["model_invocation_authorized"])
  self.assertEqual(len(r["summary"]),12)
 def test_unrecognized_policy(self):
  with self.assertRaises(ValueError):evaluate_path(trajectory("flat_noise",100),"invoke_model")
if __name__=="__main__":unittest.main()
