# Scout stopping reproducibility companion: editorial lock and implementation boundary

Status: Tony accepted the full manuscript on November 6, 2026 Pacific. Source is frozen for draft implementation; public release is not authorized.
Issue: https://github.com/pinklon/ghostmesh-readers/issues/76
Lane: GhostMesh Scout / reproducibility companion.
Owner and editorial authority: Tony Malott and segfault. Mechanical executor: Codex.

## Identity and immutable editorial source

- Title: The Plateau That Lied: Reproducing the Experiment.
- Subtitle: What three deterministic experiments actually establish about search, stopping decisions, and the limits of synthetic evidence.
- Byline: Tony Malott | GhostMesh Scout.
- Slug candidate: `/scout/essays/the-plateau-that-lied-reproducing-the-experiment/`.
- Source: `content/scout/publication-drafts/24-the-plateau-that-lied-reproducing-the-experiment.md`.
- Original owner-supplied attachment SHA-256: `f8f62a9d03ba75536ba73cdc79800201719e03623621d2205f5c269f7a9280fc` (no terminal newline).
- Repository Markdown SHA-256: `b4523498d768858afd60b7f59a400ed35e5a6e871593d069c9f42c3e9221da07` (one terminal newline added by patch serialization, prose and Markdown otherwise identical).
- No compression, paraphrase, table replacement, order change, or semantic reinterpretation.
- Reader audience: technically literate readers challenging reported synthetic results and agent stopping claims.

## Evidence, disclosure, and claims

- Primary evidence: pinned commit `d46047390869ff372aa6239053ef882bd1b60a65`, scripts at Git blob SHAs `265d75d392b79e986c2afe957982f275ea833f91`, `c807e3b5d92efe7800d22d533b92c6608bb8a046`, `2753367dcedf3d3b17f3f9151a3c2e1d7766c3a9`; `docs/SCOUT_STOPPING_REPLAY_RECEIPT_2026-10-23.md`.
- Supporting public context: `/scout/essays/the-plateau-that-lied/` and `/scout/research-journal/`.
- Claim posture: synthetic deterministic counterexamples and same-implementation replay. Neither independently implemented replication nor operational effectiveness is claimed.
- Key claims: search 432 rows and strategies 144 trials each; stopping 240 rows and late-breakthrough 20/20 premature basic stops; probe 240 rows and no win against the better alternative across four designed regimes. All exact figures remain in the locked Markdown.
- Original raw archive hashes: UNKNOWN. Independent algorithmic replication: NOT ESTABLISHED. Production savings or generalization: NOT ESTABLISHED.
- Public-safe exclusions: private packets, participant data, media/transcripts, credentials, service endpoints, model dispatch, production policies and private archive exports.
- Required evidence boundary: preserve the accepted final paragraph verbatim until a separately accepted publication-stage correction.

## Design and publication constraints

- Reuse the established Scout essay wrapper, site navigation, footer, light/dark controls and responsive tables from the strongest current comparable essay.
- Static HTML and standard-library Python only; no new backend, model calls, analytics, external runtime or dependencies.
- No invented relationships; only the two approved public contextual links and issue/source references in the manuscript. Do not mutate the existing Research Journal or older article.
- The source package is allowed as a standalone private/draft implementation before editorial page release: pinned scripts, one-command runner, 912 synthetic per-trial rows, summaries, seed/configuration manifest, SHA-256 output hashes, overwrite refusal, deterministic rerun and negative mutation test.
- Runner must never overwrite output, access private records, contact a service, dispatch a model, or change production stopping rules. Inspect every JSON output field for public safety.
- Original raw archive hash reconciliation remains UNKNOWN unless exact originals are recovered and checked.
- Page candidate, Scout discovery/index, RSS event and Production release remain separate approval decisions. No publication event in this tranche.

## Validation and UAT

- Verify source blobs by Git blob IDs; verify row counts and summary values against the October 23 receipt.
- Verify repeated output hashes on a clean rerun and failure after deliberate fixture mutation.
- Run current repository site checks and focused source/public-safety tests, plus `git diff --check`.
- Validate desktop and 390px mobile, table overflow, anchors, links, light/dark behavior and browser console on Netlify preview.
- Keep a draft PR, automerge disabled, and record exact source/head hashes and checks. Tony owns UAT and exact-head merge authorization.

## Publication-stage editorial hold

The accepted manuscript says the public package is a *next step* and *not yet implemented or released*. Once a package is actually built, publishing those lines unchanged would be misleading. Do not silently rewrite the accepted copy. Request Tony's focused approval of a narrow status update before marking the draft ready or merging. No need to reopen the article's thesis or other sections.

## Scope and rollback

- Branch: `segfault/scout76-repro-companion-draft-20261106` from clean `main` at `7320fd0ff331936c42c1d66124c30145160bbb89`.
- Allowed: one source Markdown file, this lock, scoped reproducibility runner/data/tests, later approved Scout page and mechanically necessary discovery/receipt files.
- Forbidden: other Scout drafts, existing articles, private assets, production policy, runtime services and release events without explicit permission.
- Rollback before merge: close the draft PR or delete its isolated branch; Production unchanged.
- Gate: draft preparation only. Exact-head merge requires separate Tony authorization after source, CI and browser acceptance.
