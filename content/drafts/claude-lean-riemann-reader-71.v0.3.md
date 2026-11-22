# Claude, Lean, and the Riemann Hypothesis: What Has Actually Been Proven?

Private editorial v0.3 | GhostMesh Reader #71 | November 20, 2026
State: RESEARCH DRAFT, not Creative Lock, reviewed candidate, release or accepted mathematical proof.
Primary editorial intake: Control Tower #1169.
Snapshot: MIT verification record last updated November 21, 2026 at 12:55 UTC.

## Deck

A mathematician says he and Claude have proved a 167-year-old conjecture. His released Lean code has now survived a striking collection of independent technical checks. That is a historic-looking event, but it is not the same thing as a mathematical community declaring the Riemann Hypothesis settled. The interesting question is exactly what has crossed the proof boundary, and what remains to be understood.

## GhostMesh verdict

**Extraordinary source-backed formal verification progress; mathematical acceptance remains open.** Reader #71 should neither dismiss the evidence as a chatbot hallucination nor declare the problem solved. The appropriate headline reports the precise technical checkpoints, their independent provenance, their date, and their remaining limits.

## The three-move brief

1. **The proposition:** Every nontrivial zero of the Riemann zeta function has real part 1/2. Dirichlet GRH extends analogous claims to Dirichlet L-functions. The claim concerns the fine structure of prime distribution, not an instant attack on encryption.
2. **The artifacts:** Alpöge released a four-page account and fourteen Lean archive parts, crediting Claude with much of the difficult technical final stretch. He has not published a conventional, complete human-readable proof.
3. **The independent checks:** MIT reports that the Lean source compiles, has only standard axioms, uses Mathlib's own RH definition, and passes multiple kernel and statement-matching checks. The full lake comparator and full-export Lean kernel replays remained in progress at the observed November 21 12:55 UTC update.

## I. What exactly is the hypothesis?

Prime numbers become rarer as numbers grow, and the prime number theorem gives their approximate distribution. The Riemann Hypothesis (RH) is a much sharper claim connected to the zeros of the complex-valued Riemann zeta function, usually written as a function of a complex variable s. In the usual formulation, every nontrivial zero has real part 1/2. The familiar trivial zeros lie at negative even integers; the function has a pole at s = 1, not a zero. If correct, it constrains error terms throughout analytic number theory.

Dirichlet's Generalized Riemann Hypothesis (GRH) asks an analogous critical-line question for the Dirichlet L-functions connected to arithmetic progressions. It is stronger than classical RH. Alpöge's note also anticipates an *Extended* Riemann Hypothesis, but his anticipated extension must not be reported as an already checked theorem. Our source scope is classical RH plus Dirichlet GRH, with five publicized top-level theorems.

## II. What Alpöge and Claude say they did

Levent Alpöge announced on November 20 that he believed he had found a proof with Claude. His note traces ideas from Stepanov-style methods over function fields through Fourier analysis, automorphic forms, and iterated theta lifts. He describes choosing the larger direction while Claude supplied surprising technical moves, including a proposed chain length roughly proportional to the square root of a summation scale.

The public statement is first-person testimony about the research process, not a verified transcript of the Claude sessions. Alpöge says he had the broader analogy and selected the mathematical setting, while Claude suggested technical moves and far outpaced him near the finish. Its account of who originated which idea should not be silently elevated to an independently reconstructed authorship record. A chronological outline supplied in the note is useful evidence of what the author asserts, not a verified provenance trace for every human-AI exchange. The 250,000-plus pages he mentions were an informal generated 'book' he explicitly decided not to publish; that is not the 14-part Lean proof artifact now being checked.

The meaningful deliverable is the Lean formalization, not the emotional force of the announcement. Machines can present convincing mathematical narratives and still be wrong. Proof assistants change the question by requiring the kernel to accept a precisely stated sequence of deductions. They do not automatically supply conceptual understanding.

## III. Verification that matters

Andrew Sutherland of MIT maintains an independently reported verification record with command outputs, software versions and artifact hashes. **Sutherland states that he ran these checks with Claude Code.** His verification work is distinct from Alpöge's submission. nanoda and con-leche are separately implemented kernels, not evidence of wholly independent teams reproducing the mathematical discovery or completing a human audit. As of November 21 at 12:55 UTC, its status is:

