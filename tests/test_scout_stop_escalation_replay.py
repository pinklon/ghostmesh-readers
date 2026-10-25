import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_stop_escalation_replay import choice,score_pair,evaluate
from scout_stepwise_replay import replay,run
class StopReplayTests(unittest.TestCase):
 def test_no_future_data_in_decision(self):
  t=replay(5,1,.3,"adaptive")["trace"]
  if len(t)>=6:
   a=choice(t[:6])
   z=t[:6]+[dict(x,observed_reward=0) for x in t[6:]]
   self.assertEqual(a,choice(z[:6]))
 def test_completed_target_stops(self):
  prefix=[{"observed_reward":.8,"best_reward_after":.8} for _ in range(3)]
  prefix[-1]={"observed_reward":1.0,"best_reward_after":1.0}
  self.assertEqual(choice(prefix)[0],"STOP")
 def test_cannot_invoke_model(self):
  result=score_pair(replay(5,0,.5,"adaptive")["trace"])
  self.assertFalse(result["esc_model_invoked"])
  self.assertGreaterEqual(result["saved_cost"],0)
  self.assertGreaterEqual(result["missed_gain"],0)
 def test_aggregate_is_bounded(self):
  result=evaluate(run())
  self.assertEqual(len(result["rows"]),1152)
  self.assertFalse(result["model_dispatch_authorized"])
  self.assertEqual(len(result["aggregates"]),8)
if __name__=="__main__":unittest.main()
