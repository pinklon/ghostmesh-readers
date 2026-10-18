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

The previous site checker passed at baseline. This replacement preserves URLs and timed navigation through baseline-derived invariants, rather than retaining brittle requirements for all old videos to appear as homepage cards. No infrastructure workflow was added; existing CI runs the enhanced checker and targeted regression tests.
