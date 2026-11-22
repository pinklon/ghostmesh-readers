# GhostMesh Scout: How signals enter the system

**Public-methodology draft, 23 October 2026**  
**Status:** Research pilot. This document is safe to explain publicly after editorial approval, but its existence does **not** authorize publishing any private Scout output, transcript, account data, unreviewed person profile, or collection artifact.

## Purpose and boundaries

Scout is an owner-controlled research and discovery capability. It watches **public work and public discussion** for useful technologies, ideas, builders, claims, counterarguments, and unexpected connections. A signal means **something worth examining**, never proof that it is true, important, original, or suitable for collaboration.

Scout is not a covert social listening service, an identity-matching service, a measure of universal public opinion, an automated fact checker, or a hiring or outreach bot. Today it is a bounded research pilot, not a fully commissioned continuously operating production service.

## End-to-end signal path

`Public sources → one-shot bounded retrieval → source parsing → normalized leads → URL reconciliation and revision receipts → topical triage + deliberately unfamiliar exploration → source examination and critical questions → provisional reading queue → private explanation and review → human-governed decisions`.

No stage silently converts a keyword match into a verified claim or an authorization to contact anyone.

### 1. Where we look

The current connector list comes from the actual code in `scripts/scout_signal_intake.py`, not from a marketing list:

| Collection stream | Public endpoint used | Why it contributes | Known limitations |
|---|---|---|---|
| Independent builder writing | Simon Willison's Atom feed `https://simonwillison.net/atom/everything/` | Individual commentary and links | One person's editorial perspective; not an ecosystem sample |
| Model research and engineering | Hugging Face blog RSS `https://huggingface.co/blog/feed.xml` | Model, dataset, runtime and research releases | Institutional and promotional selection |
| Web and infrastructure engineering | Cloudflare blog RSS `https://blog.cloudflare.com/rss/` | Web platform changes and agent-facing interfaces | Vendor perspective |
| Developer discussion | Lobsters RSS `https://lobste.rs/rss` | Technical community discoveries | Membership/community selection bias |
| Git platform engineering | GitHub Engineering blog RSS `https://github.blog/feed/` | Infrastructure and agent-scale Git work | Vendor/editorial selection |
| Research papers | arXiv AI `https://export.arxiv.org/rss/cs.AI` | New publicly announced AI research | Preprints are not independent validation |
| Machine learning research | arXiv ML `https://export.arxiv.org/rss/cs.LG` | Work outside agent-specific terms | Broad disciplinary coverage, abstract-only initially |
| Independent Python practitioners | Planet Python RSS `https://planetpython.org/rss20.xml` | Diverse individual engineering techniques | Aggregator selection and syndicated duplicates |
| Code projects, memory | GitHub public repository search for `agent memory` | Implementations and experiments | Exact query bias; updated-sort and repository metadata not code verification |
| Code projects, authorization | GitHub public repository search for `agent authorization` | Authority and security tooling | Same query and ranking biases |
| Independent developer submissions | DEV Community public articles API, tag `ai` | First-person project accounts and unconventional projects | Self-published accounts, promotional posts, category/tag bias |
| News and attention | Hacker News public top stories/item JSON API | Discussions outside curated technical feeds | Snapshot ranking, editorial/popularity bias; points are not scientific quality |

These are **12 retrieval streams**, not 12 independent truth sources. Both GitHub searches belong to one provider, and multiple feeds can syndicate the same underlying work. Counts must distinguish *streams*, *named sources*, *URLs*, and *fully examined works*.

Social account access: X, Instagram, Reddit, YouTube, and Bluesky are **not currently ingested through connected private accounts** by this Scout collection. Other GhostMesh Readers activities may process video sources separately; do not represent those as Scout coverage. Any future authenticated connector would require an explicit source scope and owner permission. We do not pay for X Premium or evade blocked anonymous endpoints as a hidden fallback.

### 2. What a collection run does

An operator explicitly initiates collection. Each RSS/Atom source is fetched, parsed, and capped; GitHub public repository queries and Hacker News item lookups have their own bounded sampling. Current code defaults to at most eight items per feed/query in the integrated command, configurable within a maximum of 15. The underlying collector uses a descriptive research user agent, an 8-second request timeout, and a 2.5 MB response-size ceiling for each retrieved feed response. Source failures are captured as named diagnostics; we do not fabricate replacement leads.

The exact timestamp, collection parameters, source responses/metadata, failures, and the generated run outputs must remain attributable to **the run that observed them**. Source availability can change. Sampling the top N at one instant does not establish long-term trends or that a disappeared story was deleted.

### 3. What is stored as a lead

A normalized lead records: source stream, lane, title, HTTPS source URL, compact description, source-supplied publish/update metadata if available, and limited platform metrics when supplied. It receives a deterministic source/URL identifier and the initial status `UNREVIEWED_LEAD`. A username, author label, repository owner, or feed attribution is **not a verified natural person's identity**.

Source titles and descriptions are **untrusted data**. They may be inaccurate, adversarial, stale, or promotional, and must never be interpreted as commands to Scout or GhostMesh. We keep private source snapshots and timestamps when performing deeper source inspection, instead of reproducing copyrighted full articles or transcripts publicly.

