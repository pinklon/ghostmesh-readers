import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_blind_review import make_packet,evaluate
def fixtures():
 leads=[{"url":"https://example.org/"+str(i),"title":"Work "+str(i),"description":"A candidate project "+str(i),"source":"feed"+str(i%2)} for i in range(4)]
 intake={"schema":"scout-multisource-intake-v0","publication_authorized":False,"outreach_authorized":False,"sampled_leads":leads}
 triage={"schema":"scout-relevance-triage-v0","publication_authorized":False,"outreach_authorized":False,"entries":[{"url":x["url"],"topics":["agent"] if i<2 else []} for i,x in enumerate(leads)]}
 outside={"schema":"scout-outside-bubble-v0","publication_authorized":False,"outreach_authorized":False,
 "topic_matched":2,"outside_sampled":2,"outside_sample":[{"url":x["url"]} for x in leads[2:]]}
 return intake,triage,outside
class BlindReviewTests(unittest.TestCase):
 def test_no_cohort_leakage(self):
  packet,key=make_packet(*fixtures())
  self.assertEqual(len(packet["cards"]),4)
  self.assertNotIn("TOPIC_MATCHED",str(packet["cards"]))
  self.assertNotIn("OUTSIDE_BUBBLE",str(packet["cards"]))
  self.assertTrue(all(x["review_fields"]["ghostmesh_relevance"] is None for x in packet["cards"]))
 def test_reproducible_but_different_from_source_order(self):
  a=make_packet(*fixtures());self.assertEqual(a,make_packet(*fixtures()))
  self.assertEqual({x["review_id"] for x in a[0]["cards"]},{x["review_id"] for x in a[1]["review_ids"]})
 def test_incomplete_scores_not_accepted(self):
  packet,key=make_packet(*fixtures())
  with self.assertRaises(ValueError):evaluate(packet,key,{"schema":"scout-independent-review-labels-v0","ratings":[]})
 def test_require_reasoned_scores(self):
  packet,key=make_packet(*fixtures())
  rows=[{"review_id":x["review_id"],"ghostmesh_relevance":2,"rationale":"short"} for x in packet["cards"]]
  with self.assertRaises(ValueError):evaluate(packet,key,{"schema":"scout-independent-review-labels-v0","ratings":rows})
 def test_permissions(self):
  a,b,c=fixtures();a["outreach_authorized"]=True
  with self.assertRaises(ValueError):make_packet(a,b,c)
if __name__=="__main__":unittest.main()
