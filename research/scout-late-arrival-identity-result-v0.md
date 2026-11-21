# Scout late-arrival and identity uncertainty experiment

Research-only fixture, 2026-10-23. No live source data or person identities.

Twelve arrival-ordered events include older-publication sources arriving after newer ones, two version updates, one duplicate delivery, and name collisions.

**Naive publication timestamp cursor** accepted 6 of 12 deliveries.
**Stable source ID plus revision ledger** accepted 11 distinct revisions and rejected the repeated `paper-c@v1`.
Five valid late or revised source records were missed by the cursor:
`paper-a@v2`, `paper-b@v2`, `paper-c@v1`, `paper-e@v1`, `paper-h@v1`.

The fixture also contains four display-name groups; explicit simulated identifier strings form separate authority-claim clusters. Different synthetic identifier strings for the same display name are not merged. Unresolved same-name attributions stay unconfirmed. These test strings **are not verified ORCID identities**, nor proof of authorship.

Conclusions: source IDs and revisions should drive deduplication; publication timestamps are useful for sorting and discovery windows but unsafe as the sole correctness cursor. Name matching is a candidate search technique, not an identity resolution rule.

Limits: deterministic fixture is synthetic and hand-crafted. A ledger still needs provenance, content hashes, retry policy, paging limits, transient error accounting and verified identifier checks to work in live collection. No current Scout ingestion loss has been demonstrated. No integration, production change or outreach authorized.

VPS result: `/tmp/scout-trial-34Lfv9/scout-late-arrival-identity-v0.json`.
