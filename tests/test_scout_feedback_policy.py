import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_feedback_policy import decide,summarize
def receipt(**extra):
 x={"evaluations":7,"unused_evaluations":5,"proposals_examined":12,"hints":5,
    "wrong_hints":0,"best_reward":0.94,"exact_match":False,"total_cost":7.6}
 x.update(extra);return x
class FeedbackPolicyTests(unittest.TestCase):
 def test_keep_exploring(self):
  self.assertEqual(decide(receipt())["action"],"CONTINUE")
 def test_weak_feedback_falls_back(self):
  d=decide(receipt(wrong_hints=3))
  self.assertEqual(d["action"],"FALLBACK")
  self.assertFalse(d["escalation_executed"])
 def test_solution_stops(self):
  self.assertEqual(decide(receipt(exact_match=True))["action"],"STOP")
 def test_exhausted_requests_review_only(self):
  self.assertEqual(decide(receipt(evaluations=12,unused_evaluations=0))["action"],"REQUEST_ESCALATION_REVIEW")
 def test_reject_counter_fraud(self):
  with self.assertRaises(ValueError):decide(receipt(hints=2,wrong_hints=5))
 def test_requires_research_only(self):
  p={"schema":"scout-noisy-guidance-pilot-v0","production_adoption":"NOT_AUTHORIZED",
     "publication_authorized":False,"trials":[dict(receipt(),policy="guarded",error_rate=0.3)]}
  s=summarize(p)
  self.assertFalse(s["model_invocation_authorized"])
  self.assertEqual(s["cases"],1)
  p["publication_authorized"]=True
  with self.assertRaises(ValueError):summarize(p)
if __name__=="__main__":unittest.main()
