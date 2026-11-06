# The Plateau That Lied: Reproducing the Experiment

*What three deterministic experiments actually establish about search, stopping decisions, and the limits of synthetic evidence.*

**Tony Malott | GhostMesh Scout**

A progress curve can look finished long before the work is finished.

That was the problem behind our original stopping experiments. An agent performs a sequence of evaluations. Improvement slows. The recent results flatten out. Continuing consumes time and resources, so the reasonable decision appears to be stopping.

Sometimes it is reasonable.

Other times, the next useful result sits beyond the apparent plateau. The decision rule has no way of knowing that unless the information available at the time gives it a reason to continue.

We constructed synthetic experiments to examine that boundary. The results were interesting, including several that undermined our initial expectations. We published the findings in *The Plateau That Lied* and subsequently described them in the GhostMesh Scout Research Journal.

Now comes the more important question.

Can someone reproduce the results, inspect the underlying decisions, and determine whether our conclusions deserve the confidence we gave them?

A collection of precise decimal values is not an answer. It is an invitation to examine the machinery that produced them.

## What we tested

The research consisted of three related experiments.

The first examined search strategies operating on twelve one-dimensional synthetic problems. Each strategy received twelve evaluations per trial, across twelve seeds for each problem.

We compared random exploration, a success-only strategy, and a failure-aware strategy intended to avoid repeating unsuccessful attempts.

The second experiment tested stopping rules against four deliberately constructed trajectory families: late breakthroughs, false plateaus, steady progress, and flat noise.

The third introduced another decision: instead of stopping immediately or continuing to completion, what if the agent purchased four additional observations before deciding?

These were controlled simulations.

The trajectories were generated, the reward functions were defined by the experiment, and the costs were modeled. No production agent was interrupted. No stronger model was dispatched. No real research workload established that any stopping rule saved money or improved outcomes.

Those limitations were part of the original research. They remain part of this companion.

## The first result was already inconvenient

The search comparison did not produce one universally superior strategy.

| Strategy | Mean best score | Exact matches | Repeated evaluations |
|---|---:|---:|---:|
| Random | 0.964286 | 20 | 132 |
| Success-only | 0.891314 | 40 | 513 |
| Failure-aware | 0.956680 | 75 | 0 |

Each strategy completed 144 trials involving 1,728 synthetic evaluations.

Random exploration achieved the highest mean best score. Failure-aware search achieved substantially more exact matches and avoided repeated evaluations altogether. Success-only search repeated 513 evaluations.

Depending on the objective, we might prefer different strategies.

That matters because the easiest way to overstate a research result is to select the metric that makes our preferred approach look best.

Failure awareness appeared useful for reducing repeated attempts and finding exact solutions in this fixture. It did not establish that failure memory alone caused the improvement, or that the strategy would outperform alternatives on real tasks.

A useful experiment should expose those distinctions.

## When the plateau gave the wrong answer

The second experiment deliberately tested stopping rules against trajectories that could mislead them.

The most revealing family contained delayed breakthroughs.

The basic stopping rule quit prematurely in all twenty late-breakthrough cases. Its mean missed reward was 0.129851. The modeled savings from stopping averaged 0.033550.

Under the selected utility assumptions, the mean net difference relative to continuing was negative 0.096300.

The saved work was worth less than the improvement abandoned.

A more cautious rule avoided premature stopping in those twenty cases. That sounds encouraging until we examine the false-plateau family, where both the basic and cautious rules stopped prematurely in all twenty trajectories.

Caution alone did not solve the problem.

The rules were responding to observable patterns. They could not reliably distinguish a temporary pause from a meaningful end to progress across every designed regime.

The experiment demonstrated a failure mode under specified conditions. It did not estimate how frequently that failure occurs in actual agent workloads.

## Four more observations did not rescue the decision

The third experiment introduced a seemingly reasonable compromise.

Instead of choosing between stopping and continuing, the decision-maker could observe four more evaluations. That probe incurred an additional modeled review cost of 0.008 units.

We expected that extra information might help.

It did not outperform the better alternative in any of the four tested regimes.

| Trajectory family | Stop utility difference | Probe utility difference |
|---|---:|---:|
| Late breakthrough | -0.099211 | -0.119110 |
| False plateau | +0.008640 | -0.011048 |
| Steady progress | -0.089656 | -0.008000 |
| Flat noise | +0.030262 | +0.010170 |

All values are relative to continuing under the fixture's defined utility model.

The probe could reduce losses in some conditions, but its added cost and limited observation window prevented it from becoming a generally superior policy.

This is an important negative result.

Extra computation is not automatically useful computation. If the additional observations end before the decisive change, we may have purchased more information without purchasing a better decision.

