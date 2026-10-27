# Reviewing visual claims in Claude PDF answers

Imagine a hypothetical quarterly report. The prose says total sales increased. On the same page, a chart shows three divisions growing and one shrinking. An answer says sales increased across every division, then supplies a citation to the sentence about total sales.

The citation can be accurate as a reference and insufficient for the answer. The cited sentence supports aggregate growth. It does not support the claim about every division. A reviewer who checks that the citation opens the right report, sees the word “increased,” and moves on has verified less than the answer asserts.

The question: does a citation on a PDF answer identify the visual evidence that the claim depends on?

## What the documentation establishes

Anthropic's PDF documentation describes processing that converts pages into images and extracts text, supplying both for analysis. The documented input therefore includes more than the extracted prose. [Anthropic PDF support](https://platform.claude.com/docs/en/build-with-claude/pdf-support)

Its citation documentation describes a narrower boundary: citations support text, not PDF images. It also says scanned PDFs without extractable text are not citable. PDF citation locations use one-indexed page ranges with an exclusive end page. These are details of the citation mechanism, not a finding that Claude cannot read scans or understand charts. [Anthropic citations](https://platform.claude.com/docs/en/build-with-claude/citations)

The inference is limited but useful. An answer can concern visual material while its citation identifies nearby text. That does not establish a failure in any particular answer. It does establish a reason to examine the relationship between the claim and its cited support, rather than treating the presence of a citation as the end of review.

A page reference helps a person find material. It does not, by itself, establish that every visual element on that page was cited or checked.

## The strongest objection is also a useful boundary

Nearby prose may independently support exactly the same proposition as a chart. If the report explicitly says all four divisions increased sales, a citation to that sentence can adequately support the bounded claim. The chart need not become a second mandatory checkpoint merely because it exists.

Nor should reviewers assume that a visual claim is wrong because the citation mechanism cannot cite its image. The claim may be correct. The available evidence record may simply leave its basis unresolved.

That distinction matters operationally. A blanket requirement to inspect every figure would add work even where the text is sufficient. A blanket acceptance of every cited sentence would allow the hypothetical aggregate-to-division mistake through. The useful review boundary is the proposition being asserted: its population, period, units, comparison, and qualifiers.

In the opening example, “every division” is the consequential expansion. Remove it and the aggregate claim may be fully supported. Keep it and the reviewer needs evidence at division level. The necessary action is to narrow the sentence or check that evidence before accepting the broader conclusion.

## Start with a review note, not a new pipeline

The smallest proposed intervention is a claim-level record beside the ordinary citation. Keep the claim's wording, its page locator, and a short note about the evidence actually inspected. Use three explicit labels:

- **Text-cited:** the reviewer checked cited text that supports the bounded proposition, including its qualifiers.
- **Visually reviewed:** the reviewer inspected the relevant chart, table, or diagram and recorded what supports or contradicts the claim.
- **Unresolved:** the available check does not establish support for the claim as written.

These are proposed review labels, not descriptions of native Claude features. The first two can both apply. A citation's mere existence does not earn the first label, and a page opened in a viewer does not earn the second.

For the hypothetical report, a useful note might identify “page 4, upper-right division chart” and explain that the fourth division's bar is below its prior-period value. It should record any necessary legend, axis, or period information, rather than just “chart checked.” If the page uses printed numbering different from its PDF position, record enough information to find it again.

The note makes the review inspectable without pretending to be a machine-generated image citation. It also preserves disagreement. If the chart is ambiguous, the reviewer should mark the claim unresolved rather than upgrading uncertainty into approval.

## One small test, not yet performed

A reversible manual test could use one small synthetic PDF with three deliberately bounded claims: one supported only by text, one supported only by a visual, and one independently supported by both. The fixture would contain no private data. Its answer cards would be written for the exercise and clearly labeled as fabricated, not presented as model outputs.

Two reviewers could independently assess the cards first with ordinary text-citation information, then with a page-region locator and a visual-review note. Record their evidence classifications, whether they miss a visual dependency, and the effort each review takes. Keep the original cards unchanged so the exercise can be repeated or discarded without altering a production workflow.

The comparison would be exploratory. Seeing the same cards twice creates a learning effect; three claims cannot establish a general error rate or a performance improvement. Agreement between reviewers is useful to inspect, but agreement alone is not proof that their assessment is correct.

Include the negative case deliberately: the text-only claim should require no additional visual check once its cited text fully supports it. The proposed method should earn its extra work where evidence crosses modalities, not manufacture work everywhere.

If reviewers cannot consistently identify the supporting region, or the added note merely repeats the answer without making support easier to inspect, defer adoption. First clarify the claim and fixture. No model, API, OCR, or citation-output test is part of this exercise; any later model evaluation would require a separately authorized scope.

## The consequence is specific

The possible benefit is a more explicit record of what was checked. It remains hypothetical until tested. There is no basis here for promising better model performance, claiming a security property, or prescribing a multimodal infrastructure project.

For now, keep the citation, identify the exact claim, and record the missing visual check when that claim needs one. In the hypothetical sales report, the practical result is simple: do not approve “every division” on evidence that establishes only the total.

*Evidence note: the two linked living documentation pages were reviewed for this analysis on October 26, 2026. That is an observation date, not a release date. Both belong to the same vendor evidence family; no publication timestamp or immutable revision was established. No model or review experiment was performed.*
