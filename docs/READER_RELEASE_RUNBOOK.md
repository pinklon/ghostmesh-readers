# Reader release runbook

This is the one publication queue and release path for `pinklon/ghostmesh-readers`. One accepted publisher owns a candidate from source handoff through the final production receipt. Source custodians and independent reviewers can supply evidence or read-only findings; they do not start competing uploads. The public repository contains original analysis and sanitized receipts, never copied media, captions, full transcripts, private source packs, signed URLs, or credentials.

## Canonical queue and evidence

The status table below is the one maintained Reader queue. Add a row when a source is accepted; update its public-safe evidence status or receipt reference, exact candidate head, review gate, PR and deployment state as work advances. The publisher's task receipt holds detailed evidence for these fields, not a second status queue. Keep private custody in private storage and cite only sanitized evidence in public Git. Do not create a second tracker or uploader.

| Field | Required entry |
| --- | --- |
| Original source | Exact video URL and ID, publisher/title, duration, native aspect, and available chapter timestamps. |
| Private evidence | Custodian and private source/caption/transcript hash receipt; acquisition coverage and limits. Record hashes and status, not private paths or source bytes in Git. A verified ReasonPack is one possible source, not a universal prerequisite. |
| Claim review | Dated claim/evidence/counterevidence ledger, source roles, unresolved claims, and the public disclosure boundary. |
| Candidate | Sole writer, branch, exact commit, article hash, and catalog/graph relationship assessment, including a justified zero-link result when appropriate. |
| Editorial gate | Independent review of exact article and public receipt; findings and resolution. Reuse that review while those reviewed bytes and source claims are unchanged. Review changed material again. |
| Deployment | PR and exact head, CI and Netlify preview, owner publication decision, production commit, live page/catalog/map/sitemap checks, and final receipt. |

Current queue checkpoint, October 20, 2026: the production catalog has 25 Readers. Issue 46 is the accepted, unpublished candidate; the candidate branch projects 26. Update this table when that changes; a dated checkpoint is not a substitute for maintaining the rows.

| Exact source | Public-safe evidence gate | Candidate and editorial gate | Deployment state |
| --- | --- | --- | --- |
| [David Ondrej, `DwoWIf8f2yQ`](https://www.youtube.com/watch?v=DwoWIf8f2yQ) | Private full auto-generated transcript aid qualified; [issue 46 intake receipt](https://github.com/pinklon/ghostmesh-readers/issues/46#issuecomment-6305102689). No media or captions in Git. | Sole publisher candidate on `codex/dwowif8f2yq-reader-20261020`; independent editorial/privacy review passed; exact head pending. | Issue 46: INGESTED, ANALYZED, TESTED; not published. Issue 45 artwork gate is separate. |
| [Cloud Codes, `AKovdUFvThA`](https://www.youtube.com/watch?v=AKovdUFvThA) | Private source qualified; [sanitized claim and custody receipt](https://youtube.shareplane.malott.ai/the-grader-is-part-of-the-harness/receipt.json). | Head `c89a3d4ab560bc12c5e2fda9a519f7cf33453fb5`; independent public-copy and privacy review passed. | [PR 42](https://github.com/pinklon/ghostmesh-readers/pull/42) merged; [The Grader Is Part of the Harness](https://youtube.shareplane.malott.ai/the-grader-is-part-of-the-harness/) live. |
| [16-Bit Business, `DP9YPiWL_zM`](https://www.youtube.com/watch?v=DP9YPiWL_zM) | Private source qualified; [sanitized claim and custody receipt](https://youtube.shareplane.malott.ai/the-stop-button-is-outside-the-chat/receipt.json). | Head `20b446627931dcfc9bbb2942cedac3d7d06a2435`; independent public-copy and privacy review passed. | [PR 43](https://github.com/pinklon/ghostmesh-readers/pull/43) merged at `8b3a6a8f0853848e3105d9e75c09a2896edbb2e4`; [The Stop Button Is Outside the Chat](https://youtube.shareplane.malott.ai/the-stop-button-is-outside-the-chat/) live. |

Muse, Bostrom, California, Gates, and Robinson are published through PRs 36–40. Historical draft PRs 31–34 retain their VIDEO-FIRST holds; their previews are not release candidates.

## One bounded release

1. Qualify the exact source in private custody. Preserve video identity, original timestamps and native aspect. If transcript, audio or frames are incomplete, narrow public claims and name the limit. Keep source files outside this Git history.
2. Author the canonical three-part brief, recommendation, dated claim register, counterevidence and sanitized receipt in `content/`. Review every existing Reader for substantively supported typed graph routes; record rationale for links or none. Run `python3 scripts/generate_site.py` and `python3 scripts/knowledge_contract.py` once from the final inputs. Batch all generated public files into the same local commit and use the repository's normal authenticated Git push. Do not loop over individual Git-tree uploads.
3. Run `python3 scripts/generate_site.py --check`, `python3 scripts/knowledge_contract.py --check`, `python3 scripts/check_site.py`, the full Python tests and `git diff --check`. Check desktop/mobile, opt-in playback, source timestamps, link targets and the public/private boundary. Obtain independent editorial and privacy review of the exact article and receipt. If only generated projections or review metadata change, confirm the reviewed article bytes and claims are unchanged; do not commission a ceremonial second editorial review.
4. Push the exact local commit to its named public review branch once authorized. Verify the remote ref equals that commit. Open one draft PR. Use the normal GitHub checks and Netlify deploy preview; inspect the exact head, page, catalog, map, sitemap and source privacy. A green preview is a review surface, not production proof.
5. Merge only the owner-authorized exact head after review, CI, preview and normal repository protections pass. If the head or base changed materially, reconcile before merging. Verify `main` and the Netlify production page, original player and timestamps, content, source links, receipt, catalog count, map edges, sitemap and private-source exclusion. Record the PR, reviewed head, merge SHA, tests and complete live URLs in the final receipt.

## Denied or uncertain operations

If a push, PR, merge or deploy is denied, stop that operation. Report its exact target, checker reason, known execution state and unaffected completed work. Seek a decision for that specific operation through the normal approval path; do not change credentials, permissions, routes or service settings, and do not repackage the same write through a connector. When materially new authorization arrives, check the remote state first and attempt only the denied operation once. If a write times out or disconnects, read back the remote ref or object before deciding whether any retry is appropriate. Do not treat an absent status message as proof of failure.

This runbook does not authorize any new Reader, merge, deployment, private-source disclosure, ReasonPack operation or historical PR 31–34 promotion. Unrelated PR 27 provenance work is not a prerequisite for a source-qualified Reader.
