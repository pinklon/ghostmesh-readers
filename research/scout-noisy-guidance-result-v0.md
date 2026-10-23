# Scout noisy-guidance research result

Status: **synthetic, research-only**. Not a reproduction of SpecEvo or validation of a GhostMesh model.

Twelve one-dimensional target tasks, twelve matched seeded trials each, twelve possible evaluator calls per arm, across four levels of deliberately flipped directional hints.

| Wrong-hint rate | No-guidance mean reward | Always-guided mean reward | Guarded mean reward | Exact successes: baseline / always / guarded |
| --- | ---: | ---: | ---: | --- |
| 0% | 0.964176 | 0.999890 | 0.999890 | 32 / 143 / 143 |
| 10% | 0.964176 | 0.929674 | 0.979497 | 32 / 84 / 90 |
| 30% | 0.964176 | 0.824405 | 0.965278 | 32 / 33 / 49 |
| 50% | 0.964176 | 0.761354 | 0.961750 | 32 / 11 / 35 |

Illustrative cost units per trial (evaluation + proposals + hint fee): baseline 12.0262; guarded 12.7043 at 0%, 12.6081 at 10%, 12.6790 at 30%, 12.6734 at 50%. These are **defined toy cost units**, not dollars, GPU seconds or model tokens.

Important controls and limitations:
- All approaches share deterministic task/seed candidate generation and a cap of twelve evaluator calls. Some guidance arms cannot use all twelve because the noisy hints eliminate their search range; unused calls are reported in the JSON receipt.
- Directional hints reveal privileged target information. The baseline does not receive equal information.
- Guarded strategy abandons guidance if the accumulated constraints are contradictory. It cannot detect plausible incorrect hints. Its results depend on the synthetic one-dimensional reward geometry.
- The experiment doesn't establish real LLM critique accuracy, cost savings, SpecEvo validity, author collaboration potential, or production agent safety.

Research implication: a strong guided-exploration capability should **monitor feedback reliability and retain a no-guidance fallback**, with actual information and cost accounting. Next controlled test should use ambiguous or delayed reward landscapes, imperfect critique from independent sources, and explicit stop/escalate criteria. No automated adoption, production merge, deployment, or outreach authorized.
