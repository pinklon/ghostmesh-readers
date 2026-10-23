import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_discovery_contrast import compare,render
def data():
 o={"schema":"scout-outside-bubble-v0","publication_authorized":False,"outreach_authorized":False,"outside_sample":[{"url":"https://arxiv.org/abs/2610.1","title":"<script>x</script>"}]}
 t={"schema":"scout-relevance-triage-v0","publication_authorized":False,"outreach_authorized":False,"entries":[{"url":"https://example.org/2","title":"Other","topics":["interoperability"]}]}
 e={"schema":"scout-editorial-contrast-v0","publication_authorized":False,"outreach_authorized":False,"assessments":[]}
 return o,t,e
class ContrastTests(unittest.TestCase):
 def test_untagged_work_retained_without_ground_truth(self):
  x=compare(*data());self.assertEqual(len(x["rows"]),2)
  self.assertEqual(x["human_label_coverage"],0)
  self.assertEqual(x["precision_recall"],"NOT_MEASURABLE_WITHOUT_INDEPENDENT_LABELS")
 def test_no_unrelated_assessment(self):
  o,t,e=data();e["assessments"]=[{"url":"https://other.invalid/x","cohort":"OUTSIDE_BUBBLE"}]
  with self.assertRaises(ValueError):compare(o,t,e)
 def test_html_sanitized(self):
  x=render(compare(*data()))
  self.assertIn("&lt;script&gt;",x);self.assertNotIn("<script>x",x)
 def test_no_outreach(self):
  o,t,e=data();o["outreach_authorized"]=True
  with self.assertRaises(ValueError):compare(o,t,e)
if __name__=="__main__":unittest.main()
