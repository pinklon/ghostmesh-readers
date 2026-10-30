# Validate the Association, Not Just the Extracted Value

*A parser can preserve a number and its bounding box while assigning it to the wrong column. The useful validation boundary is the relationship between the value, its source region, and its header.*

A table extraction can preserve every digit and still change the answer. The number is present. Its bounding box points somewhere plausible. The document loads successfully. But the number now belongs to a different year.

That distinction matters before a language model enters the workflow. Text recognition, source location, and table membership are separate claims. Checking one does not automatically check the others.

Docling makes the separation inspectable. Its provenance object carries a page number, bounding box, and character span. A table cell separately carries text, optional geometry, row and column offsets, spans, and header flags. These are useful representations, but they answer different questions: where did the content come from, and where does the extracted structure place it? [Provenance model](https://github.com/docling-project/docling-core/blob/2dc4c9f511269eb39be5aad84b838f7bb179142e/docling_core/types/doc/common/reference.py#L205-L217), [table model](https://github.com/docling-project/docling-core/blob/2dc4c9f511269eb39be5aad84b838f7bb179142e/docling_core/types/doc/items/table/table_data.py#L21-L165).

## The grid follows the offsets

The consequential detail is in `TableData.grid`. It creates an empty grid, then places supplied cells into positions determined by their logical offsets. It does not consult their bounding boxes. If supplied cells cover the same position, a later assignment replaces the earlier one at that position. This is implementation behavior, not evidence that ordinary conversions frequently produce overlaps. [Grid implementation](https://github.com/docling-project/docling-core/blob/2dc4c9f511269eb39be5aad84b838f7bb179142e/docling_core/types/doc/items/table/table_data.py#L126-L165).

The resulting inference is narrower and more useful: preserving text and geometry cannot, by itself, establish that logical membership stayed correct. An adapter could change offsets without changing either. The structured output would still contain the original number and its original address.

This is not merely a hypothetical class of extraction difficulty. Docling's own options guide describes erroneously merged columns and offers an alternative to matching recognized structure back onto PDF cells. That documents an association failure category; it does not establish its frequency or make disabling matching the right default. [Table extraction options](https://github.com/docling-project/docling/blob/7b12671e1d324710e70784c18844d1d97522414f/docs/usage/advanced_options.md#L189-L213).

## A second extraction is not automatically a check

A simpler tool does not remove the need to define the check. PyMuPDF documents that supplying a cached `TextPage` causes the `clip` and `flags` arguments of `get_text` to be ignored. The ordinary text extraction implementation reuses that page rather than building a newly clipped one. A check intended to ask whether a value exists inside one cell can therefore accidentally ask whether it exists anywhere on the cached page. Repeated values make that distinction especially important. [Extraction contract](https://github.com/pymupdf/PyMuPDF/blob/d2423b1367bcc9721ea7e994e710e5bc7ea91b09/docs/page.rst), [implementation](https://github.com/pymupdf/PyMuPDF/blob/d2423b1367bcc9721ea7e994e710e5bc7ea91b09/src/utils.py#L453-L565).

Coordinates need a contract too. PyMuPDF generally returns unrotated page coordinates, while its page rectangle reflects rotation. A bounding box is usable only with the page identity and transformation conventions that give those numbers meaning. [Page coordinate documentation](https://github.com/pymupdf/PyMuPDF/blob/d2423b1367bcc9721ea7e994e710e5bc7ea91b09/docs/page.rst).

These are adapter constraints, not arguments against either library. They explain why a second extraction must be tested as a measurement procedure rather than treated as an independent oracle.

## Give each check its own result

A practical contract can distinguish three outcomes:

- **Address checked:** the source identity, page, coordinate convention, and transformation resolve to the intended region.
- **Value checked:** the literal content agrees under an explicit normalization policy, without silently changing signs, units, or decimal separators.
- **Association checked:** the value belongs to the expected row and header chain, accounting for spans and orientation.

Missing geometry should produce an unavailable check, not invented precision. Docling permits empty item provenance and optional cell boxes. Its confidence documentation also identifies table scoring as not yet implemented in the inspected revision. Overall conversion grades should not be silently promoted into probabilities that a particular header/value relationship is correct. [Item provenance](https://github.com/docling-project/docling-core/blob/2dc4c9f511269eb39be5aad84b838f7bb179142e/docling_core/types/doc/items/node.py#L119-L132), [confidence documentation](https://github.com/docling-project/docling/blob/7b12671e1d324710e70784c18844d1d97522414f/docs/concepts/confidence_scores.md).

## Test the distinction before building a framework

Start with one synthetic two-by-two data table, plus row labels and two year headers. Give its four values known source regions and expected header associations. Include a repeated value so text presence alone cannot identify its owner.

Keep the source immutable. In disposable serialized-output copies, swap two logical column offsets while preserving text and boxes; separately introduce overlapping offsets and remove one box. The proposed validator should flag changed ownership, ambiguous occupancy, and unavailable provenance rather than treating them all as successful extraction.

Also compare coordinates before and after loading the serialized document. The inspected Docling validator invokes page-bound clamping; that is a reason to measure changes, not to assume every roundtrip changes geometry. Preserve the raw input alongside the loaded representation. [Validation and clamping](https://github.com/docling-project/docling-core/blob/2dc4c9f511269eb39be5aad84b838f7bb179142e/docling_core/types/doc/document.py#L219-L343), [validation call](https://github.com/docling-project/docling-core/blob/2dc4c9f511269eb39be5aad84b838f7bb179142e/docling_core/types/doc/document.py#L5647-L5660).

This is a test design, not a reported experiment. Its purpose is to discover what the checks cannot see, not to rank parsers.

## The objection is cost

For clean, stable templates, existing structure and coordinates may already be sufficient. Rechecking every cell can add latency, conflicting outputs, and maintenance burden without changing a decision.

The answer is not universal re-extraction. Apply cheap structural checks first, then reserve source-region and association checks for consequential fields, ambiguous layouts, and parser or adapter upgrades. Keep confidence as useful metadata. Keep source agreement distinct from truth. Most importantly, do not let a correctly extracted number stand in for a correctly extracted relationship.
