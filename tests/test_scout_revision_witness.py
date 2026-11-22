import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_revision_witness import witness,compare,identify
class WitnessTests(unittest.TestCase):
 def test_github_revision_and_explicit_same(self):
  def read(url):
   return json.dumps({"default_branch":"main"} if url.endswith("/r") else {"sha":"a"*40}).encode()
  w=witness("https://github.com/o/r",read)
  self.assertEqual(w["revision"],"a"*40)
  self.assertEqual(compare(w,w)["state"],"SAME_REVISION_ID")
  self.assertEqual(w["content_review"],"NOT_PERFORMED")
 def test_arxiv_versions(self):
  def read(url):
   return b'<a href="/abs/2601.19921v1">v1</a><a href="/abs/2601.19921v3">v3</a>'
  w=witness("https://arxiv.org/abs/2601.19921",read)
  self.assertEqual(w["revision"],"v3")
  self.assertEqual(w["stable_content_url"],"https://arxiv.org/abs/2601.19921v3")
 def test_change_not_substance(self):
  a={"kind":"arxiv","identity":"2601.19921","revision":"v1"}
  b=dict(a,revision="v2")
  c=compare(a,b)
  self.assertEqual(c["state"],"REVISION_ID_CHANGED")
  self.assertEqual(c["substantive_change"],"NOT_ASSESSED")
 def test_different_work_rejected(self):
  with self.assertRaises(ValueError):
   compare({"kind":"arxiv","identity":"a","revision":"v1"},{"kind":"arxiv","identity":"b","revision":"v2"})
 def test_unsafe_host(self):
  for url in ["http://github.com/o/r","https://github.com.evil.test/o/r",
              "https://user:pass@github.com/o/r"]:
   with self.assertRaises(ValueError):identify(url)
 def test_unknown_arxiv_version(self):
  with self.assertRaises(ValueError): witness("https://arxiv.org/abs/2601.19921",lambda url:b"<html>No versions</html>")
if __name__=="__main__":unittest.main()