| Check | Reported status | Meaning |
| --- | --- | --- |
| 175,187 Lean/Mathlib modules compile | PASS | Source elaborates and builds without Lean errors |
| Five theorem axioms | PASS | Only `propext`, `Classical.choice`, `Quot.sound` reported |
| Mathlib cache comparison | PASS | 8,322 Mathlib and 378 dependency compiled .olean files byte-identical to official cache |
| Lean kernel module replay | PASS | Every module replayed by `leanchecker` |
| nanoda independent Rust kernel | ACCEPT | Full exported proof accepted by a separate checker |
| con-leche independent kernel | ACCEPT | 1,468,418 full-export declarations accepted |
| con-leche independent challenge comparator | ACCEPT | All five submitted theorem statements justified against the challenge |
| lean4lean module-by-module | PASS | All 175,187 modules, with raised step limits for five |
| Full `lake comparator` | RUNNING | Statement/axiom phase passed, kernel end-to-end work unfinished |
| Default/paranoid Lean full-export replay | RUNNING | Full-export single-threaded passes had not concluded |

**None of these rows means GhostMesh executed the check.** They are Sutherland's published results with timestamped limits.

A crucial difference from a merely plausible proof sketch is the **statement-checking boundary**. One exceptional detail is easy to miss. The submitted `riemannHypothesis : RiemannHypothesis` uses the definition already present in Mathlib rather than a conveniently worded theorem unique to Alpöge's submission. The code's formula quantifies over complex zeros of `riemannZeta` and concludes the real part is 1/2 after excluding the trivial zeros and pole. This reduces a critical false-proof risk: proving an easier proposition whose name resembles RH. The independently checked statement comparison also strengthens confidence in the target. Yet understanding the entire mathematical construction and its significance is still a separate task.

Sutherland records caveats: the mass compilation was unsandboxed and used direct `lean` invocations rather than a complete, byte-for-byte confirmed `lake build`; dependencies and kernels remain software trust boundaries; older checker binaries declined unsupported features without formally rejecting the proof. Those caveats deserve visibility, not a footnote that disappears under a celebratory headline.

### November 21: an arithmetic cross-check

