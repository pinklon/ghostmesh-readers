# Scout fresh blind study 2 | Frozen packet qualification

Date: 2026-10-23. Research-only draft PR #65.

- New source collection: 95 unique public URLs, of which 47 did not occur in the prior 59-lead snapshot.
- Source-diverse blinded experiment: 14 fresh cases from 9 source streams, with six familiar-topic and eight outside-vocabulary cases.
- The sealed cohort key is owner-private on the isolated VPS, not committed or revealed.
- Original reviewer packet: `research/scout-fresh-blind-review-2.md`, Git blob SHA `bb01ce7fff465f465cc743246529e5e80201e616`.
- Frozen research JSON: `/tmp/scout-trial-34Lfv9/scout-fresh-blind-packet-v2.json`.
- New deterministic renderer: `scripts/scout_fresh_review_render.py`.
- Rendered packet JSON digest: SHA-256 `e39a7a16ebee0870ad5547063c3fba57bec648140a772defb484eff969a86806`.
- Generated reviewer document preserved all **14 review IDs in the same order** as the existing packet; the reviewer-facing Markdown was intentionally **not replaced** while Pale Horse's assessment is in progress.
- Latest isolated VPS checkout test: **280 Scout tests PASS**.
- Pale Horse acknowledged the fresh 14-case assignment; no second-study ratings were yet available when this receipt was recorded.

Limits: the JSON hash witnesses the exact input document, not external source truth. Matching opaque IDs and order do not establish independent review quality or statistical representativeness. Do not unseal the new cohort key until independent ratings are completed and verified.

No production merge, deploy, scheduled collector, outreach, or paid inference.
