import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_outside_bubble import build
def source():
 leads=[{"url":"https://example.com/"+str(i),"title":"Work "+str(i),"source":"source"+str(i%3),"lane":"community"} for i in range(10)]
 intake={"schema":"scout-multisource-intake-v0","sampled_leads":leads,"publication_authorized":False,"outreach_authorized":False}
 triage={"schema":"scout-relevance-triage-v0","entries":[{"url":x["url"],"topics":["x"] if i<3 else []} for i,x in enumerate(leads)],"publication_authorized":False,"outreach_authorized":False}
 return intake,triage
class OutsideTests(unittest.TestCase):
 def test_keeps_everything_and_selects_unmatched(self):
  a,b=source();r=build(a,b)
  self.assertEqual(r["total"],10)
  self.assertEqual(r["outside_topic_vocabulary"],7)
  self.assertTrue(all(x["existing_topic_filter_would_hide"] for x in r["outside_sample"]))
  self.assertEqual(len(a["sampled_leads"]),10)
 def test_deterministic_source_balancing(self):
  a,b=source();x=build(a,b)
  self.assertEqual(x["outside_sample"],build(a,b)["outside_sample"])
  from collections import Counter
  self.assertTrue(all(v<=2 for v in Counter(i["source"] for i in x["outside_sample"]).values()))
 def test_absent_topic_never_becomes_novelty(self):
  a,b=source();r=build(a,b)
  self.assertTrue(all(x["novelty"]=="UNASSESSED" for x in r["outside_sample"]))
 def test_reject_coverage_gap(self):
  a,b=source();b["entries"].pop()
  with self.assertRaises(ValueError):build(a,b)
 def test_no_automated_authority(self):
  a,b=source();a["outreach_authorized"]=True
  with self.assertRaises(ValueError):build(a,b)
 def test_bounded(self):
  a,b=source()
  with self.assertRaises(ValueError):build(a,b,max_total=1000)
if __name__=="__main__":unittest.main()
