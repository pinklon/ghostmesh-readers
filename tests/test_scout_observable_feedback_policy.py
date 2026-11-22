import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_observable_feedback_policy import decide_observable,summarize
def r(**override):
 x={"policy":"guarded","evaluations":8,"unused_evaluations":4,"proposals_examined":15,"hints":7,"range_resets":0,"best_reward":0.92,"exact_match":False}
 x.update(override);return x
class ObservablePolicyTests(unittest.TestCase):
 def test_oracle_truth_never_affects_decision(self):
  a=decide_observable(r(wrong_hints=0,error_rate=0))
  b=decide_observable(r(wrong_hints=7,error_rate=.5))
  self.assertEqual(a,b)
 def test_observed_contradiction(self):
  self.assertEqual(decide_observable(r(range_resets=1))["action"],"FALLBACK")
 def test_budget_review_not_dispatch(self):
  a=decide_observable(r(evaluations=12,unused_evaluations=0))
  self.assertEqual(a["action"],"REQUEST_ESCALATION_REVIEW")
  self.assertFalse(a["escalation_executed"])
 def test_solved(self):
  self.assertEqual(decide_observable(r(exact_match=True))["action"],"STOP")
 def test_noisy_receipts_rejected_if_bad(self):
  with self.assertRaises(ValueError):decide_observable(r(proposals_examined=1))
 def test_audit_separates_truth_from_action(self):
  experiment={"schema":"scout-noisy-guidance-pilot-v0","production_adoption":"NOT_AUTHORIZED",
              "publication_authorized":False,"outreach_authorized":False,
              "trials":[dict(r(),task=0,seed=0,error_rate=.5,wrong_hints=6)]}
  x=summarize(experiment)
  self.assertEqual(x["cases"],1)
  self.assertEqual(x["cohorts"]["guarded@50pct"]["bad_hints_without_fallback"],1)
  self.assertFalse(x["model_invocation_authorized"])
if __name__=="__main__":unittest.main()
