"""Regression tests for the single-pass Reader publication contract."""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from catalog_design import card
from check_site import new_reader_canonical_errors
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
