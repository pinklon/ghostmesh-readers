# Scout three-way decision pilot | Stop vs continue vs bounded extra work

Status: offline synthetic research; no stronger model was invoked.

Design: four adversarial 20-step synthetic trajectory families, 20 held-out seeds each. At the fixed ten-step checkpoint, compare (1) stop immediately, (2) continue to step 20, (3) perform four additional observed evaluations with a review surcharge of 0.008 cost units, then continue only if their observed best reward improves more than 0.003 versus the checkpoint. The probe is **not** intelligent model escalation or an oracle. Reward observations beyond each decision are not available to that decision.

| Regime | Stop mean utility delta vs continue | Probe mean utility delta vs continue | Stop premature terminals/20 | Probe premature terminals/20 |
| --- | ---: | ---: | ---: | ---: |
| Late breakthrough | -0.099211 | -0.119110 | 20 | 20 |
| False plateau | +0.008640 | -0.011048 | 20 | 20 |
| Steady progress | -0.089656 | -0.008000 | 20 | 0 |
| Flat noise | +0.030262 | +0.010170 | 2 | 1 |

Each action is scored against the *same full pre-generated trajectory*. A probe can fail when its four-step window ends before a delayed improvement, and its review surcharge is counted. In this toy comparison, probe never beats the stronger of simple STOP or CONTINUE in any family.

Limitations: test scenarios were deliberately selected for challenge, not sampled from production GhostMesh cases. Costs and rewards are toy units, incomparable to real service compute. The extra-work option is four further evaluations plus a fixed overhead, **not a stronger-model counterfactual**. There is no actual trained predictor of the best action, no model invocation, no calibrated escalation expected value, and no authority to dispatch.

Recommendation: do not adopt a rule such as 'always grant four more tries' based on this pilot. To assess stronger-model escalation, first collect offline nonprivileged model traces with real measured model-call costs, compare matched tasks and held-out labels, and retain an explicit no-escalation baseline. Keep Scout as discovery/research, not a production model dispatcher.

Results: `/tmp/scout-trial-34Lfv9/scout-three-way-extra-work-v0.json`.
