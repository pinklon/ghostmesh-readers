# Next Reader: one pass

This is the short working checklist for Reader #64 and later. The [release runbook](READER_RELEASE_RUNBOOK.md) remains authoritative. There is one publisher, one draft PR, one independent editorial acceptance, one owner publication decision, and the existing Netlify deployment. This checklist creates no new gate.

## Before implementation

- Qualify the exact source and retained private aids. Record honest acquisition, coverage, transcript/caption method, SHA-256 digests and limitations. Never commit media, full transcripts, captions, private paths or signed URLs.
- Lock the complete original manuscript and presentation together. Use Reader #62 for provenance and the genuine opt-in YouTube thumbnail, and Reader #63 for the robust GhostMesh opening, first assessment, substantive analysis, earned verdict, source chapters and reading rail. Adapt the depth and visuals to the source, without importing their claims.
- Complete the claim/cue map and both relationship decisions: catalog-backed Readers and independently labeled SharePlane Works, with specific rationales or justified zeros. Complete the public-safe receipt wording before rendering.

## One implementation pass

1. Stage the locked authored HTML, catalog record, source map and sanitized provenance together. Use the existing wrappers and projectors, without a new page builder.
2. Run `make reader-prepare`. This regenerates the site and knowledge projections, then runs their drift checks, `check_site.py --local`, the existing Python test suite and `git diff --check`. It does **not** provide release qualification.
3. Review the rendered manuscript against the locked original for omissions, reordering, source/claim meaning, links and disclosures. Inspect the actual preview at desktop and 320/390/430px mobile, including navigation, timestamps, keyboard, dark appearance, video thumbnail/fallback and console health.
4. Obtain independent source/editorial/privacy acceptance on stable authored bytes and evidence hashes. Record the real findings in the existing `content/editorial-reviews/` and `content/editorial-depth/` formats. If content changes, re-review only affected inputs. Run `make reader-prepare` again after binding the receipts.
5. Commit one complete candidate and open one **draft** PR. Confirm remote head, hosted CI, Netlify preview and owner UAT. Request one explicit publication approval for that exact accepted head; do not merge before it. The normal full hosted gate remains authoritative.
6. After an authorized merge, verify `main`, the live article, player, chapter seeks, public receipt, catalog, both relationships, sitemap and source privacy. Close the existing issue with exact merge and production evidence.

**Stop only for a real change or failure:** material editorial/source revisions, invalid privacy/custody, failed checks, changed approved head, or owner hold. Do not introduce a PREPARE approval, a second publisher, repeated source qualification, or another orchestration service.
