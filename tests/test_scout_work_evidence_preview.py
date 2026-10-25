import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_work_evidence_preview import render
class WorkEvidenceTests(unittest.TestCase):
 def test_work_annotation_cannot_grant_outreach(self):
  html='<!doctype html><meta content="noindex,nofollow"><main></main>'
  a={"schema":"scout-reviewed-work-annotations-v0","source_work":"https://arxiv.org/abs/a","work_title":"<script>x</script>","disposition":"INVESTIGATE","contact_authorized":False,"publication_authorized":False}
  b={"schema":"scout-failure-ledger-ablation-v0","publication_authorized":False,"outreach_authorized":False,
     "summary":{"ledger":{"mean_best_reward":1,"exact_matches":2,"duplicate_evaluations":0,"total_proposals_examined":3},"no_ledger":{"mean_best_reward":.5,"exact_matches":1,"duplicate_evaluations":1,"total_proposals_examined":3}}}
  output=render(html,a,b)
  self.assertIn("&lt;script&gt;",output)
  self.assertNotIn("<script>x",output)
  self.assertIn("proposals examined",output.lower())
  a["contact_authorized"]=True
  with self.assertRaises(ValueError):render(html,a,b)
if __name__=="__main__":unittest.main()
