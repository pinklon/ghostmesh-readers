import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_fresh_comparison import select
def fixture():
 items=[{"url":f"https://example.org/{i}","title":f"Research item {i}",
         "description":"A study of permission and provenance" if i<9 else "Unrelated discovery description",
         "source":f"feed{i%5}","lane":"research"} for i in range(30)]
 prior={"schema":"scout-multisource-intake-v0","sampled_leads":items[:2],
        "publication_authorized":False,"outreach_authorized":False}
 cur={"schema":"scout-multisource-intake-v0","sampled_leads":items,
      "publication_authorized":False,"outreach_authorized":False}
 return cur,prior
class FreshComparisonTests(unittest.TestCase):
 def test_reproducible_new_only(self):
  a,b=fixture();packet,key=select(a,b)
  self.assertEqual(packet["case_count"],14)
  self.assertEqual((sum(x["cohort"]=="TOPIC_MATCHED" for x in key["cohort_map"]),sum(x["cohort"]=="OUTSIDE_BUBBLE" for x in key["cohort_map"])),(6,8))
  self.assertFalse(any(x["url"] in {p["url"] for p in b["sampled_leads"]} for x in key["cohort_map"]))
  self.assertEqual((packet,key),select(a,b))
 def test_blind_cards_do_not_include_cohort(self):
  a,b=fixture();packet,key=select(a,b)
  self.assertTrue(all("cohort" not in x for x in packet["cards"]))
  self.assertTrue(all(x["relevance"] is None for x in packet["cards"]))
 def test_private_permissions(self):
  a,b=fixture();a["publication_authorized"]=True
  with self.assertRaises(ValueError):select(a,b)
 def test_insufficient_fresh_fails(self):
  a,b=fixture()
  with self.assertRaises(ValueError):select(a,b,topic_quota=12)
if __name__=="__main__":unittest.main()
