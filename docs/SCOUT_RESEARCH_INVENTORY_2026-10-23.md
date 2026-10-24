# Scout research evidence and publication inventory
As-of: 2026-10-23. Owner-private planning classification expressed in public-safe terms only.

This inventory distinguishes **source-committed public copy** from **production HTTP verification**. It is not a private Scout data export, nor evidence that every research run has been found. Counts below are limited to the inspected Readers repository. Source location is a proof pointer, not a claim of independent replication.

## A. Public editorial works: 9 confirmed source records

All nine source files exist in `pinklon/ghostmesh-readers`. The three review URLs are generated from `content/scout-public.json`; the six essays have committed static HTML and retained editorial drafts. They entered the unified public index through merged PR #72. The main-branch index and nine public routes were verified after that release.

| Stable public ID | Title | Source of record | Public route | Disposition |
| --- | --- | --- | --- | --- |
| cloudflare-security-audit-skill | Cloudflare security-audit-skill | `content/scout/reviews/cloudflare-security-audit-skill.md` | `/scout/reviews/cloudflare-security-audit-skill/` | Approved source review; no audit executed |
| graphify-labs-graphify | Graphify | `content/scout/reviews/graphify-labs-graphify.md` | `/scout/reviews/graphify-labs-graphify/` | Approved documentation review; no graph built |
| nvidia-openshell | NVIDIA OpenShell | `content/scout/reviews/nvidia-openshell.md` | `/scout/reviews/nvidia-openshell/` | Approved documentation review; runtime untested |
| essay:the-signal-is-not-the-finding | The Signal Is Not the Finding | `content/scout/publication-drafts/01-the-signal-is-not-the-finding.md` | `/scout/essays/the-signal-is-not-the-finding/` | Existing original editorial essay |
| essay:follow-the-work | Follow the Work, Not the Follower Count | `content/scout/publication-drafts/02-follow-the-work-not-the-follower-count.md` | `/scout/essays/follow-the-work/` | Existing original methods essay |
| essay:five-ideas-outside-the-filter | Five Ideas Outside the Filter | `content/scout/publication-drafts/03-five-ideas-outside-the-filter.md` | `/scout/essays/five-ideas-outside-the-filter/` | Existing original comparison; bounded cohort |
| essay:a-faster-review-button-is-not-a-better-decision | A Faster Review Button Is Not a Better Decision | `content/scout/publication-drafts/04-a-faster-review-button-is-not-a-better-decision.md` | `/scout/essays/a-faster-review-button-is-not-a-better-decision/` | Existing original source comparison |
| essay:the-plateau-that-lied | The Plateau That Lied | `content/scout/publication-drafts/05-the-plateau-that-lied.md` | `/scout/essays/the-plateau-that-lied/` | Existing synthetic experiment discussion, not production measurement |
| essay:latent-states-are-not-an-agent-api | Latent States Are Not an Agent API | `content/scout/publication-drafts/06-latent-states-are-not-an-agent-api.md` | `/scout/essays/latent-states-are-not-an-agent-api/` | Existing paper/code assessment, not reproduction |

The six publication drafts are retained editorial source counterparts, **not six additional articles**. Each of the six rendered HTML pages is under `site/scout/essays/<slug>/index.html`. No new RSS items should arise from indexing old content. The historical essays have no explicit dated release-event entries in `content/public-release-events.json`; do not infer dates.

## B. Public support and method records: not counted as distinct works

| Evidence | What it proves | Next disposition |
| --- | --- | --- |
| `content/scout/method.md` and `site/scout/method/index.html` | Expanded public method page now covers distinct acquisition lanes, source provenance, evidence levels, experiment boundaries, and explicit unknowns | Published through PR #74 on October 23, 2026; retain and update the evidence status distinctions |
| `content/scout/editions/2026-10-22-first-look.md` | First dated three-review edition; organizing wrapper, not a fourth independent investigation | Keep existing URL and list as an edition, outside the nine-work count |
| `content/scout/publication-drafts/02-follow-the-work-not-the-follower-count.md` | Detailed 12-stream pilot, 36-lead capped sample, familiar/outside-vocabulary lanes, evidence ladder and limitations, as editorially described | Primary narrative source for new method guide; verify each operational assertion before claiming it is still current |
| `content/scout/publication-drafts/03-five-ideas-outside-the-filter.md` | Published editorial account of corrected 21-item comparison with significant selection limits | Use for an experiments ledger summary; do not invent raw cohort evidence |
| `docs/SCOUT_PROVIDER_WATCH.md`, `content/scout/provider-sources.json`, `scripts/scout_provider_watch.py` | A bounded official-provider observation lane with 30-day artifact retention and daily GitHub Actions schedule | Publish a method appendix only after a real default-branch source-level run is inspected; provider notices are leads |
| `docs/SCOUT_PROVIDER_DIFF.md`, `scripts/scout_provider_diff.py` | Offline comparison distinguishes changed source entries from verified feature releases; failures are UNKNOWN | Explain the difference between detection, independent assessment and editorial publication, with synthetic examples explicitly labelled |
| `docs/SCOUT_AND_FEED.md` and `content/public-release-events.json` | Public publication/RSS boundaries; only explicit approved events become feed items | Include in publication methods, but do not expose internal operator procedures |

