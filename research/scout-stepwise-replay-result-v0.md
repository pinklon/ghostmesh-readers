# Scout stepwise counterfactual replay: evidence receipt

Status: offline research, no production adoption or publication authority.

The new pilot records observations available before each candidate selection, the chosen policy action, the evaluated candidate, observed reward, optional noisy feedback and proposal-search overhead. The synthetic target and wrong-hint oracle are used by the simulated environment only and are not policy inputs.

Each of 12 fixed targets and 12 seeds is replayed at four simulated feedback-error rates, producing **576 matched pairs** and 1,152 policy trajectories. Both arms use the same seeded candidate stream and a maximum of 12 evaluator calls per trajectory.

| Wrong-hint rate | Independent exact/144 | Adaptive exact/144 | Independent mean reward | Adaptive mean reward | Adaptive mean proposals inspected |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0% | 32 | 143 | 0.964176 | 0.999890 | 1624.486 |
| 10% | 32 | 90 | 0.964176 | 0.979497 | 769.312 |
| 30% | 32 | 49 | 0.964176 | 0.965278 | 206.292 |
| 50% | 32 | 35 | 0.964176 | 0.961750 | 94.750 |

Why this matters: the adaptive arm can consume enormous proposal inspection effort filtering its fixed candidate tape against narrow constraints. Comparisons based on evaluator calls alone conceal this overhead. The result is consistent with prior toy experiments, not independent evidence of scientific novelty.

What it does **not** show: real-agent counterfactual evaluation, autonomous stop/escalate optimization, equal-information comparison, robust evaluation of model critiques, or permission to call additional models. The simulator generates both possible policies; we are **not** pretending that a real logged trajectory exposes unobserved counterfactual outcomes.

Trace receipt: `/tmp/scout-trial-34Lfv9/scout-stepwise-replay-v0.json`.
Private six-view workspace: `/tmp/scout-trial-34Lfv9/scout-unified-v5.html`.

Next experiment: inject time-dependent evaluation costs and noisy multi-dimensional feedback; compare stopping and escalation proposals with realized benefit rather than action counts. No production services or outreach touched.
