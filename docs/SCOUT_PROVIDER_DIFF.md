# Scout provider observation comparison

This bounded, offline tool compares two previously collected first-party provider observation JSON files. It generates review-only candidate changes. It neither fetches networks nor mutates the repository or public site.

```bash
python3 scripts/scout_provider_diff.py --previous previous.json --current current.json --output candidates.json
python3 -m unittest discover -s tests -p 'test_scout_provider_diff.py'
```

- A new source-entry URL produces one unreviewed candidate; repeated URLs are deduplicated within each source.
- A changed title at a stable URL produces a review candidate, **not** a verified announcement, pricing revision, GA transition or deprecation.
- The same entry on a later day is not reannounced.
- A missing or failed source yields `UNKNOWN`, never a zero-release conclusion.
- Removed entries are not treated as deprecations.
- Every candidate is `NOT_APPROVED` and must undergo first-party evidence and owner editorial review before inclusion in #68.

This first increment deliberately does not download the previous GitHub Actions artifact, run a semantic classifier or publish anything. Retained artifacts expire after 30 days. A subsequent change will connect adjacent scheduled-run artifacts and add source-specific status evidence. Never infer Tony's account entitlement from a public release notice.

Related: #69 and #68.
