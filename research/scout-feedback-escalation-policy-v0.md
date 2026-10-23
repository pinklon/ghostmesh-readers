# Scout feedback-confidence and escalation review policy

Research status: **simulation only**. No runtime executor, external model call, or authority delegation.

The prototype evaluates 1,728 existing offline trials from the noisy-guidance pilot. A deterministic rule returns CONTINUE, FALLBACK, STOP, or REQUEST_ESCALATION_REVIEW, together with its reason and a non-executable review record.

## Important caveat

The prototype calculates its hint-reliability proxy from **oracle-labeled wrong hints** in synthetic experiments. This information is **not available** from an ordinary real-world agent or an unverified model critique. Therefore no calibration, real-time confidence measurement, claim of optimal policy, expected-value model, or safe production escalator has been demonstrated.

The policy also reports a *hypothetical* stronger-model cost; it does not establish expected benefit or dispatch authority. Reaching the trial's twelve-evaluation limit is a trigger for review, **not** a mandate to use an expensive model.

## Pilot coverage

- 12 target-search tasks, 12 seeded repeats, 4 simulated error rates, 3 exploration policies.
- Total of 1,728 trial-level action suggestions across the four action categories.
- In the noiseless always-guided cohort, 143 STOP and 1 REQUEST_ESCALATION_REVIEW.
- In the 50%-error always-guided cohort, 106 FALLBACK, 26 CONTINUE, 11 STOP and 1 REQUEST_ESCALATION_REVIEW.
- In the ledger-only cohorts, an exhausted search without an exact match is flagged for review, not automatically escalated.

## Next qualification

Replace oracle truth with observable evidence, such as held-out independent checks, measured contradiction, and actual evaluation outcomes. Explicitly account for false fallback, unnecessary escalation, missed improvements, model cost, and early stopping on difficult tasks. Demonstrate benefit against a no-policy baseline **before** proposing agent integration.

Full machine-generated receipt: `/tmp/scout-trial-34Lfv9/scout-feedback-policy-v0.json` on the research VPS. No production adoption, publication, or outreach authorized.
