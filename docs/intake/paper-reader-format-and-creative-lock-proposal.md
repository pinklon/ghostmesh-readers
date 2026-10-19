# Paper Reader format and Creative Lock proposal

**Decision stage:** Tony authorized a distinct paper Reader draft and reviewed preview under Readers Issue #23; final editorial copy, route, source contract and production release are still pending. The existing video-first manifest and generator require a `source` with `platform` and `mediaAspect`, video controls, and a brief written for a video. No paper-source identity, publication route or paper template exists on frozen PR27 base `c7025444cad2f10253556be3cbc77bc82ccc50b9`. This isolated branch currently changes only paper source input, source-only checks and research records; it does not admit the article to the catalog or generated site.

## Smallest source-only contract change

1. Add a discriminated source kind in a future versioned catalog schema. Existing video records keep their current shape and paths. A paper record requires a pinned bibliographic identity (`arxiv:2607.27191v2` or DOI plus version), author/publisher, source URL, publication and version dates, and a source-route choice. It does not accept `mediaAspect`, video ID, playback timestamps, or a fabricated player. Direct paper and PDF links can replace opt-in media controls after review.
2. Keep the shared Reader shell and near-top orientation, adapted explicitly to the source type: what the paper studied, why the reader should care or skip, and GhostMesh's bounded takeaway. Preserve visible recommendation, claim status, date-stamped corroboration and counterevidence, uncertainty, sanitized receipt, related-thinking disposition, theme controls, keyboard access and responsive layout. Do not create a graph edge from topical similarity.
3. For each material claim, bind a stable claim ID to a pinned version and human-readable paper section or page, reference role, checked date, and epistemic status. An extraction hash and source-map anchor prove byte custody and location only. They do not confer factual verification. Distinguish study-author reports, separately published context, and independent reproduction. Retain source-specific extraction limits and the current public/private boundary; no full PDF, extracted text, logs, or unpublished TabPFN artifacts enter Git or Netlify.
4. Use a deterministic paper-specific generator and checker only after the contract is approved. Reject video-only fields in paper records and paper-only fields in video records; preserve every existing permalink and index. A paper record may enter the public knowledge projection only under its separately reviewed identity/admission rules. Do not infer a SharePlane/Atlas graph admission.

## Draft choices and remaining Creative Lock

| Field | Candidate for review | Current authority |
| --- | --- | --- |
| Artifact lane and slug | Paper Reader; candidate `/the-experiment-ran-did-the-research-advance/` matching existing Reader permalinks | Distinct paper format authorized for draft and preview; final route needs preview/editorial acceptance. |
| Source identity | Kirgis et al., arXiv:2607.27191v2, with version-pinned HTML/PDF links | Pinned source; Aug 7 arXiv revision and Aug 24 HTML title-block date must remain distinct. |
| Editorial thesis | “The experiment ran. Did the research advance?” | Original bounded public draft at `content/readers/the-experiment-ran-did-the-research-advance.html`; not locked final copy. |
| Audience and recommendation | Autonomous research evaluators; provisional “Worth studying” for the method and limits | Working classification, not owner-approved verdict. |
| Public claim ledger | P1–P6 in the companion source qualification | Source-read and bounded, not independently replicated; final assertion wording and prominence unapproved. |
| Public-safe boundary | Original analysis and bounded citations; no private full source or derived extraction | Proposed constraint consistent with Issue #23. |
| Design and related items | Reuse shared shell; paper citation affordance, no player; no new related edge until curated | Tony authorized source-appropriate presentation; exact preview and relationship decisions remain open. |
| Acceptance | Source review, editorial acceptance, old URL/privacy check, desktop/390px, light/dark, no-JS, keyboard, exact-head CI and hosted preview | Criteria proposal; no implementation or preview yet. |

## Qualified sequence to a preview

The sole paper writer prepares the source article and source checks in an isolated checkout, then integrates a narrow variant from the reviewed PR29 design head after its writer freezes and pushes it. Synthetic paper fixtures and the real article must pass generator, schema, site and knowledge checks. An independent reviewer checks source entailment, qualifiers, privacy and schema behavior at the exact successor head. A draft PR and hosted preview may follow only after those checks, browser review and private-source exclusion pass. The preview is for Tony's editorial and release decision; it is not permission to merge or deploy.

This draft is reversible by dropping its isolated successor branch. The cost of inaction is that the paper cannot be represented honestly in the video-first catalog; the research notes and source-only article remain usable without public admission. No paid service, adapter installation, credential change, provider change, production publish, or modification of combined PR29 is proposed.
