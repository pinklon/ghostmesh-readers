# Scout public editorial launch | Release candidate plan

Status: **THREE UNPUBLISHED ESSAY DRAFTS COMPLETE; NOT YET A SITE RELEASE**. 23 October 2026.

## Publishable story versus private product

Scout already has a public Readers section at `/scout/`, with the first-look product review archive, methodology and public review pages. The newer GhostMesh research Scout also uses the name "Scout." The release must clearly establish that these are related but different surfaces:

1. **Public Scout** is edited, attributable analysis on the Netlify Readers site.
2. **Private GhostMesh Scout** is the owner's research acquisition, triage, history and analytical workspace. Its ten-panel workspace, run receipts, attribution queues and source snapshots do not belong on Netlify.
3. The public essays **explain the discipline and selected aggregate research evidence**, not grant public access to private intelligence or claim that the public Scout review archive updates in lockstep with the private daily collector.

These distinctions belong above the fold of the eventual public landing experience. Do not reuse the name without explanation.

## Three editorial launch candidates

1. `content/scout/publication-drafts/01-the-signal-is-not-the-finding.md`
   - Proposed main story: **The Signal Is Not the Finding**.
   - Core thesis: discovery is not verification, and verified continuity is more valuable than collecting more content. It explains privacy, authority, human interpretation and provenance.
   - Reader fit: flagship GhostMesh essay and the introduction to the research capability.
2. `content/scout/publication-drafts/02-follow-the-work-not-the-follower-count.md`
   - Proposed companion: **Follow the Work, Not the Follower Count**.
   - Core: 12 bounded streams, sampling bias, normalized metadata, source versions, familiar/outside lanes, evidence ladder, and when a connection thesis deserves credence.
   - Reader fit: transparent methodology with a source-by-source limitation table.
3. `content/scout/publication-drafts/03-five-ideas-outside-the-filter.md`
   - Proposed evidence article: **Five Ideas Outside the Filter**.
   - Core: corrected 21-case comparison, full cohort counts, five linked potential connections, selection bias, counterevidence, and next discriminating experiment.
   - Reader fit: critical original analysis rather than a product announcement. Do not market `5/12` as population precision, `6/9` as a superiority estimate, or reviewer judgments as replicated benefit.

Each draft has ~1200-1300 words and primary public links or a precise method citation. They are original authored prose, not copied source text.

## Editorial gates before Netlify production

**Content review**
- Fact-check the *live code* and the first scheduled collector execution receipt before publishing operational statements (first scheduled run due October 24, 2026 at 08:00 Pacific; commissioned on October 23). Draft methodology currently says `research pilot`, so refresh the tense and count status before publication.
- Independently re-check cohort totals against `research/scout-second-pass-unsealed-reconciliation-v0.md`. Separate the first pass, corrected second pass and newer 14-case study; do not combine different review rounds.
- Verify each external research link, source authorship and accessible original. Where only README/abstract inspected, do not state replicated performance. A cited work's existence does not certify its conclusions.
- Review claims about identity, outreach and privacy. No person directory, private scout intake, personal data, Slack discussion contents, SSH/GPG fingerprints, hostnames, private repository credentials or research packet bytes in public pages.
- Editorial depth: strongest counterargument, explicit unknowns, genuine next test and original synthesis, not a superficial three-paragraph announcement.

**Site integration**
- Prepare a **separate editorial release PR branched from current `main`**. Do not merge research PR #65 wholesale: it carries private-operational engineering and should not be treated as a publication batch.
- Add three stable public route slugs under existing `/scout/` navigation, e.g. `/scout/essays/the-signal-is-not-the-finding/`, `/scout/essays/follow-the-work/`, and `/scout/essays/five-ideas-outside-the-filter/`. Exact slugs to be settled in the editorial release PR.
- Use the canonical Readers design system and typography, light/dark parity, responsive layout, correct share labels, semantic links and mobile behavior. Keep no portrait of Tony, no public source packs, and no invented video player or timestamps for original essays.
- Update the public Scout introduction to link the three articles without confusing public first-look reviews with owner-private research.
- Generate the catalog/knowledge/search/sitemap projections only as appropriate for **new editorial articles**, under the existing publishing runbook, without altering historical Reader count to imply these are video deconstructions.
- Make one Netlify PR preview. Inspect all three routes and the Scout landing page in Chrome desktop and mobile emulation, run `generate_site.py --check`, `check_site.py`, full tests and `git diff --check`. Check linked references and noindex only on unreleased preview pages.

**Release authorization**
- Independent editorial findings and the canonical owner article approval must bind the actual candidate PR/version under `docs/READER_RELEASE_RUNBOOK.md`, with separate exact-head decision before merging. Preview green is not publication permission.
- Merge only after owner approves final text and release. Record production Netlify deployment, live routes, sitemap, catalog/search and privacy witness.
- Do not launch an unsolicited press/outreach campaign or a public dashboard.

## Honest readiness verdict

**Ready today for an editorial PR and Netlify preview after the article rendering/integration step. Not yet ready for production publishing.** The difference is editorial release acceptance, final site build QA and clear public/private labeling, *not* another research infrastructure program. Publication can follow within the next normal release cycle if review and checks pass; no unsupported fixed deadline or unobserved deployment success is implied.

## Proposed public launch introduction

> GhostMesh Scout is about finding useful ideas without confusing discovery with proof. Its public articles show how sources are selected, how uncertainty is retained and what a small outside-the-filter experiment actually taught us. The underlying research workspace remains private, with human control over consequential decisions.
