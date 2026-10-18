"""Publication failure modes, not snapshots of implementation details."""
import json,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from check_site import check
class PublicationGate(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for name in ['site','content','docs']:shutil.copytree(ROOT/name,self.root/name)
 def tearDown(self):self.tmp.cleanup()
 def mutate(self,fn):
  p=self.root/'content/catalog.json';d=json.loads(p.read_text());fn(d);p.write_text(json.dumps(d))
 def rejected(self,term):self.assertTrue(any(term in x for x in check(self.root)),check(self.root))
 def test_source_media_outside_publish_directory(self):
  (self.root/'content/private.vtt').write_text('WEBVTT');self.rejected('Private source media')
 def test_public_capture_formats(self):
  for name in ['capture.mkv','capture.MKA','capture.opus','capture.ttml','capture.unknown']:
   with self.subTest(name=name):
    p=self.root/'site'/name;p.write_text('capture fixture')
    self.rejected('Unapproved public file type');p.unlink()
 def test_renamed_capture_is_rejected(self):
  for payload in [b'\x1a\x45\xdf\xa3test',b'RIFFtestWAVE',b'\x00\x00\x00\x18ftypisom',b'OggStest',b'WEBVTT\n']:
   with self.subTest(payload=payload):
    p=self.root/'site/assets/capture.css';p.write_bytes(payload)
    self.rejected('Private source capture signature');p.unlink()
 def test_public_symlinks(self):
  for name,target in [('directory-link',self.root/'content'),('dangling-link',self.root/'missing'),('file-link.css',self.root/'site/assets/knowledge.css')]:
   with self.subTest(name=name):
    p=self.root/'site'/name;p.symlink_to(target)
    self.rejected('Public symlink');p.unlink()
 def test_non_utf8_public_asset(self):
  (self.root/'site/assets/capture.css').write_bytes(b'\xff\xfeinvalid')
  self.rejected('Non-text public asset')
 def test_unknown_binary_public_asset(self):
  (self.root/'site/assets/capture.css').write_bytes(b'unknown\x00binary')
  self.rejected('Binary public asset')
 def test_encoded_em_dash_is_rendered_prose(self):
  p=self.root/'site/readers/index.html';p.write_text(p.read_text().replace('</main>','<p>Bad &#8212; prose</p></main>'));self.rejected('Em dash')
 def test_confirmation_without_evidence(self):
  self.mutate(lambda d:d['readers'][0]['claims'][0].update(status='corroborated',references=[],counterevidence=[]));self.rejected('confirmation from empty')
 def test_counterevidence_does_not_promote_aggregate(self):
  def bad(d):
   r=d['readers'][0];r['evidenceState']='partially corroborated'
   for c in r['claims']:c['status']='unverified'
  self.mutate(bad);self.rejected('aggregate evidence promotion')
 def test_reference_must_resolve(self):
  self.mutate(lambda d:d['readers'][0]['claims'][0].update(references=['invented']));self.rejected('dangling reference')
 def test_timezone_is_required(self):
  self.mutate(lambda d:d['readers'][0]['references'][0].update(checkedAt='2026-10-18T12:00:00'));self.rejected('timezone required')
 def test_future_check_is_rejected(self):
  self.mutate(lambda d:d['readers'][0]['references'][0].update(checkedAt='2099-01-01T00:00:00Z'));self.rejected('future timestamp')
 def test_invalid_source_date_is_rejected(self):
  self.mutate(lambda d:d['readers'][0]['references'][0].update(publicationDate='2026-99-99',datePrecision='day'));self.rejected('invalid source date')
 def test_claim_identity_is_global(self):
  self.mutate(lambda d:d['readers'][1]['claims'][0].update(id=d['readers'][0]['claims'][0]['id']));self.rejected('Duplicate global claim')
 def test_relation_requires_provenance(self):
  self.mutate(lambda d:d['readers'][0]['relationships'][0].update(provenance=[]));self.rejected('unqualified relation')
if __name__=='__main__':unittest.main()
