# GhostMesh Readers public knowledge integration receipt

## Scope and provenance

This candidate combines the reviewed relationship data/UI cap repair for Readers issue #23 with the source-only knowledge contract from issue #11. It begins at PR #24 head `8f26c8456841360212a84cc4e42f8434c8125645`. The issue #11 origin is local commit `27361bcf3f9d645ef4ecb08a931b5262f2c1063b` on `codex/issue-11-public-knowledge-contract-v01`; that original branch and its checkout remain unchanged. The integration is on a new isolated branch, `codex/readers-convergence-20261018`. Its final commit and test receipt are reported outside this tracked file to avoid a self-referential hash.

## What is projected

The public knowledge v0.1 source has one versioned Reader identity record for each of the 13 current catalog entries. Only the existing Inbox Reader claim and Swarmchasers citation are projected as claim/evidence records. Their exact text, anchor and URL were inspected after the Reader migration. The full Inbox page hash changed from `ba08d224c5acf6fed0b37774b6ba5e39086b5c449482bfce9082daba6e73eeef` to `8e18056341ec6d981a0e80d1d6526771a3cf446d9435a1d044bf170295c40ac4`; the new digest is pinned in the v0.1 source. The external report's content hash stays `null` because its bytes are not in public repository custody.

The knowledge page uses the normalized theme and site shell. Homepage discovery and `/knowledge/` sitemap entry come from the normal generator. The checker admits only the two new reviewed text formats (`site/llms.txt` and JSON-LD) and keeps public privacy checks. CI calls the site checker, knowledge byte-for-byte check and full Python unit suite. The local relation cap fix preserves every qualified relation in catalog and receipt while displaying four cards, with a synthetic fifth-edge regression fixture. Public SharePlane Work admission and cross-site relationship edges remain outside this scope.

## Stage and boundary

This file records source intent, not a signoff. Before PR review, run both generator `--check` modes, the site gate, full tests, browser/mobile/theme/keyboard/no-JavaScript checks, public privacy/URL checks, diff hygiene, and an independent review on the exact committed head. Record exact commands, outcomes, PR, CI and preview in the task receipt. A Netlify PR preview is automatically produced when a draft PR is opened; it is a review surface and does not prove production deployment. Tony retains merge and production promotion authority.

No private ReasonPack media, transcripts, captions, paths, credentials, external corpus identifiers, new hosting provider, DNS change or service installation belongs in this source candidate. The 131 of 148 unverified claim statuses remain unpromoted. Before merge, rollback is to close or discard the draft PR. After a separately authorized merge, revert that commit or restore a prior successful Netlify deploy.
