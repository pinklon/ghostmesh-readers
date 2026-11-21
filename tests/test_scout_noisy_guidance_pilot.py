import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_noisy_guidance_pilot import benchmark,trial,RATES,TARGETS,POLICIES,EVAL_LIMIT
class NoisyGuidanceTests(unittest.TestCase):
 def test_bounded_calls_and_cost(self):
  for policy in POLICIES:
   for rate in RATES:
    x=trial(5,2,rate,policy)
    self.assertLessEqual(x["evaluations"],EVAL_LIMIT)
    self.assertGreaterEqual(x["total_cost"],x["evaluations"])
 def test_deterministic(self):
  self.assertEqual(trial(5,4,0.3,"guarded"),trial(5,4,0.3,"guarded"))
 def test_baseline_no_hints(self):
  for rate in RATES:self.assertEqual(trial(5,1,rate,"ledger")["hints"],0)
 def test_invalid_params(self):
  with self.assertRaises(ValueError):trial(5,2,0.7,"guarded")
 def test_explicit_research_limits(self):
  x=benchmark()
  self.assertFalse(x["publication_authorized"])
  self.assertEqual(len(x["summary"]),len(RATES)*len(POLICIES))
  self.assertTrue(all("unused_evaluations" in item for item in x["summary"]))
if __name__=="__main__":unittest.main()
