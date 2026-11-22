import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_source_collector import collect
class SourceExtensionTests(unittest.TestCase):
 def test_new_host_allowlist_not_wildcard(self):
  for host in ("https://huggingface.co/blog/a","https://simonwillison.net/2026/Oct/22/a/"):
   class Response:
    status=200
    class headers:
     @staticmethod
     def get_content_type():return "text/html"
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,count):return b'<html><main><p>'+(b'word '*40)+b'</p></main></html>'
   class Opener:
    def open(self,*args,**kwargs):return Response()
   p=collect(host,Opener())
   self.assertEqual(p["substantive_text"]["extraction_status"],"EXTRACTED_UNVERIFIED")
  for host in ("https://evil.huggingface.co/a","https://huggingface.co.evil.test/a"):
   with self.assertRaises(ValueError):collect(host)
if __name__=="__main__":unittest.main()
