"""Regression tests for the single-pass Reader publication contract."""
import hashlib
import json
import tempfile
from unittest.mock import patch
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from catalog_design import card
from check_site import new_reader_canonical_errors
from editorial_depth import evidence_revision
from generate_site import projected_publication_status


class ReaderPublicationDefaults(unittest.TestCase):
    def test_new_reader_archive_call_lives_in_catalog_not_generator_code(self):
        reader = {
            'slug': 'test-future-reader', 'title': 'Test future Reader',
            'whyItMatters': 'A bounded scenario', 'ghostMeshTakeaway': 'Test the failure mode',
            'overview': 'Source-specific consideration', 'category': 'AI & Technology',
            'tags': ['test'], 'published': '2026-11-11', 'editorialOrder': 51,
            'source': {'kind': 'video', 'platform': 'YouTube', 'mediaAspect': '16:9',
                       'videoId': '45-qbcAeUbM', 'url': 'https://www.youtube.com/watch?v=45-qbcAeUbM'},
            'claims': [{'status': 'unverified'}], 'evidenceState': 'unverified',
            'archiveCall': {'label': 'Test the source claim',
                            'text': 'Compare the identical task twice, record the baseline and the observed outcomes, and retain the original source.'},
        }
        rendered = card(reader)
        self.assertIn('Test the source claim', rendered)
        self.assertIn('Compare the identical task twice', rendered)
        del reader['archiveCall']
        with self.assertRaisesRegex(ValueError, 'archiveCall in content/catalog.json'):
            card(reader)
        reader['archiveCall'] = {'label': 'Incomplete'}
        with self.assertRaisesRegex(ValueError, 'source-grounded'):
            card(reader)

    def test_release_status_is_projection_not_an_edited_reviewed_article(self):
        source = ('<article><p class="gm-publication-status" data-gm-release-status="">'
                  'Status inserted by site generator</p></article>')
        authored_sha = hashlib.sha256(source.encode()).hexdigest()
        reader = {'slug': 'test-future-reader'}
        self.assertEqual(source, source[:])
        draft = projected_publication_status(source, reader)
        self.assertIn('Editorial draft', draft)
        receipt = {'decision': 'accept', 'articleSha256': authored_sha,
                   'evidenceRevision': 'original-review',
                   'ownerDecision': {'pullNumber': 999, 'commentId': None}}
        reviewed = projected_publication_status(source, reader, receipt)
        self.assertIn('Independent editorial review accepted', reviewed)
        self.assertNotIn('Owner-approved', reviewed)
        receipt['ownerDecision'] = {'kind': 'conversation', 'owner': 'Tony Malott',
                                    'approvalDate': '2026-11-11',
                                    'approval': 'Approved after editorial review and bound to the unchanged authored source.',
                                    'articleSha256': authored_sha,
                                    'evidenceRevision': 'original-review'}
        approved = projected_publication_status(source, reader, receipt)
        self.assertIn('Owner-approved for release', approved)
        self.assertIn('does not attest deployment', approved)
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), authored_sha)
        self.assertEqual(projected_publication_status(source.replace('Status inserted', 'Changed'), reader, receipt).count('Owner-approved'), 0)

    def test_verification_receipt_accepts_new_canonical_origin_only_for_exact_slug(self):
        import generate_site
        source = '<p class="gm-publication-status" data-gm-release-status="">Status</p>'
        reader = {'slug': 'next-reader', 'published': '2026-11-28'}
        receipt = {'mergeCommit': 'a' * 40, 'verifiedAt': '2026-11-28T12:00:00Z',
                   'checks': ['article-http-200', 'receipt-http-200', 'catalog-http-200',
                              'sitemap-http-200', 'claim-register-http-200']}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'content').mkdir()
            record = root / 'content/production-verifications.json'
            for origin, accepted in [('https://readers.ghostmesh.ai', True),
                                     ('https://youtube.shareplane.malott.ai', True),
                                     ('https://reader.example', False)]:
                record.write_text(json.dumps({'next-reader': dict(receipt, url=origin+'/next-reader/')}))
                with patch.object(generate_site, 'ROOT', root):
                    result = projected_publication_status(source, reader)
                self.assertEqual('Published November 28, 2026' in result, accepted)
            record.write_text(json.dumps({'next-reader': dict(receipt, url='https://readers.ghostmesh.ai/other/')}))
            with patch.object(generate_site, 'ROOT', root):
                self.assertNotIn('Published November 28, 2026', projected_publication_status(source, reader))

    def test_published_reader_can_disclose_outstanding_independent_review(self):
        from pathlib import Path
        raw = (Path(__file__).resolve().parents[1] / 'content/readers/uncensored-private-or-sovereign.html').read_text()
        projected = projected_publication_status(
            raw, {'slug': 'uncensored-private-or-sovereign', 'published': '2026-11-16'})
        self.assertIn('Published November 16, 2026', projected)
        self.assertIn('independent editorial review remains pending', projected)
        self.assertNotIn('Editorial draft', projected)

    def test_new_archive_recommendation_is_in_review_evidence_binding(self):
        prior = {'slug': 'historical'}
        self.assertEqual(evidence_revision(prior), evidence_revision(dict(prior)))
        future = {'slug': 'test-future-reader',
                  'archiveCall': {'label': 'Inspect', 'text': 'Test source-specific evidence.'}}
        first = evidence_revision(future)
        future['archiveCall']['text'] = 'Change source-specific evidence.'
        self.assertNotEqual(first, evidence_revision(future))
        self.assertNotEqual(evidence_revision(prior), evidence_revision(future))

    def test_future_reader_gate_rejects_missing_metadata_before_review(self):
        article = '<p class="gm-publication-status" data-gm-release-status="">Status</p>'
        future = {'slug': 'test-future-reader', 'editorialOrder': 51}
        self.assertIn('archiveCall', new_reader_canonical_errors(future, article)[0])
        future['archiveCall'] = {'label': 'Check', 'text': 'Grounded recommendation'}
        self.assertEqual(new_reader_canonical_errors(future, article), [])
        self.assertIn('projected publication-status',
                      new_reader_canonical_errors(future, '<p class="gm-publication-status">Old state</p>')[0])
        self.assertEqual(new_reader_canonical_errors({'slug': 'historical', 'editorialOrder': 50}, ''), [])

    def test_existing_reader_without_marker_remains_byte_identical(self):
        historical = '<p class="gm-publication-status">Original review text</p>'
        self.assertEqual(projected_publication_status(historical, {'slug': 'old'}), historical)


if __name__ == '__main__':
    unittest.main()
