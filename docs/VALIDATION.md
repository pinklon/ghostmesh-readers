# Validation receipt

The final exact Git head and PR URL are reported in the delivery receipt outside the commit, avoiding a self-referential commit hash. These commands are reproducible from the repository root.

```sh
python3 scripts/generate_site.py --check
python3 scripts/check_site.py
python3 -m unittest discover -s tests -v
```

Passed: 37 generated projections; all 13 Reader routes, retained chapter starts and historical Reader anchors; complete sitemap; homepage feature plus six cards; all 13 archive records; reference IDs and dates; qualified relation provenance; decoded no-em-dash text; current-tree source-artifact boundary; 10 negative publication tests.

Development-only browser checks require an existing Playwright installation and Chrome. They add no hosting dependency:

```sh
python3 -m http.server 8765 --directory site
# In another terminal, with Playwright resolvable through NODE_PATH if needed:
GM_TEST_OUTPUT=/tmp/ghostmesh-reader-checks node scripts/browser_check.cjs
GM_TEST_OUTPUT=/tmp/ghostmesh-reader-checks node scripts/keyboard_check.cjs
GM_TEST_OUTPUT=/tmp/ghostmesh-reader-checks node scripts/contrast_check.cjs
```

Observed candidate results: 60 viewport/theme cases (15 pages × 390/1440px × light/dark), no overflow or premature player load; search and category/tag intersection; persistent explicit appearance and system changes; 13 opt-in player controls; 13 keyboard/reduced-motion/blocked-storage cases; 28 no-JavaScript cases; computed ordinary-text contrast sweep in both themes. External requests are blocked in these browser tests. Streaming playback itself is not attested.

Independent review identified and prompted fixes for source-date labeling, evidence direction, claim coverage, historical temporal scope, aggregate evidence labeling, curated sorting, repository-wide media checks and light-theme contrast. Final signoff must reference the delivery head. Reference-fidelity research is separate from exact-head code review and is timestamped in the catalog.

Public outgoing-link check on October 18: 177 distinct HTTPS links, 175 returned HTTP 200 to HEAD. Two remain explicitly unconfirmed: the historical SharePlane source Markdown URL returned 404; OpenAI's historical Hugging Face incident article returned 403 to automation. Neither result certifies a missing article or disproves the underlying claim. Original URLs are retained rather than silently redirected to a guessed destination. The fresh METR incident reference supplies separately scoped evidence.

The previous site checker passed at baseline. This replacement preserves URLs and timed navigation through baseline-derived invariants, rather than retaining brittle requirements for all old videos to appear as homepage cards. No infrastructure workflow was added; existing CI runs the enhanced checker; targeted regression tests run locally and during independent review. The original workflow is unchanged because the existing OAuth credential does not permit workflow edits.

## PR review repairs

The later GitHub review found three gaps in the earlier implementation signoff: omitted capture containers, a contrast script that did not fail its process, and a fixed no-JavaScript archive count. These are repaired on the existing branch. The original signoff does not cover these repairs; exact-head fresh review is recorded in the PR and delivery receipt.

The public directory now permits only the site's reviewed UTF-8 text asset types and two named hosting files. Unknown formats fail closed. Common capture signatures, binary content and symlinks are rejected; repository-wide capture-extension checks include Matroska, audio and caption formats. This bounded gate is not a claim to identify every possible disguised text transcript. Private packs and Git history are untouched.

Run the additional development regression fixture with Playwright and Chrome available:

```sh
node tests/browser_regressions.cjs
```

It checks a 14-card archive with JavaScript disabled, rejects missing/extra cards, detects deliberately low-contrast text in a real browser and proves the report process exits 1. A readable fixture passes. The full contrast suite now exits nonzero on violations or execution errors. Catalog cards explicitly display the unverified-claim count; all 131 of 148 unverified statuses are unchanged.

The historical SharePlane source URL returning HTTP 404 is confirmed broken and has been explicitly de-linked in the Reader while preserving attribution. The OpenAI incident URL returning automation HTTP 403 is UNKNOWN, not classified as broken. Current availability reruns are recorded separately in the delivery evidence. Historical link-check counts above describe the original run only.

## Shared shell and source preview revision

The generated home, archive, knowledge index and 13 Reader pages now use one Reader-derived top shell with one theme control. The Reader editorial bodies, near-top brief, retained historical anchors and chapter controls are independent of that shell. The full archive is present in static HTML; the local search is progressive enhancement, not an estate-wide search service.

The homepage displays six current YouTube source thumbnails from the same public `i.ytimg.com` host already used by Reader source pages. Those are third-party **image requests before Play**; they do not load an iframe or video stream. The Instagram Reel has no durable approved public poster URL in its source record, so it uses a labeled fallback and direct source link. A deliberate Play click creates one non-autoplay inline iframe; the Open Reader and original-source links remain separate. No source media, caption, transcript, proxy or player dependency was added to Git.

With a local static server, Playwright and Chrome available, run:

```sh
node tests/visual_revision_regressions.cjs
node tests/player_regressions.cjs
```

The first checks one shell and heading per route, responsive light/dark behavior, legible light-mode signal tokens, 13 static archive entries, local search/reset, seven separate home Reader/source actions, click-gated non-autoplay playback and no-JavaScript links. The second checks all Reader source-player shapes, opt-in behavior, external fallback and reduced motion. Visual acceptance still requires owner review of the draft deploy preview.
