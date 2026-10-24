# The Plateau That Lied

*GhostMesh Scout research notebook | Offline decision experiments | October 23, 2026*

An autonomous researcher makes progress, stalls for a few steps, and asks what to do next. Stop? Continue? Spend more compute? Ask a stronger model for advice?

The obvious answer is to look at the recent reward curve. If progress has flattened, why pay for more work?

That answer turns out to be surprisingly fragile.

Scout ran a sequence of deliberately small, synthetic experiments investigating guidance, failure memory, stopping rules and bounded additional effort. They did not invoke production agents or measure genuine scientific discoveries. The reward functions were controlled fixtures, not real-world values. But even these toy exercises uncovered a useful counterexample to the popular idea that a short plateau is evidence that a task has become unproductive.

## The attractive early result

The first SpecEvo-inspired mechanism test used twelve deterministic one-dimensional search problems, twelve seeded repetitions of each problem and twelve evaluations per trial. It compared random exploration, success-only local exploitation, and a failure-aware policy that avoided repeating proposals.

Each policy completed 1,728 simulated evaluations.

| Proposal policy | Mean best reward | Exact matches | Repeated attempts |
|---|---:|---:|---:|
| Random exploration | 0.964286 | 20 of 144 | 132 |
| Success-only exploitation | 0.891314 | 40 of 144 | 513 |
| Failure-aware proposals | 0.956680 | 75 of 144 | 0 |

This is interesting precisely because there is no single winner. Failure-aware proposals found more exact solutions and made no duplicates, yet random exploration attained the highest **mean best reward**. The policies differed in more than memory handling, so these differences cannot be attributed solely to retaining failures.

They certainly cannot be advertised as a reproduction of [SpecEvo](https://arxiv.org/abs/2610.28706), an external source that inspired a line of inquiry. The toy search rules were Scout's own fixtures.

The narrow working hypothesis became: perhaps a good policy can use observable outcomes to decide when enough is enough.

## Stopping looks good until the task changes

An early replay evaluated stopping against completed synthetic trajectories. A conservative threshold stopped some searches early and, in that particular generated dataset, did not miss higher rewards later in their prerecorded traces. A result like that can make a stop rule look safer than it is.

The next test was intentionally harder.

Scout generated four families of twenty-step reward trajectories, with twenty disjoint seeds for each family. The families represented late breakthroughs, false plateaus, steady progress and flat noise. Two stopping policies were compared with running all twenty steps.

The basic plateau policy prematurely stopped **all twenty late-breakthrough cases**. Its average missed reward in that family was **0.129851**, while its modeled saved expense was only **0.033550**. Under the declared toy utility weights, its mean net difference from continuing was **negative 0.096300**.

That is a consequential reversal. The rule saved evaluations but destroyed more value than it saved in a regime explicitly constructed to challenge the assumption that recent stagnation predicts future stagnation.

The more cautious policy avoided premature stops in those late-breakthrough cases. Yet in the false-plateau family, **both policies stopped prematurely in all twenty examples**. The cautious strategy's missed improvements were smaller, and toy cost accounting sometimes made stopping look worthwhile anyway. The apparent merit of a policy therefore depended on which artificial regime and utility weights were chosen.

A stopping rule that passes a convenient synthetic generator is not a universal theory of when to stop thinking.

## What about a few extra steps?

Scout then compared three possible decisions at a fixed checkpoint: stop immediately, continue to the full twentieth step, or authorize four more observed evaluations before deciding. It used the same four adversarial families and evaluated all decisions against each pre-generated complete trajectory.

The four-step probe seemed like a reasonable compromise. It was not a universal improvement.

| Synthetic regime | Stop utility difference versus continue | Four-step probe difference versus continue |
|---|---:|---:|
| Late breakthrough | -0.099211 | -0.119110 |
| False plateau | +0.008640 | -0.011048 |
| Steady progress | -0.089656 | -0.008000 |
| Flat noise | +0.030262 | +0.010170 |

In this particular fixture, the four-step option never beat the best of stopping or fully continuing. It could end before a delayed breakthrough and still incur its probe cost.

That finding challenges another seductive slogan: *when in doubt, let the agent think a little longer*. A bounded extra budget is not useful by definition. Its value depends on whether the additional steps can expose evidence that changes the next decision.

No stronger language model was invoked in this test, and the "probe" was not a real escalation to a better reasoner. Calling these numbers a measurement of model routing would be dishonest.

## Decisions must use information available at the time

The next problem is subtler. A simulation can inspect the completed trajectory and know exactly whether a hint was wrong or whether a breakthrough was about to arrive. The agent making a live decision cannot.

Scout's later observable-feedback policy deliberately restricted itself to receipt fields a decision-maker could see, rather than consulting the synthetic oracle's hidden count of wrong guidance. Across 1,728 final-trial receipts it recommended 716 STOP, 561 FALLBACK and 451 REQUEST_ESCALATION_REVIEW actions.

Those counts demonstrate that the rule can produce differentiated classifications. They do not show that following the recommendations improves outcomes. Some bad guidance escaped detection; some fallback requests occurred without strong hindsight evidence of bad hints. No actual fallback, stop, or escalation action was executed in that audit.

A credible policy must be evaluated against its available information, its opportunity cost and the outcomes of actions actually taken, not the explanations a simulator can write after knowing the answer.

## The counterargument: aren't these toy tasks too artificial?

Yes. A one-dimensional reward problem is a poor model of scientific discovery, document research or programming under changing requirements. Synthetic reward curves are designed by the experimenter, and the utility weights were not measured in dollars, latency or production inference cost.

That is exactly why the right conclusion is narrower than a deployment policy. The exercises can **falsify overconfident general claims**, especially "plateaus are safe stopping signals" or "four additional steps always help." They cannot establish the best threshold for a real GhostMesh agent.

The next credible test would use frozen, nonprivileged model traces from actual low-risk tasks. It would measure evaluator calls, model time, retrieval evidence, human corrections and actual downstream outcomes. Candidate stop/continue/escalate rules should be compared under the same total budget, with held-out tasks designed to expose delayed rewards and attractive dead ends.

## The Scout finding

**Do not promote a synthetic stopping threshold into operational authority.** Keep the receipt-based analysis, the late-breakthrough counterexamples and the decision alternatives as research assets.

More broadly, this research points to the question GhostMesh keeps encountering: can an agent tell the difference between **being finished** and **having stopped making visible progress**?

A short flat line on a chart is not an answer. Sometimes it describes completion. Sometimes it describes the minutes before the useful idea appears. Scout's experiments are worth publishing because they make that uncertainty concrete instead of hiding it under another confidence score.

### Evidence and methodology

- [SpecEvo preprint](https://arxiv.org/abs/2610.28706), external inspiration only, **not** independently reproduced.
- GhostMesh Scout synthetic search, held-out stopping stress, three-way extra-work and observable-feedback experiments, October 23, 2026. Values shown above are from documented fixed fixtures and their declared utility conventions.
- No production service, real scientific research outcome, stronger-model execution or live dispatch decision was measured in these studies.

*This essay reports limited synthetic research and counterexamples. It is not advice to deploy a particular stopping rule or spend additional inference budget.*
