# Scout stop / escalation replay | Measured toy utility

Status: draft research, not a deployable decision policy.

Source replay: `/tmp/scout-trial-34Lfv9/scout-stepwise-replay-v0.json`.
Output: `/tmp/scout-trial-34Lfv9/scout-stop-escalation-v0.json`.

The stop heuristic sees only the observed prefix. It stops on a witnessed exact target, or after at least five evaluations when the recent best score is stagnant and at least 0.985. If the search has used at least nine evaluations while best reward remains below 0.90, it **requests a non-executable escalation review**, and otherwise continues.

A completed counterfactual trajectory provides the **hindsight comparison**, not advance information for a decision.

## Pilot totals

Across 1,152 source trajectories (576 synthetic pairs), 375 strategies stopped before exhausting their original traces; none missed an improvement under this specific conservative rule and toy task generator. There were 339 non-executed escalation review requests.

| Noise | Baseline early stops / 144 | Adaptive early stops / 144 | Baseline mean saved cost | Adaptive mean saved cost | Adaptive escalation reviews |
|---|---:|---:|---:|---:|---:|
| 0% | 30 | 105 | 0.003839 | 0.011557 | 0 |
| 10% | 30 | 73 | 0.003839 | 0.009450 | 32 |
| 30% | 30 | 44 | 0.003839 | 0.006534 | 60 |
| 50% | 30 | 33 | 0.003839 | 0.004231 | 87 |

Saved costs use *declared toy weights*: evaluator call 0.003, proposal inspected 0.00005, feedback hint 0.001. Not currency, real compute or latency.

## What is and isn't established

**Established for this fixed set only:** prefix-only stop rules can reduce synthetic modeled costs without giving up higher rewards found later in these completed traces. The current threshold is conservative and matches the particular toy reward geometry; it is not independently optimized or held-out validated.

**Not established:** effectiveness on ambiguous rewards, uncertain success witnesses, noisy or delayed outcome measures, out-of-sample tasks, real multiagent workflows, or net benefit of stronger-model escalation. Escalation is **review-only**, with no modeled strong-model counterfactual. The utility score makes no claim to capture real GPU costs or operational risk.

## Next step

Use held-out multi-modal reward trajectories and compare several *pre-committed* stopping thresholds, with an explicit false-stop penalty. Separately compare review-only escalation requests with actual bounded offline extra-compute alternatives before considering model dispatch. Do not connect this policy to GhostMesh production execution or credentials.
