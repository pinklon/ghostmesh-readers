import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_relevance_triage import triage,classify

def lead(title,url="https://github.com/alice/repo",source="github-search"):
 return {"title":title,"description":"","url":url,"source":source,"status":"UNREVIEWED_LEAD"}
def intake(items):
 return {"schema":"scout-multisource-intake-v0","sampled_leads":items}
class RelevanceTests(unittest.TestCase):
 def test_conservative_topics(self):
  a=classify(lead("Agent memory provenance"))
  self.assertEqual(set(a["topics"]),{"agent-continuity","evidence-and-evaluation"})
  self.assertEqual(a["relevance_status"],"KEYWORD_CANDIDATE")
  self.assertFalse(a["outreach_authorized"])
 def test_unknown_not_forced(self):
  self.assertEqual(classify(lead("Beautiful landscape photos"))["relevance_status"],"UNKNOWN")
 def test_handle_not_person(self):
  a=classify(lead("Some project"))
  self.assertEqual(a["identity"]["value"],"alice")
  self.assertFalse(a["identity"]["verified_person"])
 def test_cross_source_topic_not_same_story(self):
  d=triage(intake([lead("Agent memory",source="github-search"),
                   lead("Recovering persistent memory",url="https://example.org/post",source="lobsters")]))
  item=next(x for x in d["topic_groups"] if x["topic"]=="agent-continuity")
  self.assertTrue(item["cross_source_topic"])
  self.assertEqual(item["leads"],2)
  self.assertIn("not established",d["limits"][0])
 def test_track_repeated_handle(self):
  d=triage(intake([lead("One"),lead("Two","https://github.com/alice/other")]))
  self.assertEqual(len(d["recurring_source_handles"]),1)
 def test_reject_bad_input(self):
  with self.assertRaises(ValueError):triage({})
if __name__=="__main__":unittest.main()