## C. Research needing evidence reconciliation before public admission

These are **candidate families**, not counted investigated works. A reference in a draft is insufficient evidence of a retained source record.

| Candidate family | Currently witnessed | Missing for admission | Disposition |
| --- | --- | --- | --- |
| Additional 12-stream Scout runs and their discovery records | The existing method essay describes one capped 36-lead pilot | Current run IDs, public-safe normalized source URLs, observation dates, snapshots, deduplication receipts and reviewer dispositions | HOLD, private inventory source required |
| Corrected 21-item comparison and later 14-case study | Existing editorial draft references separate rounds | Distinct cohort identifiers, saved fixtures, methodology revisions and counterexamples; do not combine denominators | HOLD for source reconciliation; published essay remains as historically qualified |
| Synthetic plateau/stopping experiments | A public essay describes controlled fixtures and limitations | Retained executable fixtures, results and provenance for a reproducibility companion; no production-outcome implication | EDITORIAL DEVELOPMENT, no automatic new article |
| First-party provider release observations | `#69`, observer script, scheduled workflow and offline differ | Reviewed actual scheduled artifact; first-party source status, date, availability, entitlement and source-level failures | REVIEW CANDIDATE only; no public capability claims |
| Lab collaboration tests with Dennis, Vic and other participants | Conversation-level proposals to resume testing | Approved test protocol, actual results, participant disclosure consent and first-party evidence | PRIVATE/UNVERIFIED; no public claims or named-person directory |
| Other private Scout research packets and ten-panel workspace | Published articles mention a separate owner-controlled workspace | Authorized read-only private inventory, exact IDs, source provenance and owner disclosure decisions | UNKNOWN count and disposition; never infer zero or auto-export |

No public repository evidence establishes the total size of the owner-private historical corpus. Its count is **UNKNOWN**, not zero. This document does not certify access to that private corpus.

## D. Next substantive publication tranche

1. **Method guide:** `How GhostMesh Scout Actually Researches` is published at `/scout/method/` through PR #74. Future amendments should preserve the distinct acquisition lanes, source versioning, deduplication, outside-vocabulary selection, evidence ladder, counterevidence, uncertainty, human authorization, and the distinction between implemented and proposed mechanisms.
2. **Research journal:** an unpublished editorial draft is staged at `content/scout/publication-drafts/08-the-research-journal.md`. It cross-references the 21-item comparison and synthetic stopping experiments. A rendered public page and raw-result appendix remain HOLD pending evidence review, Creative Lock and owner approval.
3. **Historical reconciliation:** inventory owner-private research by stable identifiers using a read-only custodian and a redacted classification worksheet. Emit counts by investigated, approved, published and withheld only when backed by inspected records. Never require Tony to manually classify all items or expose private files publicly.

## E. Release and ownership boundary

- The nine-work Research Library was released via [merged PR #72](https://github.com/pinklon/ghostmesh-readers/pull/72), with production verification reported after merge. The expanded methodology was released through [merged PR #74](https://github.com/pinklon/ghostmesh-readers/pull/74), merge commit `2616079a74b8da06856de6a19b197455d2a5daf0`, and production content observed at `https://youtube.shareplane.malott.ai/scout/method/` on October 23, 2026.
- Tony and segfault own the editorial thesis, source/counterevidence choice, exact public copy, relationship decisions and publication authorization. Mechanical execution may wire approved content into the static Netlify generator and run checks.
- The method guide is already published. The research journal remains an editorial draft; later public rendering requires a separate owner-locked release and exact-head authorization. No automatic public release, credential/identity changes, database, RAG or private source export. Preserve existing URLs.
- Acceptance: source provenance and status table, genuine counterexamples, all material unknowns, full CI, exact-head Netlify preview, desktop/mobile UAT, then Tony's exact-head merge approval. Record production HTTP verification separately.