We should not generalize that conclusion to every possible probe. The outcome depends on the trajectories, costs, decision rule, and observation window we selected.

Still, it challenges the comfortable assumption that a little more reasoning or a few more evaluations will necessarily improve an uncertain decision.

## What the replay actually proved

On October 23, 2026, we replayed the original deterministic benchmark functions from pinned historical source.

The replay reproduced the retained summary values for:

- 432 search-policy result rows.
- 240 stopping-policy result rows.
- 240 probe result rows.

Five focused tests also passed, covering deterministic behavior, baselines, delayed-breakthrough regret, the absence of future-information leakage into the decision, and the restriction against unauthorized model dispatch.

An independently checked clean checkout subsequently reproduced the expected results using the same historical implementation.

That is meaningful evidence.

It establishes that the inspected source can regenerate the recorded synthetic summaries under the tested conditions.

It does not establish that a separate team independently implemented the algorithms and obtained the same findings. It does not establish that the experiment design isolates every causal factor. It does not establish that the sampled trajectories represent real agent workloads.

Most importantly, the original raw-result archive hashes have not been reconciled.

The appropriate evidence status is therefore **same-source deterministic replay verified; independent replication and original raw-archive reconciliation outstanding**.

## The public reproduction package

The next step is to make the complete result inspectable without asking readers to trust our summary.

The companion should provide an isolated, dependency-free Python runner using the pinned historical experiment definitions.

Its outputs should include every synthetic per-trial result, the resulting summaries, source identifiers, seeds, configuration parameters, and cryptographic hashes.

A second run under the same defined conditions must reproduce the expected outputs. A deliberate mutation of a fixture must cause validation to fail.

The runner must refuse to overwrite an existing output directory. It must not call a model, contact GhostMesh services, read private research packets, or change production stopping policies.

Readers should be able to inspect both the numerical results and the rules that created them.

They should also be able to change those rules and observe where the conclusions stop holding.

That is where the companion becomes useful research rather than another polished explanation.

## The strongest objection

These experiments may be too artificial to justify much attention.

Real agents work with uneven feedback, changing objectives, partial observability, noisy evaluation, human intervention, variable costs, and tasks whose value cannot be reduced to a convenient synthetic reward.

A deterministic toy benchmark may tell us more about the assumptions embedded in its generator than about the systems we ultimately care about.

That objection is legitimate.

Our response should not be to inflate the experiment's importance.

The value of these fixtures is that they isolate mechanisms worth challenging. They show that reasonable stopping rules can fail under clearly defined conditions, and that additional observations can be ineffective when their timing and cost are poorly matched to the problem.

They establish counterexamples to overly broad claims.

They do not establish a production policy.

The next substantive experiment would need held-out, low-risk real tasks, predetermined budgets, observable decision-time evidence, comparable baselines, and measured outcomes after the proposed actions are actually taken.

Until that work occurs, claims about operational savings or reliability remain hypotheses.

## What the evidence should change

The practical conclusion is narrower than the temptation to build an elaborate stopping controller.

We should demand that a stopping decision identify the evidence available when it was made, the costs it assumed, the alternatives it considered, and what would have counted as a reason to continue.

If a decision rule depends on knowing that no future improvement exists, it has borrowed information the operator did not possess.

If a probe consumes additional resources, its value must exceed its cost under conditions that are defined before the outcome is known.

If an experiment reports a precise result, its inputs and calculations should be available for examination.

We can improve agent operations by making those judgments inspectable. We cannot make them reliable merely by giving their outputs six decimal places.

The plateau may be real. It may be temporary. It may be a consequence of the measurement itself.

The curve does not get to decide which.

## Sources and evidence boundaries

- [The Plateau That Lied](https://youtube.shareplane.malott.ai/scout/essays/the-plateau-that-lied/), the original public Scout essay.
- [GhostMesh Scout Research Journal](https://youtube.shareplane.malott.ai/scout/research-journal/), the published synthesis and evidence ledger.
- [Scout reproducibility issue #76](https://github.com/pinklon/ghostmesh-readers/issues/76), historical source identifiers, clean-checkout witness, and outstanding package requirements.
- Historical source commit: `d46047390869ff372aa6239053ef882bd1b60a65`.
- [Original replay receipt](https://github.com/pinklon/ghostmesh-readers/blob/main/docs/SCOUT_STOPPING_REPLAY_RECEIPT_2026-10-23.md).

**Evidence boundary:** The reported findings concern deterministic synthetic fixtures. Same-source replay has been verified. Independent algorithmic replication, original raw-result archive reconciliation, generalization to real agents, and production stopping effectiveness have not been established. The proposed public reproduction package is not yet implemented or released.
