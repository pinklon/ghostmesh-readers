import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_relations import build
class RelationsTests(unittest.TestCase):
 def test_typed_edges_and_no_person_claims(self):
  a={"schema":"scout-multisource-intake-v0","publication_authorized":False,"outreach_authorized":False,
     "sampled_leads":[{"url":"https://github.com/abc/project","title":"Agent memory"}]}
  t={"schema":"scout-relevance-triage-v0","publication_authorized":False,"outreach_authorized":False,
     "entries":[{"url":"https://github.com/abc/project","topics":["agent-continuity"],
                 "identity":{"type":"repository_owner_handle","value":"abc"}}]}
  h={"schema":"scout-reconciliation-v0","publication_authorized":False,"outreach_authorized":False,
     "leads":[{"url":"https://github.com/abc/project","state":"SEEN_AGAIN"}]}
  result=build(a,t,h)
  self.assertEqual(result["counts"]["sources"],1)
  self.assertEqual({e["relation"] for e in result["edges"]},
                   {"METADATA_TOPIC_MATCH","OBSERVED_SOURCE_HANDLE"})
  self.assertFalse(next(x for x in result["nodes"] if x["kind"]=="observed_handle")["person_verified"])
  a["outreach_authorized"]=True
  with self.assertRaises(ValueError):build(a,t,h)
if __name__=="__main__":unittest.main()
