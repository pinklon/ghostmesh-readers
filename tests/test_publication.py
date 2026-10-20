"""Publication failure modes, not snapshots of implementation details."""
import json,shutil,subprocess,sys,tempfile,unittest
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
  for name,target in [('directory-link',self.root/'content'),('dangling-link',self.root/'missing'),('file-link.html',self.root/'missing-private.html'),('file-link.css',self.root/'site/assets/knowledge.css')]:
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
 def test_missing_or_generic_relationship_assessment_is_rejected(self):
  self.mutate(lambda d:d['readers'][0].pop('relationshipReview'));self.rejected('missing or invalid relationship review date')
  self.mutate(lambda d:d['readers'][0].update(relationshipReview={'reviewedAt':'2026-10-20','reviewedCatalogSize':len(d['readers']),'decision':'none','reviewedTargets':[],'rationale':'No links'}));self.rejected('relationship review needs a substantive rationale')
 def test_compact_relationship_review_date_is_rejected(self):
  self.mutate(lambda d:d['readers'][0]['relationshipReview'].update(reviewedAt='20261020'));self.rejected('missing or invalid relationship review date')
 def test_stale_or_false_zero_relationship_assessment_is_rejected(self):
  self.mutate(lambda d:d['readers'][0]['relationshipReview'].update(reviewedCatalogSize=22));self.rejected('stale relationship review catalog size')
  self.mutate(lambda d:d['readers'][0]['relationshipReview'].update(reviewedCatalogSize=len(d['readers']),decision='none',reviewedTargets=[]));self.rejected('relationship review targets differ from catalog edges')
 def test_justified_zero_relationship_assessment_is_allowed(self):
  data=json.loads((self.root/'content/catalog.json').read_text())
  unlinked=[r for r in data['readers'] if not r['relationships']]
  self.assertEqual({'the-warning-is-not-a-ballot-ruling','the-parallel-result-is-not-the-product'},{r['slug'] for r in unlinked})
  self.assertEqual([],check(self.root))
 def test_five_relations_remain_public_and_navigable(self):
  p=self.root/'content/catalog.json';data=json.loads(p.read_text());reader=data['readers'][0]
  existing={edge['target'] for edge in reader['relationships']}
  for target in data['readers'][1:]:
   if target['id'] in existing:continue
   reader['relationships'].append({'target':target['id'],'type':'related topic',
    'reason':'Synthetic capacity fixture only; not an editorial relationship.',
    'provenance':[f'/{reader["slug"]}/#at-a-glance',f'/{target["slug"]}/#at-a-glance'],
    'basis':'synthetic-test','direction':'outgoing'})
   if len(reader['relationships'])==5:break
  self.assertEqual(5,len(reader['relationships']))
  reader['relationships'][-1]['type']='examines same claim'
  substantive_target=next(r for r in data['readers'] if r['id']==reader['relationships'][-1]['target'])
  reader['relationshipReview']['reviewedTargets']=[edge['target'] for edge in reader['relationships']]
  p.write_text(json.dumps(data))
  schema=json.loads((self.root/'content/catalog.schema.json').read_text())
  self.assertNotIn('maxItems',schema['$defs']['reader']['properties']['relationships'])
  scripts=self.root/'scripts';scripts.mkdir();shutil.copy2(ROOT/'scripts/generate_site.py',scripts/'generate_site.py')
  shutil.copy2(ROOT/'scripts/map_design.py',scripts/'map_design.py')
  shutil.copy2(ROOT/'scripts/catalog_design.py',scripts/'catalog_design.py')
  result=subprocess.run([sys.executable,str(scripts/'generate_site.py')],capture_output=True,text=True)
  self.assertEqual(0,result.returncode,result.stdout+result.stderr)
  self.assertEqual([],check(self.root))
  slug=reader['slug'];public=json.loads((self.root/'site/catalog.json').read_text())
  self.assertEqual(5,len(next(r for r in public['readers'] if r['id']==reader['id'])['relationships']))
  receipt=json.loads((self.root/'site'/slug/'receipt.json').read_text())
  self.assertEqual(5,len(receipt['normalization']['relationships']))
  section=(self.root/'site'/slug/'index.html').read_text().split('<section class="gm-related"',1)[1].split('</section>',1)[0]
  self.assertEqual(5,section.count('<article>'))
  self.assertIn(f'/{substantive_target["slug"]}/',section)
  fifth=reader['relationships'][-1];provenance=fifth['provenance']
  fifth['provenance']=[]
  p.write_text(json.dumps(data));self.rejected('unqualified relation')
  fifth['provenance']=provenance
  reader['relationships'][-1]['target']='reader:missing'
  p.write_text(json.dumps(data));self.rejected('unqualified relation')
if __name__=='__main__':unittest.main()
