# Scout Research Library: content-only tranches

The canonical public register is `content/scout-research.json`. The generated searchable catalog is `/scout/research/`. The earlier `/scout/archive/` and `/scout/essays/` addresses remain stable.

1. Secure Tony's editorial approval of the complete public Markdown or static essay, evidence boundary, provenance, topic tags and any exact related-work IDs. Do not export private Scout scans or internal experiments.
2. Put reviewed source content at its existing stable location (`content/scout/reviews/<id>.md` for investigations; `site/scout/essays/<slug>/index.html` for legacy essays). Future essays should use the existing public essay layout and its canonical trailing-slash URL. Never silently rewrite published text.
3. Add one `published` entry to `content/scout-research.json`. Set a unique stable ID/slug and exact source path. Add only owner-approved `relatedIds`. For new publications, add the dated explicit event to the release ledger before entering its ID in `releaseEventId`. The six historical essays were published before that ledger: their null IDs deliberately preserve an unresolved historical gap and do not create retroactive RSS announcements.
4. Run `python3 scripts/generate_site.py`, `python3 scripts/generate_site.py --check`, `python3 scripts/check_site.py`, and `python3 -m unittest discover -s tests -p 'test_*.py'`. Check the generated index, links, sitemap and absence of private files.
5. Review a Netlify deploy preview on desktop/mobile. Tony approves semantic/visual UAT and the exact PR head before merge. Verify production HTTP routes and Netlify deploy ID afterward. Keep unknowns UNKNOWN.

No database, semantic-autolinker, reader rewrite or ingestion job is needed. Public research inventory and historical private Scout candidate counts must remain separate until independently reconciled.
