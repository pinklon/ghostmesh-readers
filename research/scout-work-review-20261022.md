# Scout source-first work review

Status: private editorial draft. Source findings are author claims, not reproduced results. No outreach or release approval.

## SpecEvo | INVESTIGATE

Primary paper: https://arxiv.org/abs/2610.28706v1

The authors propose a speculate-then-consolidate process, preserving success, failure and stagnation evidence while inexpensive models explore and a stronger model intervenes selectively. The paper reports up to 80% API cost reduction on its evaluation suite. This does not establish savings on GhostMesh workloads.

Potential gap: Does our exploration benefit from retaining failed approaches and selective stronger-model intervention? Objection: a program-search evaluator is not an authority-enforcement mechanism, and optimization differs from infrastructure orchestration. Pilot: compare three equal-budget, provider-free search methods on twelve fixed synthetic evaluation tasks, tracking best result, repeated failures and total evaluation cost. Do not touch production agents.

## Structured clinical judgment | FOLLOW

Primary paper: https://arxiv.org/abs/2610.28826v1

The authors compare a structured decision model against large-model judges in clinical evaluation. Their reported lower cost and latency have not been reproduced and are not directly transferable to GhostMesh research reviews. Possible experiment: test abstention and false positives on independently labeled Scout cases before considering an advisory classifier. Do not treat clinical score agreement as proven relevance ranking.

## Relational model pretraining speedrun | FOLLOW

Primary paper: https://arxiv.org/abs/2610.28855v1

The paper describes a fixed-target benchmarking approach and reports a 305.63-second target on H200, 8.11 times faster than its reference implementation. This is relational pretraining, not Hyperion inference. Consider borrowing fixed-quality benchmarking discipline, not adopting its model architecture.

## Limitations

All three assessments are source-derived editorial interpretations. Independent scoring, experimental reproduction, validated contributor identities, and verified collaborator interest are absent. No public page or introductions are authorized.