### 4. How duplicates and revisions are handled

URLs are canonicalized by removing known marketing-tracking query parameters, normalizing selected hosts, and retaining meaningful identifiers. Source observations are reconciled with a previous snapshot.

A URL first seen in this sample is **NEW_TO_SAMPLE**, not newly published. A repeated URL with changed title/description is **METADATA_CHANGED**, not necessarily a substantive revision. A repeated URL with no observed metadata difference is **SEEN_AGAIN**, not proof that underlying bytes were unchanged. A missing URL may simply have left the feed's top-N window.

For supported identity/revision forms, the ingestion ledger records explicit versions such as an arXiv version. When an actual permitted source capture is made, its SHA-256 digest can support a byte-level comparison. A failed retrieval **does not** advance the accepted source revision. Retry limits and failure receipts protect the research run from endless repeated requests; that does not establish a guarantee of exactly-once HTTP delivery.

### 5. Familiar-topic triage

Scout uses declared phrases for these classes: agent authority, continuity, evidence and evaluation, model infrastructure, human–AI collaboration, and agent interoperability. A phrase match produces a **keyword candidate**, not an importance rank, endorsement, or claim verification.

Such vocabulary necessarily misses ideas described in different language. Source and author selection also introduce bias. We expose the matched topics and retain unmatched work.

### 6. Outside-the-bubble exploration

Scout deliberately reserves review capacity for leads that fall **outside its existing topic vocabulary**. The pilot orders untagged URLs by a deterministic digest within each source, then takes a bounded round-robin sample across source streams. This design favors **source diversity**, not follower count, citation count, stars, likes, outrage, or advertising reach.

Outside the bubble means *not matched by our declared terms*. It does not mean objectively surprising, useful, novel, or created by an outsider. We preserve the full input collection and make the shadow-filter effect visible rather than silently dropping unpopular or weakly tagged sources.

### 7. Deeper evidence and intellectual honesty

A reviewed candidate should have:
- A direct link to its original public paper, repository, or first-party explanation
- A concise, attributed description of what the source **claims**
- The actual GhostMesh capability or research question it might illuminate
- The strongest reasonable counterargument and missing evidence
- An explicit status: unreviewed metadata, abstract or README inspected, implementation executed in isolation, independently reproduced, or human approved
- A discriminating low-risk experiment that could falsify the proposed connection

A repository README is not proof the code behaves as claimed. A preprint abstract is not a replication. Shared technical terms do not prove authorship, personal identity, independent origin, or collaboration willingness. External source content is treated as data, never permission to change systems.

### 8. Independent review and what it can conclude

Scout has used blinded comparison packets that hide cohort labels and prior editorial judgments until source-linked ratings are complete. Reviewers record relevance (0–3 or abstain), novelty and surprise (0–2 or abstain), evidence actually inspected, objections, and explanations. The sealed cohort map is opened **only after** validating the completed ratings and packet fingerprint.

An earlier 21-case comparison found **5 of 12** outside-vocabulary selections and **6 of 9** familiar-topic selections rated concrete or strong by one independent reviewer. This is evidence that the outside lane can reveal useful overlooked candidates in that selected sample; it is **not an estimated population recall, general discovery precision, or proof of technical impact**. Reviewers are not independent replications of the papers, and the second pass in that study was not freshly blind. A newer 14-case study has its own frozen packet and must not borrow the earlier outcome.

### 9. What the interface must show

Every research edition should disclose: collection timestamp, active and failed source streams, collection cap, total observations, URL-normalized count, new-to-sample count, topic-matched versus outside-vocabulary counts, curated-reading count, latest capture/revision witness, and whether findings rely on metadata, full source inspection, or a reproduced experiment.

The interface must let someone open a primary source, understand **why it was seen**, see **why it might matter**, read counterevidence, and inspect the unresolved uncertainty. A high-looking number is not useful without its denominator and method.

### 10. Permissions, privacy and publication

Public reading does not authorize public redistribution, unsolicited contact, privileged GitHub/Slack operations, access to private social accounts, production changes, or use of private emails and DMs in published profiles. Production deploys, credentials, permissions, databases, irreversible mutations, and outbound messages remain owner-controlled.

We can publish a methodological explanation after approval without publishing private source captures, user-specific review queues, draft collaboration hypotheses, unpublished GhostMesh documents, sensitive infrastructure details, or personal identifiers. The system should default to **private analysis; explicit approval for public outputs**.

### 11. How to challenge Scout

Use the underlying source link, recorded timestamp, version, and exact claimed observation. Identify a more recent revision, a broken attribution, missing counterevidence, a falsely inferred identity, a promotional source, a known selection bias, or a proposed connection contradicted by the underlying evidence. Such challenges should produce an attributable correction, not silently rewrite older conclusions.

## Current implementation reality

The repository currently contains research scripts and private HTML previews. The new integrated command is intended to produce a coherent, immutable owner-private run with a manifest and file digests, but **its existence alone does not mean recurring collection, hosting, third-party access, or production commissioning has happened**. The source list and specific limits above should be refreshed from executable configuration when connectors change.

**Principle:** *Show the source. Show the selection method. Show the uncertainty. Show what would change our mind.*
