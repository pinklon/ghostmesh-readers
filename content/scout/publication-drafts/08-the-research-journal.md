# The Research Journal: What Scout Actually Tested

**GhostMesh Scout | Editorial development draft | October 23, 2026**

*We have published the method. Now the findings need a ledger that separates a promising source, a reviewer's judgment, a synthetic experiment and a result somebody can reproduce. Those are four different things.*

A research program can accumulate a surprising amount of activity without accumulating the same amount of knowledge. A dozen feeds produce links. A reviewer finds connections. A simulation produces numbers. The temptation is to arrange all of that in a beautiful interface and call the result intelligence.

We have done enough work on Scout to know why that shortcut fails.

This journal records two bounded research families documented in the public Scout essays. One concerns ideas outside our usual search vocabulary. The other concerns stopping decisions when apparent progress stalls. Both produced useful questions. Neither authorizes a production change. The private research corpus may contain more work, but its total and disposition are still UNKNOWN pending an authorized inventory.

## The research register

| Investigation | Observed evidence | What it establishes | What it does not establish |
| --- | --- | --- | --- |
| Outside-vocabulary discovery | An editorially documented 21-item comparison, from nine familiar-topic and twelve outside-vocabulary selected leads | Five outside-vocabulary items received strong or concrete relevance judgments; six familiar-topic items received those judgments | A population success rate, independent technical validation or measured adoption value |
| Synthetic proposal policies | Twelve one-dimensional problems, twelve seeds each, twelve evaluations per trial across three policies | Policies traded off mean best reward, exact matches and repeated attempts | That failure memory alone caused the difference, or that any policy is best for real agents |
| Adversarial stopping curves | Four families of twenty trajectories, including delayed breakthroughs and false plateaus | A basic plateau rule prematurely stopped all twenty delayed-breakthrough cases | A production stopping threshold or reliable probability of future improvement |
| Four-step decision probe | Stop, continue or observe four more steps in fixed synthetic trajectories | The probe did not beat the best alternative in any tested regime under those toy utilities | That bounded extra computation never helps on real work |
| Observable-feedback classification | 1,728 synthetic final-trial receipts classified into 716 STOP, 561 FALLBACK and 451 REQUEST_ESCALATION_REVIEW recommendations | The rule can classify visible receipt patterns without consulting a hidden hindsight field | That taking its recommended actions improves outcomes |

These numbers come from the existing public essays and their cited research descriptions. This draft has **not** independently rerun the original fixtures or reconciled all raw receipts. We should not describe the table as a fresh experimental replication.

## Discovery beyond the dictionary

The comparison started with 59 lead observations. The existing research account says nine matched the familiar-topic dictionary and fifty did not. A deterministic, source-balanced process selected twelve outside-vocabulary leads across eleven source streams, producing a 21-item editorial review when combined with the nine familiar-topic leads.

Five of those twelve outside items were judged strong or concrete. Six of the nine familiar items received the same grades. The familiar lane therefore had the higher fraction by the reviewer's own measure. That matters. It would be convenient to announce that the unexpected ideas won. They did not.

The useful result is narrower: a modest reservation of attention for unfamiliar vocabulary surfaced five plausible connections that a dictionary-only queue would have omitted from this particular review. That is a reason to keep examining the second lane, not a reason to call it an innovation detector.

The reviewer was not assessing equivalent verified implementations. Evidence maturity varied from source descriptions to papers, and some candidates were examined in a corrected second pass that was not newly blind. Selection was bounded, not population-representative. The denominator is twenty-one selected items, not the technical internet.

A second historical record mentions a fourteen-case study. We have not established whether it was a fresh round, an overlapping subset, or an alternate selection. It stays a separate unresolved record. Combining fourteen and twenty-one into a bigger, more impressive cohort would be accounting theater.

The next test is straightforward and deliberately less flattering. Freeze a new source snapshot, assign masked lead packets to independent reviewers with equal time budgets, preserve abstentions, and measure the rate and cost of useful retained candidates. Only then ask whether any lead survived a technical comparison and changed an actual decision.

## Why the reward curve lied

The stopping experiments expose a different failure mode. A researcher sees a flat progress curve and decides further work is wasteful. Sometimes that is correct. Sometimes the curve is hiding a delayed breakthrough. The problem is whether the decision rule can tell which case it is using information actually available at the time.

