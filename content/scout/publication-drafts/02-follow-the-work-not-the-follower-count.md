# Follow the Work, Not the Follower Count
**GhostMesh Scout | Proposed methods essay | Editorial draft, 23 October 2026**

*How to create a useful discovery system without pretending that an RSS feed is intelligence, a repository is a credential, or a reviewer is a fact-checking oracle.*

Every monitoring system inherits the blind spots of its input. That fact tends to disappear behind polished interfaces. A dashboard says “12 sources.” What does that mean? Twelve independently investigated works? Twelve editorial institutions? Twelve API calls? Twelve streams that may point to the same underlying announcement?

In Scout's current public-data collector, it means **12 retrieval streams**. Some are feeds from institutions or individuals; two are distinct GitHub repository searches; others draw from research listings, aggregators, or technical discussion platforms. A stream is an acquisition path, not an independent witness. It is important to state this because duplicate coverage is so easy to mistake for corroboration.

Scout's research method is built around the unglamorous task of keeping these categories apart.

## Twelve windows, not the whole world

The pilot samples public material from Simon Willison's feed, Hugging Face, Cloudflare, Lobsters, GitHub Engineering, arXiv's AI and machine-learning categories, Planet Python, public GitHub searches for agent memory and agent authorization, DEV Community's AI tag, and Hacker News.

Each source makes a choice about what becomes visible. Research categories are not random samples of scientific progress. Vendor blogs emphasize work useful to the vendor. Hacker News ranks attention, not truth. GitHub repository searches depend on specific terms and ranking. RSS feeds may syndicate the same article twice.

That is why Scout records the input route, source URL, retrieval time and errors alongside each lead. **Coverage is documented instead of assumed.**

In its small commissioning pilot, Scout fetched 36 leads from all twelve streams during a capped run. That number says the acquisition mechanism worked in that sample. It says nothing about how many valuable ideas existed in the wider ecosystem.

There is an even sharper boundary around authenticated platforms. The present public collector does not secretly ingest an owner's X, Instagram, Reddit, YouTube or Bluesky account. It does not evade login walls or purchase engagement data. Other GhostMesh systems may analyze user-supplied videos; that activity should not be credited to Scout's public-feed coverage.

## The first transformation: a lead

The collection stage normalizes public titles, descriptions, dates and HTTPS links. That is useful work, but the output is called an **unreviewed lead** for a reason.

A title can exaggerate. A description can summarize the wrong paper. A repository can be a wrapper around somebody else's code. Source content can contain adversarial instructions aimed at automated agents. Scout treats these strings as data rather than operational commands.

Normalization also requires restraint. Removing marketing-tracking parameters can make repeated observations easier to recognize, but merging two URLs is not proof that their underlying works are identical. A source that disappears between capped feed snapshots may simply have slipped below the sampling window. A changed title is not proof the study changed. For work with identifiable revisions, a properly pinned source version and, where permitted, captured content hashes enable stronger comparisons. Where those witnesses are absent, the conclusion stays absent.

The categories look fussy until one asks an ordinary question: *What exactly changed since the last time I saw this?* Scout should be able to answer without inventing a history.

## Familiar relevance and unfamiliar possibility

A research system inevitably begins with some vocabulary. Scout currently recognizes topics including authority boundaries, continuity, provenance, evaluation, model infrastructure, interoperability and human–AI collaboration. Keyword matches create an initial reading lane.

Then it creates a second one.

Outside-vocabulary leads are not discarded as noise. A bounded, deterministic selection reserves attention for unmatched URLs across different public-source streams. The mechanism is deliberately less dependent on engagement metrics and rankings. That does not make these leads high quality; it makes them **visible for possible examination**.

The distinction is crucial. If the declared dictionary does not mention a concept, the system is not entitled to decide that concept cannot matter. An outsider lane protects a limited amount of research curiosity without turning the system into a bottomless browsing machine.

## Evidence levels must be legible

The first review question is not “Is this interesting?” It is “What did anyone actually inspect?”

Here is a useful progression:

| Evidence reached | What it permits | What it does not establish |
|---|---|---|
| Feed title or excerpt | A reading question | Source claim validity |
| Original abstract or README | A bounded account of author-stated claims | Technical reproducibility |
| Original paper, implementation or article examined | A reasoned source critique | Independent empirical replication |
| Isolated execution | Observed behavior under stated conditions | General reliability or production suitability |
| Independent comparison against GhostMesh baseline | Evidence of a contextual benefit or deficit | Universal superiority |
| Owner editorial and adoption decision | Authorized next action within its scope | That every underlying research claim is true |

These steps are not all completed for every lead. Their purpose is to stop a UI from turning “we read the abstract” into “we evaluated the method.”

Scout's current ten-panel private workspace deliberately uses labels such as **UNVERIFIED**, **NOT ASSESSED**, and **NOT MEASURED**. Those labels are progress information. They are also guardrails against false confidence.

## What an eventual connection thesis should look like

A useful Scout connection is not “these authors work on agents too.” It is closer to:

> This paper proposes a way of selecting evidence tasks during harness evolution. GhostMesh has an identifiable question about evaluation coverage. We have examined the paper's reported procedure, but not independently reproduced its gains. The smallest discriminating test is to compare the proposed selection method against our existing harness on the same frozen tasks and budget.

That is a testable relationship between an outside idea and an actual local problem. It can be revised when a source changes, when a baseline is measured, or when an experiment fails. It also leaves room for the entirely respectable conclusion **no connection justified**.

The same discipline applies to people. A public GitHub handle is an account attribution. A repeated paper byline is a string that may refer to a namesake. Neither is automatic proof of identity, expertise, affiliation, or consent to outreach.

## Receipts, not ceremony

Scout's private runs include source observations, analysis views and manifests whose saved-file digests can be checked later. Collection failures and limitations are recorded. An earlier run may be replayed against the next snapshot without silently rewriting either.

That infrastructure should remain proportionate to its job. A source-reading assistant should not require an elaborate deployment ritual for every low-risk editorial question. But decisions worth remembering need enough provenance to survive the next enthusiastic model answer.

That is the practical compromise: lightweight acquisition, explicit evidence grades, reproducible snapshots, and human control over any consequential action.

**Scout will be credible not because it finds the most, but because it shows exactly how little or how much was actually established.**

### Source notes
- [Scout methodology and collection-stream disclosure](https://github.com/pinklon/ghostmesh-readers/blob/research/scout-connection-thesis-v0/research/SCOUT-METHODOLOGY.md), October 23, 2026.
- [arXiv AI](https://export.arxiv.org/rss/cs.AI) and [ML](https://export.arxiv.org/rss/cs.LG) listings, two of the documented research inputs.
- [GitHub public repositories](https://github.com/search?q=agent+authorization&type=repositories), an example of topic- and query-limited discovery.
- [Hacker News](https://news.ycombinator.com/) and [Lobsters](https://lobste.rs/), discussion streams with different community selection pressures.

*Not published. No private intake records, person lists, source packets, credentials, archive locations, or account access details included.*
