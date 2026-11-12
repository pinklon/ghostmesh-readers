# Scout current-run evidence queues | Integration qualification

Date: 2026-10-23. Draft research PR #65.

The integrated nine-panel private Scout now populates five panels with data from the current run or its comparison history:

- **Discovery:** 95 public signals.
- **Relationships:** metadata-linked graph generated from the current intake.
- **History:** observed metadata across two chronological samples.
- **Claims:** 19 *unverified feed-derived candidate excerpts*, clearly marked as awaiting primary-source review and revision witnesses.
- **Public Trails:** 95 observed source URLs. These are **not expanded author-contribution trails** or claims of verified person identity.

The remaining four views are pinned historical research views with a visible status notice.

The new module `scripts/scout_run_evidence_queues.py` builds safe, escaped HTML from triaged current-run source observations without additional network requests. It discloses that feed titles and excerpts are unverified and that observing a URL is not the same as confirming linked works share an author.

**Qualification:** isolated GhostMesh VPS **289 Scout tests PASS**. Integrated run directory `/tmp/scout-trial-34Lfv9/integrated-runs/evidence-queues-20261023-02` contains 11 hashed generated artifacts plus a manifest. All SHA-256 receipts match; the workspace has nine panels. Existing two-snapshot history and new evidence queues can coexist after a corrected manifest allowlist, covered by a regression test.

**Outstanding:** production commissioning remains separate; per-claim source captures and independently verified revision pins, additional contribution-trail discovery, refreshed people/theses/claim-impact analyses, actual user-interface QA, and operational scheduling remain unqualified. Do not equate a current-run *queue* with verified intelligence.

No production installation, schedule, account login, model inference, outreach, or public release occurred. Remote Mac artifact transfer was attempted but blocked by the remote execution safeguard; only the isolated VPS artifact is verified for this increment.
