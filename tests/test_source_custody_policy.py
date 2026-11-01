"""Reader custody receipts distinguish inspected source aids from verified packs."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_site import source_custody_errors,chapter_label_errors


class SourceCustodyPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        readers=json.loads((ROOT/'content/catalog.json').read_text())['readers']
        cls.limited=next(r for r in readers if r['slug']=='the-test-must-name-its-target')
        cls.pack=next(r for r in readers if r['slug']=='the-fleet-does-not-prove-the-forecast')

    def test_existing_source_qualified_reader_without_full_pack_is_admitted(self):
        self.assertEqual(source_custody_errors(self.limited),[])
        self.assertEqual(source_custody_errors(self.pack),[])

    def test_false_pack_label_and_missing_source_limits_fail(self):
        candidate=copy.deepcopy(self.limited)
        candidate['legacyReceipt']['reasonPack']={'verification':'pass'}
        self.assertIn('unverified custody claims pack verification',' '.join(source_custody_errors(candidate)))
        candidate['legacyReceipt']['reasonPack']={}
        del candidate['legacyReceipt']['sourceInspection']['caveat']
        self.assertIn('limited source inspection needs method, caveat and privacy boundary',' '.join(source_custody_errors(candidate)))

    def test_source_identity_and_byte_evidence_must_be_present(self):
        candidate=copy.deepcopy(self.limited)
        candidate['legacyReceipt']['source']['videoId']='different123'
        candidate['legacyReceipt']['sourceInspection'].pop('captionSha256')
        errors=' '.join(source_custody_errors(candidate))
        self.assertIn('receipt source identity mismatch',errors)
        self.assertIn('limited source inspection needs a retained-source digest',errors)


class VideoChapterNavigationTests(unittest.TestCase):
    def test_unique_specific_chapters_pass(self):
        raw='<div class="chapter"><h3>Inspect Git worktrees</h3></div><div class="chapter"><h3>Review pull requests</h3></div>'
        self.assertEqual(chapter_label_errors(raw,'2026-11-01'),[])

    def test_duplicate_chapter_labels_fail_even_when_case_differs(self):
        raw='<div class="chapter"><h3>Inspect Git worktrees</h3></div><div class="chapter"><h3>inspect git worktrees</h3></div>'
        self.assertIn('repeated video chapter labels',chapter_label_errors(raw,'2026-11-01'))

    def test_generic_chapter_labels_fail_for_new_readers_only(self):
        raw='<div class="chapter"><h3>Setup</h3></div>'
        self.assertIn('chapter labels too generic',chapter_label_errors(raw,'2026-11-01'))
        self.assertEqual(chapter_label_errors(raw,'2026-10-31'),[])


if __name__=='__main__':unittest.main()
