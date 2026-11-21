# Scout observable-feedback policy evaluation

**Status:** owner-private research. This is not a real-world confidence model or model-dispatch authority.

The prior synthetic decision policy relied on an oracle-provided wrong-hint count, which a real Scout observer would not know. The new `scout_observable_feedback_policy.py` uses an allowlist of observable receipt fields: input strategy, evaluation calls, remaining calls, proposal inspection count, hint count, detected search-range contradictions, measured best reward, and observed exact-task completion. It does **not** consume injected error rate or the hidden wrong-hint labels when choosing an action. Regression tests verify identical actions if those hidden fields are changed.

Across 1,728 offline final-trial receipts, the policy requested 716 STOP, 561 FALLBACK, and 451 REQUEST_ESCALATION_REVIEW actions. No CONTINUE actions were emitted because the records are end-of-trial snapshots. No actions were executed.

## Hindsight audit: fallbacks and errors

The synthetic oracle's actual wrong-hint counts are consulted *after* decisions only, to evaluate them. A case is classified as having bad guidance for audit when at least 25% of used hints were injected as wrong. This retrospective label is not available to the policy.

| Simulated error rate | Source strategy | Flagged cases with bad hints | Fallbacks without bad hints | Cases with bad hints but no fallback |
|---|---|---:|---:|---:|
| 10% | Always guided | 33 | 26 | 7 |
| 10% | Guarded | 27 | 27 | 13 |
| 30% | Always guided | 88 | 23 | 8 |
| 30% | Guarded | 73 | 22 | 23 |
| 50% | Always guided | 121 | 12 | 8 |
| 50% | Guarded | 100 | 9 | 29 |

These are **warnings, not quality improvements**. The rule can flag contradictions or extreme proposal effort, but plausible wrong guidance can escape detection. Some fallbacks are triggered where the audit does not establish high misinformation.

## Remaining gaps

- We do not yet have *intermediate* traces, so observed progress, regression and information gain over time cannot be computed.
- The observable reward and exact-completion witness are properties of synthetic evaluator tasks. More ambiguous real research requires independently specified success metrics.
- We have not tested outcomes after applying FALLBACK or STOP, so no claim of improved decisions is supported.
- There is no measured stronger-model expected benefit, latency, cost, or calibration. `REQUEST_ESCALATION_REVIEW` is non-executable.
- Current draft is isolated: no merge, model service integration, external account access, publication or outreach.

Next research capability: collect actual per-step decision traces, use precommitted held-out scoring, and replay counterfactual decisions without peeking at oracle truth. Evaluate net outcomes and missed opportunities against a baseline before authorizing any real escalation.