Sutherland additionally combined the submitted classical RH formalization with the separate Robin1984 Lean formalization (pinned commit \`acab1a3\`). This yielded two zeta-free statements: Robin's divisor-sum inequality for integers greater than 5,040 and Lagarias's inequality for every positive integer. In the 12:55 UTC record the combined export compiled with standard axioms, and nanoda and con-leche accepted it; con-leche independently matched both challenge statements. The combined \`lake comparator\` remained RUNNING. These checks probe arithmetic consequences of **classical RH** using another formalization, not Dirichlet GRH or Extended RH. They do not constitute a new proof by a second mathematical team. The combined statements still depend on Mathlib definitions and Robin1984.

## IV. What a proof checker proves, and what it does not

Formal verification has at least four layers. First, source code must elaborate and compile. Second, the completed theorem must depend on acceptable foundational axioms. Third, the checker or independently implemented kernel must accept the deductions. Fourth, the proved statement must faithfully correspond to the problem mathematicians meant to solve.

The first three have strikingly strong MIT-reported evidence, including independent implementations. The fourth has meaningful support because Mathlib's own statement is used and con-leche's independent comparator accepted all five challenge theorems. Broader mathematical acceptance is not simply another CI job. It does not follow that journal review is a fourth logical axiom: formal validity and the community's independent understanding are different kinds of evidence. Researchers still need to understand the argument, test its definitions and dependencies, compare methods, identify any hidden assumptions in mathematical interpretation, and assess what new mathematics has actually been obtained.

A proof need not be short or intuitively transparent to be valid. At the same time, acceptance by a kernel is not a free pass to claim a final solution to the world. A correct machine proof and a comprehensible human explanation are different scientific artifacts.

## V. Three ways this could still change

**Technical completion.** The MIT register has already reported a clean compilation, standard axiom checks, Lean-module replay and multiple independent checker acceptances, but its full `lake comparator` and the default/paranoid Lean-kernel full-export replay had no finished verdict at the latest cited time. They must remain **RUNNING**, not be silently promoted from other checks.

**Mathematical interpretation.** The statement matches Mathlib's native RH definition, and an independent checker compared the five targets with a challenge export. The community can still investigate dependencies, clarify arguments, and determine which ideas are genuinely new. A successful proof object does not automatically supply an intelligible mathematical proof narrative.

**Discovery provenance.** Alpöge's description credits Claude with essential technical steps. The machine-readable proof does not itself identify which collaborator first proposed each idea. Claims about AI creativity or autonomy require additional evidence beyond the validity of the theorem.

## VI. What changes if the claim holds?

The immediate mathematics would be extraordinary: classical RH, Dirichlet GRH, and a potentially new route across areas of number theory. Some theorems presently conditional on GRH could then become unconditional. But no general claim of instant encryption collapse follows, and any application still demands its own technical analysis.

The AI consequence might be even larger. Alpöge's description suggests not merely autocomplete for an existing proof but substantive participation in exploring or assembling an argument beyond his own immediate grasp. If the result survives and independent history of the human/AI work supports that account, it challenges comfortable assumptions about who must understand a proof during discovery, who is entitled to authorship credit, and where warranted trust actually resides.

If the claim fails, the failure mode would be equally valuable evidence: formal statement mismatch, kernel limitation, imported assumptions, provenance gaps, or a misinterpreted technical pass are different classes of error. A serious Reader would preserve the causal diagnosis rather than quietly erase the claim.

## VII. A GhostMesh operating lesson

The system of record should not treat a founder, a mathematician, a model vendor, a kernel, or a headline as unquestioned authority. Nor does a successful kernel check prove a result is understood, economically valuable, or correctly attributed to AI. It should track exact claims, immutable sources, technical check receipts, independent replication, expert interpretation, and explicit status transitions. The reader should be able to see what moved from CLAIMED to FORMALLY SUPPORTED, what remains RUNNING, and what still requires human intellectual appraisal.

The analogy to engineering is not perfect: mathematical proof has an unusually crisp formal target, while production systems face messy operational environments. Yet the central discipline transfers. Model confidence does not confer authority; inspectable evidence, appropriate independent checks, and competent interpretation do.

## Claims, counterevidence, and limits

Andrew Granville told Nature that the available write-up was difficult to assess. That is consequential criticism of interpretability, not a counterexample or a rejected formal verification. Clay still lists RH as unsolved, and its prize criteria are distinct from Lean kernel acceptance. See the [Nature report](https://www.nature.com/articles/d41586-026-03812-7), [Clay RH status](https://www.claymath.org/millennium/riemann-hypothesis/), and [Clay Millennium Prize rules](https://www.claymath.org/millennium-problems/rules/).

- **Claim:** A complete classical RH and Dirichlet GRH proof exists. **Role:** Alpöge's claim, with strong MIT-reported independent formal checks. **Open:** final checks, broad mathematical understanding and acceptance.
- **Claim:** Claude provided critical novel steps. **Role:** Alpöge's testimony. **Open:** external reconstruction of collaboration and causal credit.
- **Claim:** The theorem proved is really RH. **Role:** MIT's Mathlib definition and independent comparator checks. **Open:** sustained mathematical scrutiny.
- **Claim:** The claimed result immediately destroys cryptography. **Role:** unsupported extrapolation. **Disposition:** do not state.
- **Claim:** Extended RH is proved. **Role:** unsupported by the scoped author note and MIT register. **Disposition:** do not state.
- **Claim:** Clay has accepted or awarded a Millennium Prize. **Role:** not established. **Disposition:** do not state.

## Relationship candidates, subject to canonical review

- [Reader #48: The Paper Is Not the Experiment](https://youtube.shareplane.malott.ai/the-paper-is-not-the-experiment/): scientific assertions, exact experimental artifacts and independent scrutiny. Distinct from this article's proof-object checks.
- [Reader #70: A Smaller Model Can Win the Job, Not the Benchmark War](https://youtube.shareplane.malott.ai/a-smaller-model-can-win-the-job-not-the-benchmark-war/): warns against promoting an evaluation result into a broader claim about model intelligence.

Only the two Reader companions are admitted pending final canonical checks. The proposed SharePlane companion redirects to a review-transfer document, so it is excluded. **None of these editorial relationships independently verifies RH or GRH.**

## Source and verification record

Author note: https://alpo.ge/remark.pdf (November 20, 2026; archived privately, SHA-256 3fc97784b71ddd44ff8aa0a177e99622a1c61b13cfa843a0989ee4a7a0cfeb8d).

Independent technical register: https://math.mit.edu/~drew/grh/ (Andrew Sutherland, snapshot updated November 21, 2026, 12:55 UTC). See the companion machine-readable private evidence register for each reported status.

Independent reporting: https://www.nature.com/articles/d41586-026-03812-7 (media context and expert caution, not kernel verification).

Official prize/institutional status: https://www.claymath.org/millennium/riemann-hypothesis/ and https://www.claymath.org/millennium-problems/rules/.

A second retrieval of the MIT page returned byte-for-byte unchanged source at the same reported update, with SHA-256 `de7153ec1b22acab193a99824d427d41050e2c0d2c4374ec518d52fc0de62307`. This is a source refresh, not a fresh technical check.

All evidence status claims above are **as of the named source snapshot**. Refresh the MIT page at manuscript freeze and again before publication. Never silently rewrite a locked manuscript merely because a status moves.
