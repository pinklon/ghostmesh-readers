# Scout / SpecEvo-inspired exploration pilot

Status: offline synthetic mechanism test, not an implementation or reproduction of SpecEvo. PR #65 research only.

Design: 12 deterministic one-dimensional target-search tasks, 12 seeded repetitions per task, 12 evaluation calls per trial, three proposal policies. In total, each policy made 1,728 evaluations.

| Policy | Mean best reward | Exact matches | Duplicate attempts |
|---|---:|---:|---:|
| Random exploration | 0.964286 | 20/144 | 132 |
| Success-only local exploitation | 0.891314 | 40/144 | 513 |
| Failure-aware non-repeating proposals | 0.956680 | 75/144 | 0 |

Interpretation: The failure-aware strategy found exact targets more frequently and avoided duplicated evaluations. Random exploration achieved a higher mean best reward. The strategies differ in proposal policy as well as retained history, so these findings **do not isolate the causal value of failure memory**.

The test uses a simple synthetic reward landscape, not LLM discovery or scientific claims. There is no large-model navigator, persistent worker, or real agent coordination. Results do not validate the reported SpecEvo benchmark.

Source-first inspiration: https://arxiv.org/abs/2610.28706v1

Decision: RETAIN INVESTIGATE as an editorial draft, with independent review outstanding. Next experiment should hold the proposal rule constant and ablate only failure-memory use, then test richer landscapes and equal accounting of guidance overhead. No production adoption or external outreach authorized.
