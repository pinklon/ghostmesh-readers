import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_source_history import build

def snap(at, urls):
 a={"schema":"scout-multisource-intake-v0","captured_utc":at,"publication_authorized":False,"outreach_authorized":False,
    "sampled_leads":[{"url":u,"title":title} for u,title,topics in urls]}
 b={"schema":"scout-relevance-triage-v0","publication_authorized":False,"outreach_authorized":False,
    "entries":[{"url":u,"topics":topics,"identity":None} for u,title,topics in urls]}
 return a,b
class HistoryTests(unittest.TestCase):
 def test_repeat_absence_and_topic_delta(self):
  before=snap("2026-10-22T10:00:00Z",[("https://example.org/a","Alpha",["agent-continuity"]),("https://example.org/b","Beta",[])])
  after=snap("2026-10-22T11:00:00Z",[("https://example.org/a","Alpha",["agent-continuity","evidence-and-evaluation"])])
  out=build([before,after])
  self.assertEqual(out["counts"]["distinct_sources"],2)
  self.assertEqual(out["counts"]["seen_in_multiple_snapshots"],1)
  self.assertEqual(out["counts"]["not_in_latest_sample"],1)
  item=next(x for x in out["sources"] if x["url"].endswith("/a"))
  self.assertEqual(item["changes"][0]["type"],"METADATA_TOPIC_DELTA")
  self.assertEqual(item["changes"][0]["certainty"],"HEURISTIC")
  self.assertEqual(next(x for x in out["sources"] if x["url"].endswith("/b"))["changes"][0]["certainty"],"SAMPLING_ONLY")
 def test_no_fabricated_growth(self):
  out=build([snap("a",[]),snap("b",[])])
  self.assertNotIn("virality",out["counts"])
 def test_reject_bad_order(self):
  with self.assertRaises(ValueError): build([snap("b",[]),snap("a",[])])
 def test_reject_permission_change(self):
  a=snap("a",[]);b=snap("b",[])
  b[0]["outreach_authorized"]=True
  with self.assertRaises(ValueError):build([a,b])
if __name__=="__main__":unittest.main()
