import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_heldout_stop_stress import benchmark,apply,trajectory,BUDGET
class HeldoutStopTests(unittest.TestCase):
 def test_deterministic(self):
  self.assertEqual(trajectory("late_breakthrough",100),trajectory("late_breakthrough",100))
 def test_no_lookahead_for_action(self):
  a=[.9]*10+[.91]*10
  b=[.9]*10+[1.0]*10
  self.assertEqual(apply(a,"stop_on_plateau")["stop_step"],apply(b,"stop_on_plateau")["stop_step"])
 def test_adversarial_delayed_improvement_exposes_regret(self):
  x=apply(trajectory("late_breakthrough",100),"stop_on_plateau")
  self.assertTrue(x["stopped_early"])
  self.assertGreater(x["missed_gain"],0)
 def test_baseline_never_stops(self):
  x=apply(trajectory("false_plateau",100),"continue_all")
  self.assertEqual(x["stop_step"],BUDGET)
  self.assertEqual(x["missed_gain"],0)
 def test_no_authority(self):
  a=benchmark()
  self.assertEqual(len(a["rows"]),4*20*3)
  self.assertFalse(a["model_dispatch_authorized"])
if __name__=="__main__":unittest.main()
