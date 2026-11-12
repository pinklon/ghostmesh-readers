import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_connection_shortlist import validate,render
def fixture():
 item={k:"text" for k in ("id","title","source_kind","source_status","work_basis","ghostmesh_problem","complementarity","counterevidence","experiment","review_status")}
 item.update({"source_url":"https://example.org/valid","disposition":"FOLLOW","title":"<script>alert(1)</script>"})
 return {"schema":"scout-connection-theses-v1","publication_authorized":False,"outreach_authorized":False,"people_identity_verified":False,"theses":[item]}
class ShortlistTests(unittest.TestCase):
 def test_private_and_escaped(self):
  s=render(fixture())
  self.assertIn("noindex,nofollow",s)
  self.assertIn("&lt;script&gt;",s)
  self.assertNotIn("<script>alert(1)",s)
 def test_no_outreach_authority(self):
  x=fixture();x["outreach_authorized"]=True
  with self.assertRaises(ValueError):validate(x)
 def test_no_unsupported_identity(self):
  x=fixture();x["people_identity_verified"]=True
  with self.assertRaises(ValueError):validate(x)
 def test_duplicate(self):
  x=fixture();x["theses"].append(dict(x["theses"][0]))
  with self.assertRaises(ValueError):validate(x)
 def test_negative_control_must_not_invent_experiment(self):
  x=fixture();x["theses"][0]["disposition"]="NO_CONNECTION_JUSTIFIED"
  with self.assertRaises(ValueError):validate(x)
 def test_url_scheme(self):
  x=fixture();x["theses"][0]["source_url"]="javascript:alert(1)"
  with self.assertRaises(ValueError):validate(x)
if __name__=="__main__":unittest.main()
