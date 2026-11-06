# StateBench Scout essay: Creative Lock

Status: **PUBLIC COPY AND TWO VISIBLE RELATIONSHIPS APPROVED FOR DRAFT IMPLEMENTATION** by Tony on November 6, 2026. No exact-head merge or Production release authorization.

## Authority and identity

- Owner, editorial acceptance and UAT: Tony Malott. Co-development: Tony and segfault. Mechanical implementation only after this lock.
- Repository: `pinklon/ghostmesh-readers`, base `main`; branch `segfault/scout-statebench-state-authority-20261106`.
- Lane: Scout original research essay, not `routine-source-report-v1`.
- Title: **The Context Is There. The State Is Wrong.**
- Subtitle: *What StateBench reveals about memory, long-running agents, and the difference between remembering a fact and knowing what is true now.*
- Slug: `the-context-is-there-the-state-is-wrong`.
- Canonical target: `/scout/essays/the-context-is-there-the-state-is-wrong/`.
- Source: `content/scout/publication-drafts/the-context-is-there-the-state-is-wrong.md`.
- Approved source SHA-256: `b87ad242b939ef913d54d9e5ea8c957c8cfbc2f909b66fc55b09fa33bd0fe198`.
- Audience: agent architects, AI evaluation researchers, long-running automation and governance operators.

## Meaning and evidence

- Thesis: retrieval of retained history does not establish that an agent has reconstructed current state or its authority. History, current state, authorization, evidence and continuity are distinct.
- Approved copy: every word of the SHA-pinned Markdown above, including headings, source links, hypothetical release example, strongest objection, test proposal and evidence boundary. No compression, paraphrase, reordered sections or new empirical claims.
- Source roles: Petty, Merrill and Sabharwal, arXiv:2611.03094v1 (November 2, 2026), primary research report; Allen Institute for AI November 3 explanatory article and `allenai/state-bench` repository, author-affiliated context and implementation, not independent corroboration.
- Claim boundary: researchers' synthetic benchmark results are attributed, not independently reproduced. GhostMesh release example is illustrative, not a measured incident. Proposed GhostMesh test is unexecuted.
- Public safe: no private task records, employer information, credentials, test fixture exports, internal approvals or unapproved unpublished work.
- Required disclaimer: the Markdown's final `Evidence boundary` paragraph must remain verbatim.

## Design and relationships

- Reuse the incumbent Scout original-essay wrapper, with `the-approval-must-survive-the-summary` as comparable precedent. No new media or visual prompts; existing typography, responsiveness, light/dark rules, navigation and footer.
- Proposed page: `site/scout/essays/the-context-is-there-the-state-is-wrong/index.html`.
- Canonical research entry: `essay:the-context-is-there-the-state-is-wrong`; topics `agent-memory`, `state-tracking`, `authority`.
- Accepted Scout graph edge: `essay:the-approval-must-survive-the-summary`, type **architectural extension**, with exactly the visible rationale in the locked Markdown.
- Accepted support-page related reading: `/scout/method/`, type **methodological relationship**, visible in `Follow the Thinking`; this method page is not a standalone Scout research graph record, so do not invent a graph node or related ID.
- No `dependsOn`, `supports`, pattern relationships or external independent corroboration claims beyond these.
- Relationship disposition: `RELATIONSHIPS_ACCEPTED` for the exact two visible links; only the canonical essay ID goes into `relatedIds`.

## Implementation and validation

- Add source and lock, render approved Markdown into the existing essay shell and add one matching curated essay card.
- Add one canonical research record and one explicit first-release event only for the actual publication date; if publication slips, update date and repeat review before merge.
- Regenerate Scout Library, landing, relations projection, sitemap and feed through `scripts/generate_site.py`. Preserve old URLs and all prior event history.
- Run generator, generator `--check`, `scripts/check_site.py`, full unittest discovery, `git diff --check`, and the current focused Scout publication/relationship tests.
- Check source SHA, exact page text, graph edge, method link, Library card, curated card, canonical and sitemap, one RSS event, no private exports.
- Perform Netlify preview and desktop/mobile content, links, overflow, keyboard, theme and console checks. Tony owns final semantic and visual UAT.
- PR stays draft, unmerged, automerge disabled. Exact-head Tony approval required for merge. Production HTTP and feed verification after merge, with repository revert/Netlify rollback if necessary.

Codex prompt needed: none. segfault performs mechanical staging against this lock.
