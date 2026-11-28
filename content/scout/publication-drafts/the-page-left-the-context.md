# The Page Left the Context

Retrieve three page images on every search. After nine searches, there are 27 images to keep. A harness with room for 24 has to let something go.

In the released DR Pixel harness, the oldest images go first. The search record remains. A metric can correctly report that the agent retrieved the relevant page even after the original page image has left its working context.

For GhostMesh, that is a reason to record both events. Evidence acquired and evidence available at the decision are separate facts. A useful reading system can compress, extract, discard and retrieve again. Its account of the evidence should survive those choices.

## What the code actually counts

DR Pixel, introduced in a [November 2 preprint](https://arxiv.org/html/2611.03097v1), retrieves rendered document pages and supplies them directly to a vision-language model. The page stays together: text, table, figure and surrounding explanation. That is an attractive alternative to asking the model to reconstruct those relationships from separately retrieved fragments.

The public implementation also has to manage a finite context. At [revision 14a3a82](https://github.com/StarTrail-org/DRPixel/blob/14a3a82f5c5266c6c87565a19184d1e16adfb531/eval/drbench/harness.py#L209-L256), it keeps at most 24 images. Older images are replaced with short text notices. A separate token-budget estimate can remove images earlier. Surrounding text and any facts already written into the conversation can remain.

Its page-hit metric answers a different question. The [metric implementation](https://github.com/StarTrail-org/DRPixel/blob/14a3a82f5c5266c6c87565a19184d1e16adfb531/eval/drbench/judge.py#L157-L184) checks whether any recorded search returned the gold document and page number. It does not inspect the final working context.

An [offline reproducer](./retention-probe.py) using the exact helper functions makes this visible. It checks the source hashes, extracts `_img_count`, `_drop_oldest_images` and `retrieval_hits`, then feeds in nine searches with three synthetic image markers each, placing the gold page first. After applying the image cap, 24 markers remain, the first image is gone, and the historical page hit remains true.

That check used no model, image decoder or retrieval service. It establishes the accounting behavior. It says nothing about whether a model would answer correctly.

There is a source boundary worth making explicit. The paper says observations remain in context; the release documentation describes a 24-image limit and says it applied to reported runs. Those descriptions are in tension. The released code establishes eviction behavior, but this check does not establish which original paper trajectories lost relevant images.

The receipt is doing its job. We need to be careful about the job we assign it.

## The objection is fair

PgHit is a retrieval metric. It never promised to measure retention.

Eviction may also be the right choice. A model can read a table, extract the relevant value and its source, then continue without carrying the entire image through every later turn. Requiring every page to remain visible would spend context and money to avoid making a more useful decision about what to preserve.

The concern appears when a historical hit becomes shorthand for a stronger claim: the evidence was available when the answer was produced, or the model had everything it needed and simply failed to read it.

The repository also reports [accuracy conditioned on retrieving the gold page](https://github.com/StarTrail-org/DRPixel/blob/14a3a82f5c5266c6c87565a19184d1e16adfb531/eval/drbench/judge.py#L208-L238). The paper's [Table 3](https://arxiv.org/html/2611.03097v1#S4.SS2) already distinguishes hits on the last search from earlier hits. That is useful timing analysis. It does not directly measure which images remained available.

If we use conditional accuracy to diagnose reading ability, retention remains a possible contributor. A wrong answer could follow an initial misreading, a poor factual note, or loss of the original image before a later comparison required it. The aggregate does not separate those cases, and this probe does not explain the paper's reported reading gap.

This is a proposed diagnostic distinction, not an accusation that the paper's results are wrong. No model outcomes were reproduced in this analysis.

## What survives should be inspectable

For a document-reading workflow, I would want three questions answered before treating a source-backed conclusion as ready for review:

- Which original page was retrieved, with what document identity and revision?
- At the answer, was that original evidence still available, or was the model relying on an extracted fact?
- If a derived fact replaced the original, what connects it to the source, and what checks made that substitution acceptable?

The second path can be entirely legitimate. A source-linked note may be sufficient for a single value. A claim about table alignment, footnotes or the relationship between a chart and its caption may need the page again. That choice belongs in the reading policy and its tests.

Keeping a page ID beside an extracted number helps preserve provenance. It does not, by itself, prove the number was copied correctly or remained attached to the right row.

The practical failure to avoid is quieter: a historical retrieval flag satisfying an acceptance rule that was intended to require reviewable evidence at the decision.

## A small test before a large architecture decision

Start with the bookkeeping test. Make sure the system can distinguish a page that was retrieved, a page that remains in context and a source-linked fact retained after the page was removed.

Then test a small set of public documents with known answers. Place the relevant page early and late in prepared search sequences. Within each ordering, replay identical retrieved pages and the same pre-intervention history in a paired comparison: ordinary eviction versus retaining the relevant page while dropping a distractor. Keep the image count fixed and record both the answer and the evidence available at the answer. Compare retention within each ordering before comparing early and late positions.

Selecting the known gold page makes this an oracle diagnostic intervention. A production system does not get that answer key. The test asks whether retention changes outcomes under controlled replay, not whether the system already knows which page it should preserve.

This is a retention experiment. It should not be presented as a new model ranking or proof that images always beat text.

The [release documentation](https://github.com/StarTrail-org/DRPixel/blob/14a3a82f5c5266c6c87565a19184d1e16adfb531/eval/README.md) supplies further reasons to keep comparisons bounded. The separate figure-search index is not yet released. The public GPT-5.4 adapter uses a different tool protocol from the paper's run. Text chunks lack page numbers, so their page-hit metric is unavailable rather than zero. These are declared reproduction limits, not details to smooth away.

DR Pixel offers a useful way to keep visual evidence together. Its implementation also gives us a concrete place to ask what remains after the system has made room for the next search.

Record the page arriving. Record what replaced it when it left.

