# Scout directional feedback ablation | Synthetic research receipt

Research-only. This is **not** a reproduction of SpecEvo, a real model evaluation, or evidence that an agent may exercise new authority.

Design: twelve fixed one-dimensional target tasks, sixteen paired seeds, twelve evaluator calls per arm and trial. Both arms use an identical fixed proposal stream and avoid evaluating the same candidate twice. Only the feedback arm uses an oracle telling it whether an evaluated guess is too high or too low.

| Metric | Ledger only | Directional feedback |
| --- | ---: | ---: |
| Trials | 192 | 192 |
| Mean best reward | 0.964451 | 0.999752 |
| Exact target found | 40 | 189 |
| Evaluator calls | 2304 | 2304 |
| Candidate proposals inspected | 2528 | 13104 |
| Privileged directional hints used | 0 | 1053 |

Interpretation: additional accurate information and rejection of candidates outside the implied feasible range markedly improve performance on this synthetic task. This is **not a same-information comparison** and does not isolate durable memory, model reasoning, or actual failure diagnosis. The extra oracle feedback and approximately 5.18-fold proposal-inspection cost must be budgeted explicitly.

Original paper that motivated the research question: https://arxiv.org/abs/2610.28706v1 . The paper's claims remain the authors' claims; this experiment is separately designed and does not verify its results.

Next decisive test: use noisy or misleading guidance, include a cost per feedback hint, measure total rather than evaluator-only budget, and add tasks where a 'too high/too low' signal cannot trivially reveal the optimal target. No production adoption, deployment, model calls or outreach.
