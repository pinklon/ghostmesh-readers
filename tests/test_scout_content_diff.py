import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_content_diff import compare
class ContentDiffTests(unittest.TestCase):
 def test_identical(self):
  p=compare(b"same\n",b"same\n","v1","v1","https://arxiv.org/abs/2601.19921v1")
  self.assertEqual(p["observation"],"IDENTICAL_BYTES")
  self.assertEqual(p["semantic_change"],"NOT_EVALUATED")
  self.assertFalse(p["editorial_review_required"])
 def test_changed_text_not_semantic_claim(self):
  p=compare(b"old claim\n",b"new claim\n","v1","v2","https://arxiv.org/abs/2601.19921")
  self.assertEqual(p["observation"],"BYTES_CHANGED")
  self.assertEqual(p["diff_scope"],"COMPLETE_TEXT")
  self.assertTrue(any("+new claim" in x for x in p["bounded_unified_diff"]))
  self.assertEqual(p["ghostmesh_thesis_impact"],"NOT_EVALUATED")
  self.assertFalse(p["publication_authorized"])
 def test_bounded_does_not_hide_truncation(self):
  p=compare(("row\n"*400).encode(),("row\n"*399+"new\n").encode(),"v1","v2","https://arxiv.org/abs/2601.19921")
  self.assertTrue(p["diff_truncated"])
  self.assertEqual(p["diff_scope"],"PREFIX_ONLY")
  self.assertEqual(p["observation"],"BYTES_CHANGED")
 def test_changed_revision_identical_bytes(self):
  p=compare(b"same",b"same","abc","def","https://github.com/example/repo")
  self.assertEqual(p["observation"],"SAME_BYTES_DIFFERENT_REVISION")
  self.assertTrue(p["editorial_review_required"])
 def test_reject_oversized(self):
  with self.assertRaises(ValueError):compare(b"a"*500001,b"a","a","b","https://example.org")
 def test_reject_non_https(self):
  with self.assertRaises(ValueError):compare(b"a",b"b","a","b","http://localhost")
if __name__=="__main__":unittest.main()
