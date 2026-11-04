# Scout held-out stopping stress test | Counterexamples

Status: draft, synthetic, offline. No service or model dispatch authority.

A fresh deterministic fixture uses four 20-step reward-trajectory families and 20 disjoint test seeds per family. Three precommitted policies are compared: continue all 20 steps; stop after a high-enough four-step reward plateau from step 5; or use a later, higher-threshold plateau from step 10. Decisions examine prefixes only, with hindsight full continuation used exclusively to measure regret.

## Results

| Trajectory | Plateau premature stops / 20 | Cautious premature stops / 20 | Plateau mean missed gain | Plateau mean toy net versus continuing |
|---|---:|---:|---:|---:|
| Late breakthrough | 20 | 0 | 0.129851 | -0.096300 |
| False plateau | 20 | 20 | 0.022025 | +0.012897 |
| Steady progress | 0 | 0 | 0 | 0 |
| Flat noisy | 8 | 0 | 0.001160 | +0.042912 |

For the false-plateau scenario, cautious stopping also missed a later gain in all 20 trials (mean missed gain 0.021810), despite net positive toy utility because hypothetical evaluation costs outweighed the lost incremental reward. A positive toy net cannot erase the premature decision, especially for higher-stakes tasks.

The basic plateau rule's late-breakthrough mean saved expense is only 0.033550 while missing 0.129851 reward. Its net versus continuing is negative 0.096300.

## Interpretation

This contradicts any broad claim inferred from the earlier easy 1D trials that an observed plateau safely justifies stopping. Delayed breakthroughs and temporary plateaus can defeat even the cautious threshold. Because trajectory families were hand-designed to stress this problem and costs are arbitrary normalized values, these figures are counterexamples, **not prevalence estimates or production calibration**.

No stronger-model counterfactual has been evaluated. There was no escalation or model use. Remaining work: compare a bounded offline additional-reasoning option with continuing and stopping under explicit total budgets, and test real-world-sourced task traces before considering integration.

Machine evidence: `/tmp/scout-trial-34Lfv9/scout-heldout-stop-stress-v0.json`. No deployment, publication or outreach authorization.
