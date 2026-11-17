## A parser fix is not the whole association path

*Source update: November 16, 2026 Pacific; upstream state checked November 17 UTC.*

A document-reading upgrade can repair one stage while leaving the decision downstream untested. Docling-parse 7.26.0, released November 13, includes a change to keep text grouping from crossing relevant clipping boundaries. The motivating public report shows an item code joining text from the next column. This is upstream report and implementation evidence, not a parser result reproduced for this article. [Release](https://github.com/docling-project/docling-parse/releases/tag/v7.26.0), [merged change](https://github.com/docling-project/docling-parse/pull/443), [public example](https://github.com/docling-project/docling-parse/issues/404).

At this source check, the companion core-model field proposal and the table consumer proposal were still open. The parser change therefore cannot establish that a particular installed parser, core model and table consumer preserve the correct header/value relationship together. Nor does an open proposal prove that every existing combination fails. [Core proposal](https://github.com/docling-project/docling-core/pull/964), [consumer proposal](https://github.com/docling-project/docling/pull/4786).

The GhostMesh consequence is to name the boundary an upgrade actually changes. Text retention, word grouping, source geometry and logical cell ownership are separate checks. A grouping correction can be useful without proving ownership; retaining every character does not prove either one. Pin the parser, model and consumer together before interpreting the result.

For a bounded qualification, use the public clipped-table example alongside an unclipped control and compare grouping separately from final row/header assignments. Report unavailable geometry as unavailable. That end-to-end comparison has not been performed here; no installed version, speedup, accuracy gain or corrected final association is claimed. The original source analysis and proposed fixture below remain unchanged.
