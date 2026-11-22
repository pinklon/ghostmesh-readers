# Scout | Corrected Independent Review: Unsealed Cohort Comparison

**Date:** 2026-10-23
**Research only:** draft PR #65; no production deployment, public publication or author outreach.
**Status:** corrected second-pass review received and reconciled after the sealed mapping was opened.

## Evidence and version lock

- Pale Horse's independent reviewer discussion: https://ghostmesh.slack.com/archives/D0C76SEPA3G/p1792763827800599
- Original reviewer packet (correction applied in place): `research/scout-blind-review-packet-v0.md`.
- Corrected packet git blob SHA: `9cdf3061b00b0fa9126e03a917ef975cd25b146e`. Pale Horse's second-pass message quotes this exact blob.
- Its 21 opaque IDs are preserved; all records have relevance, novelty and surprise values, source checked status, reason, and strongest objection. 18 source pages were reportedly checked and 16 primary sources inspected in the second pass.
- Cohort key stored privately on isolated VPS as `/tmp/scout-trial-34Lfv9/scout-blind-review-key-v1.json`; not copied into repository. Mapping was opened **after** verifying the second-pass records and packet hash.
- Initial first-pass review: https://github.com/pinklon/ghostmesh-readers/pull/65#issuecomment-6366393052 ; original packet blob `d27d9195a75d4e575e9915fa4d2707ac2505189f`. Preserve it separately from the corrected second pass.

## Corrected cohort results

| Reviewer relevance | Outside-bubble (n=12) | Familiar topic matches (n=9) |
|---|---:|---:|
| 3 strong | 1 | 2 |
| 2 concrete | 4 | 4 |
| 1 speculative | 5 | 3 |
| ABSTAIN | 2 | 0 |
| Strong or concrete | **5** | **6** |
| Primary inspected this pass | 8 | 8 |

The outside-bubble strong-or-concrete group comprises:
1. `SC-ACAB23884D77` GoAgentic: https://github.com/normannoble/GoAgentic (3).
2. `SC-9EB86E136723` Don't Be a Proxy Between Me and Your AI: https://dev.to/adamthedeveloper/dont-be-a-proxy-between-me-and-your-ai-mcn (2).
3. `SC-9082DF49FA74` WebMCP commerce article: https://blog.cloudflare.com/webmcp-commerce/ (2).
4. `SC-2FC3D61ECFC7` SpecEvo: https://arxiv.org/abs/2610.28706 (2).
5. `SC-A7E9EABC13F7` Successive Scale Racing: https://arxiv.org/abs/2610.28815 (2).

These are **independently proposed GhostMesh connections**, not a claim of transfer, originality, independent technical replication, verified author identity, or adoption approval. Some are supported by source README or abstract only.

## Interpretation and limits

The conventional topical cohort had a higher strong-or-concrete share in this handpicked batch, 6/9 versus 5/12. Outside discovery nevertheless surfaced five plausible connections from sources the conventional keyword filter would have excluded. The cohorts are intentionally selected, small, and unbalanced; neither ratio estimates population recall. There is no randomized discovery sample, no replicated independent jury, and no measured equal wall-clock review budget. Pale Horse's second pass had access to memory of its own first pass and thus is **not fresh blindness**; it explicitly did not consult the sealed key or earlier Scout verdicts. Reviewer attestations are not independently witnessed.

## Decision

**Keep both lanes.** Use topic matching to prioritize familiar technical relevance, and reserve a bounded source-balanced outside-vocabulary exploration budget, preserving original receipts and false-negative review cases. Do not promote any source to implementation or outreach automatically.

Next discriminating test: independently evaluate a new *unseen* feed snapshot with genuinely blind reviewers, instrument actual source-open/time budgets, compare source-backed utilities rather than only lexical relevance, and record disagreements. Do not add more approval machinery for this low-risk owner-private research.

Reference scope only; do not mistake the Netlify PR deploy preview for a production release.
