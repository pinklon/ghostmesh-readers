import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_revision_detail import github_changes,arxiv_text,possible_reassessment
class DetailTests(unittest.TestCase):
 def test_github_file_evidence(self):
  source={"status":"ahead","ahead_by":1,"files":[{"filename":"docs/a.md","status":"modified","additions":2,"deletions":1,"patch":"@@\n+updated"}]}
  result=github_changes("acme","proj","a"*40,"b"*40,lambda url:json.dumps(source).encode())
  self.assertEqual(result["files"][0]["path"],"docs/a.md")
  self.assertEqual(result["semantic_significance"],"NOT_EVALUATED")
  self.assertFalse(result["outreach_authorized"])
 def test_invalid_revision(self):
  with self.assertRaises(ValueError):
   github_changes("acme","repo","main","b"*40)
 def test_arxiv_extraction(self):
  result=arxiv_text("2601.19921","v3",lambda url:b'<meta name="citation_abstract" content="A changed methodology and new validation protocol">')
  self.assertIn("changed methodology",result["extraction"]["excerpt"])
  self.assertEqual(result["content_scope"],"EXTRACTED_EXCERPT_NOT_FULL_PAPER")
 def test_no_inferred_overturn(self):
  result=possible_reassessment({"identity":"x","before_revision":"v1","after_revision":"v2"},
         [{"id":"one","source_identity":"x"},{"id":"two","source_identity":"y"}])
  self.assertEqual(len(result),1)
  self.assertFalse(result[0]["conclusion_overturned"])
 def test_same_revision_no_candidate(self):
  self.assertEqual(possible_reassessment({"identity":"x","before_revision":"a","after_revision":"a"},
      [{"id":"one","source_identity":"x"}]),[])
if __name__=="__main__":unittest.main()
