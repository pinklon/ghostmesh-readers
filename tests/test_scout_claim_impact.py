import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_claim_impact import evaluate
def fixture(revision="v3"):
 return ({"schema":"scout-claim-register-v0","publication_authorized":False,"outreach_authorized":False,
          "claims":[{"id":"c","source_kind":"arxiv","source_identity":"2601.19921","source_revision":"v3",
                     "source_url":"https://arxiv.org/abs/2601.19921v3","disposition":"FOLLOW"}]},
         {"schema":"scout-revision-witness-v0","publication_authorized":False,"outreach_authorized":False,
          "records":[{"kind":"arxiv","identity":"2601.19921","revision":revision}]})
class ClaimImpactTests(unittest.TestCase):
 def test_match(self):
  a,b=fixture();r=evaluate(a,b)
  self.assertEqual(r["counts"]["matched"],1)
  self.assertFalse(r["observations"][0]["disposition_changed"])
 def test_new_version_only_flags(self):
  a,b=fixture("v4");r=evaluate(a,b)
  self.assertEqual(r["counts"]["revision_review"],1)
  self.assertEqual(r["observations"][0]["recommended_action"],"COMPARE_CHANGED_CONTENT")
  self.assertEqual(r["observations"][0]["editorial_disposition"],"FOLLOW")
 def test_missing_witness(self):
  a,b=fixture();b["records"]=[]
  self.assertEqual(evaluate(a,b)["counts"]["without_witness"],1)
 def test_reject_duplicate_claims(self):
  a,b=fixture();a["claims"].append(dict(a["claims"][0]))
  with self.assertRaises(ValueError):evaluate(a,b)
 def test_reject_witness_conflict(self):
  a,b=fixture();b["records"].append(dict(b["records"][0],revision="v4"))
  with self.assertRaises(ValueError):evaluate(a,b)
 def test_reject_permission(self):
  a,b=fixture();a["outreach_authorized"]=True
  with self.assertRaises(ValueError):evaluate(a,b)
if __name__=="__main__":unittest.main()
