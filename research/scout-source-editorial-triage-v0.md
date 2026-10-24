# Scout live-source editorial triage v0

Status: owner-private research note, **not collector-run evidence**, not independent replication.
Reviewed: 2026-10-22. No publication, outreach, or release permission.

## Source A: multi-agent debate (INVESTIGATE)

Primary: https://arxiv.org/abs/2601.19921v3 (last revised 2026-06-03).
Authors: Xiaochen Zhu, Caiqi Zhang, Yizhou Chi, Tom Stafford, Nigel Collier, Andreas Vlachos.

Observed on primary abstract: the authors claim vanilla multi-agent debate often underperforms majority voting; they propose diversity-aware initialization and confidence-modulated updates, reporting gains across six reasoning QA benchmarks.
Evidence classification: **AUTHOR-REPORTED ABSTRACT**, not independently reproduced.
GhostMesh question: Does independent evidence acquisition improve outcomes more than increasing reviewer count?
Small test: freeze contested cases; compare one evaluator, repeated sampling, independent initial hypotheses, and independent source acquisition at equal cost. Track correctness and correlated error.
Disconfirmation: gains might disappear when baseline strength, token budget, and task selection are matched.
Recommendation: INVESTIGATE research method, not author outreach.

## Source B: collaborative sensemaking (INVESTIGATE)

Primary: https://arxiv.org/abs/2606.09840v1 (submitted 2026-04-23).
Authors: Zhitong Guan and Soo Young Rieh.

Observed on primary abstract: a position paper proposes principles and a conceptual collaborative workspace preserving provenance and authorship while humans and agents negotiate interpretations.
Evidence classification: **CONCEPTUAL PROPOSAL**, not a measured implementation.
GhostMesh question: Do explicit attribution and disagreement records help humans correct agent-synthesized claims without losing original meaning?
Small test: compare two forms of a collaborative review, with/without explicit authorship and source-ancestry fields; score corrections and retrieval of original dissent.
Disconfirmation: added interface and recordkeeping could increase effort without changing decisions.
Recommendation: INVESTIGATE design principles, not author outreach.

## Source C: CPython README (NO_CONNECTION_JUSTIFIED)

Primary: https://raw.githubusercontent.com/python/cpython/main/README.rst (mutable branch; version cannot be claimed pinned).
Observed: build instructions, documentation links and developer guidance for Python.
Evidence classification: **UPSTREAM REPOSITORY DOCUMENTATION**.
Scout relevance: Python is already an implementation substrate; ordinary documentation alone is not evidence of a new complementary research contribution to GhostMesh.
Recommendation: **NO_CONNECTION_JUSTIFIED**. Do not manufacture a joint experiment simply because the source is high quality.

## Verification boundaries

These pages were inspected using a separate public-source reader. They were **not fetched by the Scout collector**. No collector-origin raw bytes, SHA-256 hashes, transfer timestamps, or response headers were captured. The two papers' findings remain claims by their authors. No independent evaluator scored these cases.
Do not publish this note on Readers or use it as social outreach justification.

## Decision

The triage can distinguish two concrete research opportunities from a relevant but noncomplementary negative control. This is one editorial demonstration, not a measured precision or recall result.

Next technical acceptance gate: exact-branch collector must fetch three sources from an isolated network-enabled runner, retain verifiable bytes/hashes and source revision, and show substantive excerpts. Avoid a production cron job or external contact.
