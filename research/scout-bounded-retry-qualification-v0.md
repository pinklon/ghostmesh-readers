# Scout bounded pending retry runner | Qualification receipt

Research-only implementation, 2026-10-23. Added `scripts/scout_bounded_retry.py` and isolated tests.

The runner consumes the **existing** persistent state queue, validates every pending public source against the collector's HTTPS host allowlist, and performs at most three bounded retries per invocation, with a maximum of three total attempts per source. The default command mode is **dry run** and makes no network calls. Actual one-shot reads require `--apply`; there is no schedule, background loop, model invocation, contributor contact or production installation.

It uses the existing public source collector to obtain a byte snapshot and SHA256 receipt. A failed attempt emits a typed failure record without advancing the source-revision ledger; successful captures clear the pending entry and record the content hash; attempted duplicate revisions remain distinguishable. Any exhausted item is reported for review instead of retried indefinitely. This is not permission to access arbitrary URLs.

## Evidence

- **237 Scout tests PASS** on the isolated GhostMesh VPS.
- Dry run on the existing two-run research state: zero eligible pending sources and **zero network calls**.
- Disposable end-to-end trial: an explicit pending record for `https://arxiv.org/abs/2610.28686v1` was retried once. Public fetch succeeded, captured bytes were hashed and the `v1` source revision was accepted. Queue changed from one pending to **zero**, without touching the earlier research state.
- Disposable trial receipt: `/tmp/scout-trial-34Lfv9/scout-bounded-retry-public-fixture-receipt.json`.
- Disposable trial state: `/tmp/scout-trial-34Lfv9/scout-bounded-retry-public-fixture-state.json`.

## Scope and limitations

The runner is an explicit offline operator command, **not** a live collector or unattended retry service. Its retry categories are deliberately coarse; a future enhancement can preserve HTTP status, retry-after guidance, precise exception classification and complete recovery traces without exposing private metadata. The separate receipt and state writes are atomic individually, not one database transaction. If interrupted between them, an operator must reconcile the receipt/state pair before rerunning; the same version dedupe key prevents repeat source-revision acceptance but not a repeated HTTP GET.

No production deployment, credentials, paid inference or outreach. The next reasonable work is widening sources and discovery rather than building more retry machinery.
