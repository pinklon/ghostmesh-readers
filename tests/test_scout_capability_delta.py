import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_capability_delta import assess
def data():
    b={"schema":"scout-existing-capabilities-v0","publication_authorized":False,"outreach_authorized":False,"status":"RESEARCH_ONLY",
       "capabilities":[{"id":"review","label":"Review","current":"Existing review","evidence":"source.md",
       "keywords":["code review"],"question":"What changes?","known_gap":"Not measured","anti_claim":"Not permission"}]}
    t={"schema":"scout-public-contribution-trails-v0","publication_authorized":False,"outreach_authorized":False,
       "identity_verified":False,"trails":[{"id":"a","label":"handle","kind":"github_same_account_repository",
       "work_title":"Code Review App","work_url":"https://github.com/example/repo",
       "origin_work":"https://github.com/origin/repo",
       "contact_authorized":False,"same_real_person_confirmed":False}]}
    return t,b
class DeltaTests(unittest.TestCase):
 def test_overlap_never_proves_novelty(self):
  t,b=data();r=assess(t,b)
  self.assertEqual(r["trails_with_potential_delta"],1)
  self.assertEqual(r["rows"][0]["candidates"][0]["capability_absent"],"NOT_ESTABLISHED")
  self.assertEqual(r["rows"][0]["candidates"][0]["originality"],"NOT_ASSESSED")
 def test_empty_overlap_remains_visible(self):
  t,b=data();t["trails"][0]["work_title"]="Unrelated pottery"
  r=assess(t,b);self.assertEqual(r["rows"][0]["status"],"NO_METADATA_EVIDENCE")
 def test_refuse_authority(self):
  t,b=data();t["trails"][0]["contact_authorized"]=True
  with self.assertRaises(ValueError):assess(t,b)
 def test_duplicate_ids_rejected(self):
  t,b=data();t["trails"].append(dict(t["trails"][0]))
  with self.assertRaises(ValueError):assess(t,b)
 def test_reject_unsafe_url(self):
  t,b=data();t["trails"][0]["work_url"]="https://evil.example/file"
  with self.assertRaises(ValueError):assess(t,b)
if __name__=="__main__":unittest.main()
