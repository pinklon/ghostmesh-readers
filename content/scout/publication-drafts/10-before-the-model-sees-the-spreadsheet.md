# Before the Model Sees the Spreadsheet

When an XLSX reader reports success, what did it read: literal values, stored formula results, or newly calculated results? That distinction matters before a model sees the document. A conversion can produce orderly, plausible text while leaving the calculation contract unresolved.

At Docling revision `90234a71b16785d08fd2f46ec62668dd2396db76`, XLSX conversion selects `SimplePipeline` and `MsExcelDocumentBackend`. The pipeline delegates native conversion to the backend, which opens the workbook with `ExcelReader(..., data_only=True)`. Its cell scan skips values that are `None`. This is source inspection, not an executed Docling test. [1]

The openpyxl API documents that `data_only` selects between formulas and their stored values. Microsoft's format documentation represents the formula and cached result separately; the cached value can be omitted. Those sources support a limited inference: successful values-only conversion does not establish that every formula had a result available, or that a stored result is current. They do not establish how frequently missing or stale caches occur in real workbooks. [2]

## What was actually observed

A Scout research check read one unchanged public Docling fixture using openpyxl 3.1.5, once in formula mode and once in cached-value mode. Both reads were read-only. In `Duck Observations!D7`, formula mode returned `=B7+C7` and cached-value mode returned `310`. Five other formula cells, D2 through D6, returned cached numbers of 200, 230, 250, 280 and 280. [3]

That observation establishes two representations of the same workbook bytes. It does not establish cache freshness. Docling was not executed, and neither missing-cache nor stale-cache cases were tested. The inspected upstream Docling test expects populated values, including 310, but that test was not run as part of this check. [4]

## Cached values can be the right answer

There is a credible reason to prefer this behavior. Someone searching a workbook for revenue may need the displayed number rather than the expression that produced it. Onyx deliberately chose cached values in PR 13536, merged July 29, 2026, accepting omission of formulas that had never been evaluated. Its inspected implementation uses `data_only=True`. [5]

The inspected Onyx test checks that formula text is absent and the `Total` label remains. It does not itself demonstrate a populated formula cache. That is a limit of this particular test, not a claim about all of Onyx's coverage. The implementation choice remains a useful counterargument: if trusted, recalculated workbooks and values-only retrieval are the intended contract, another adapter may add effort without improving the answer.

The qualification question is therefore specific. Does the reader preserve the distinctions its users need? Structured export cannot restore a formula/result distinction already discarded upstream. A model should not fill an unavailable total and present its inference as a value read from the sheet. Neither point establishes that a larger model, or a more elaborate extraction pipeline, would improve the result.

## The next test

A small reversible comparison would use four disposable workbooks: literal constants, a formula with an independently verified current cache, a formula without a cache, and a formula with a deliberately stale cache. Read identical bytes in formula and cached-value modes, preserving sheet and cell identity, then compare the incumbent reader with any proposed adapter. This four-case experiment has not been performed.

A useful reader should distinguish literal, cached and unavailable results without silently substituting zero. It should preserve ordinary values-only retrieval where that is the intended contract, and should not describe a cached result as freshly calculated without separate evidence. Each result needs the exact fixture, reader revision and failure classification.

Dual-reading can identify formula cells and missing cached values. It cannot independently establish freshness. Recalculation is a separate operation, with its own risks around external links and unsupported functions. If the incumbent already preserves or correctly flags the required distinctions, the experiment should reject the proposed adapter. If the application needs only trusted recalculated values, documenting that narrower contract may be enough.

No performance, cost or quality improvement has been measured. The immediate result is a better-defined input question and a bounded positive observation, not a benchmark of spreadsheet understanding.

## Evidence and provenance

1. **Docling implementation, inspected October 25, 2026.** Pinned revision `90234a71b16785d08fd2f46ec62668dd2396db76`: [XLSX route](https://github.com/docling-project/docling/blob/90234a71b16785d08fd2f46ec62668dd2396db76/docling/document_converter.py#L157-L166), [native pipeline](https://github.com/docling-project/docling/blob/90234a71b16785d08fd2f46ec62668dd2396db76/docling/pipeline/simple_pipeline.py#L28-L50), [workbook loader](https://github.com/docling-project/docling/blob/90234a71b16785d08fd2f46ec62668dd2396db76/docling/backend/msexcel_backend.py#L499-L513) and [cell scan](https://github.com/docling-project/docling/blob/90234a71b16785d08fd2f46ec62668dd2396db76/docling/backend/msexcel_backend.py#L1291). Static inspection only; not a new release claim.
2. **Primary library and format documentation.** [openpyxl reader API](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html), inspected October 25, 2026, unpinned stable documentation; [Microsoft, Working with formulas](https://learn.microsoft.com/en-us/office/open-xml/spreadsheet/working-with-formulas), updated January 14, 2025. Neither source proves the freshness of a particular cached value.
3. **Executed public fixture observation.** [Pinned upstream workbook](https://github.com/docling-project/docling/blob/90234a71b16785d08fd2f46ec62668dd2396db76/tests/data/xlsx/sources/xlsx_03_chartsheet.xlsx), Git blob `fab687878be961d1ef7c8bf8e7befbcbff9430c3`, SHA-256 `2b40c7e15aebc41f6677b8479e0ae655130f0daf503d20b3068d9179d2559002`. One unchanged fixture, openpyxl 3.1.5, read-only formula and cached-value views; no Docling execution or missing/stale-cache test.
4. **Docling positive test, inspected only.** [Pinned test](https://github.com/docling-project/docling/blob/90234a71b16785d08fd2f46ec62668dd2396db76/tests/test_backend_msexcel.py#L411-L450). Its assertions are not an execution receipt for this research.
5. **Onyx counterevidence.** [PR 13536](https://github.com/onyx-dot-app/onyx/pull/13536), merged July 29, 2026; [loader](https://github.com/onyx-dot-app/onyx/blob/616a4b1a9c75cc07e9645069c672f3e8fb029ca8/backend/onyx/file_processing/extract_file_text.py#L633-L642) and [test](https://github.com/onyx-dot-app/onyx/blob/616a4b1a9c75cc07e9645069c672f3e8fb029ca8/backend/tests/unit/onyx/file_processing/test_xlsx_to_text.py#L31-L45), pinned revision `616a4b1a9c75cc07e9645069c672f3e8fb029ca8`. Inspected implementation and maintainer tradeoff, not independently executed Onyx behavior.