The first proposal-policy fixture had three strategies: random exploration, success-only exploitation and failure-aware proposals. Each completed 1,728 simulated evaluations across the specified toy tasks. Random exploration produced the highest mean best reward at 0.964286. Failure-aware proposals produced 75 exact matches out of 144 and zero repeated attempts; success-only exploitation produced 40 exact matches and 513 repeats. Those are distinct objectives. Calling any one strategy the winner would conceal the tradeoff.

The adversarial stopping test was more pointed. In the late-breakthrough family, a basic plateau rule stopped prematurely in all twenty cases. Its mean missed reward was 0.129851, against modeled savings of 0.033550. The mean net difference under the selected toy utilities was negative 0.096300. A cautious rule avoided those late-breakthrough stops but both rules still stopped prematurely on every false-plateau trajectory in a different family.

Then the four-step probe was tested. Four more observations sound sensible. Yet the probe failed to outperform the best of immediate stopping and full continuation in each tested regime. In the late-breakthrough family, its utility difference relative to continuing was negative 0.119110. Extra steps can be wasted when they end before the decisive information arrives.

Those are counterexamples, not operational recommendations. The trajectories and reward functions were invented for the experiment. No stronger language model was actually dispatched, and no production research task was stopped or continued by these rules.

The later receipt-only classifier recommended 716 stops, 561 fallbacks and 451 escalation reviews across 1,728 final-trial receipts. That is a distribution of recommendations. No one should quietly convert it into a success rate. The actions were not executed as part of that audit.

## The missing replication package

For the outside-vocabulary work, a proper public companion would include a redacted, frozen list of source identifiers, source-role labels, the selection algorithm, the exact predeclared dictionary, review rubric, reviewer independence statement and complete counts including abstentions. Private intake packets and contact information must remain private.

For the stopping study, it would include the synthetic generator version, seeds, full parameter choices, stop-rule definitions, utility weights, executable test script, raw per-trial results and a one-command reproduction procedure. It must label which outcomes were simulated and which came from any later real task. We do not yet have a verified, public-safe reproduction bundle in this publication lane.

That gap is worth closing. Source prose with impressive decimals is still source prose. A small runnable fixture can make it inspectable.

## What should be challenged next

**Retrieval challenge.** Does the outside lane improve recall of useful ideas under a fixed examination budget, once selection and reviewer bias are addressed? The baseline is the familiar lane alone. The failure condition is that extra candidates cost more attention without yielding independently useful findings.

**Stopping challenge.** Do receipt-only stop, continue and escalation policies improve measured outcomes on held-out low-risk tasks under equal compute and human-review budgets? Delayed reward and false plateau cases should be designed into the test. The failure condition includes lost value that exceeds saved work.

**Continuation challenge.** Can a research task move between authorized workers without inventing an observation, redoing a protected action, or losing the source and decision trail? The baseline should be an ordinary handoff with the same task and fixed budget. A verbose summary is not proof of faithful continuation.

These are proposals. Dennis, Vic and others have offered opportunities to challenge assumptions, but the public journal must not present those conversations as completed experiments or imply consent to publish participant details.

## What changes the public record

A new result belongs here only when we can say which source was inspected, which fixture actually ran, what baseline it faced, what failed, and what was authorized for disclosure. A negative result is eligible. An unresolved result is eligible. The label must tell the truth.

The current nine-work Scout library remains the published register. This journal is an **unpublished editorial draft**, not a tenth published investigation. The total number of owner-private research packets is UNKNOWN. No new public release event or claim of daily provider-watch success is implied.

Our next job is to make one experiment reproducible enough that a skeptical reader can break it. If the result survives, excellent. If it falls apart, that is research too.

### Public source trail

- [How GhostMesh Scout Actually Researches](https://youtube.shareplane.malott.ai/scout/method/). Published methodology and explicit status distinctions.
- [Five Ideas Outside the Filter](https://youtube.shareplane.malott.ai/scout/essays/five-ideas-outside-the-filter/). Source for the 59-lead observation, 21 selected items, reviewer ratings and sampling caveats.
- [The Plateau That Lied](https://youtube.shareplane.malott.ai/scout/essays/the-plateau-that-lied/). Source for the deterministic search fixtures, adversarial stop policies and reported synthetic values.
- [Follow the Work, Not the Follower Count](https://youtube.shareplane.malott.ai/scout/essays/follow-the-work/). The broader twelve-stream acquisition pilot and evidence ladder.

**Editorial status:** Source-backed draft for Tony and segfault review. Raw fixture reproduction, current private inventory and any new participant disclosures remain unverified. Not approved for publication.
