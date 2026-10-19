# Reader candidate: The Test Must Name Its Target

Stage: isolated draft for independent editorial review. Source inspected 2026-10-19 UTC. This is **not** a publication or a verified full ReasonPack.

## Source identity and custody

Tony supplied [the public YouTube source](https://www.youtube.com/watch?v=7O84mdxehWY). Read-only `yt-dlp` inspection reported video ID `7O84mdxehWY`, title “AI Doesn't REALLY Understand. We've Said That Before.”, creator Count Grey Matter, upload date 2026-10-18, duration 1,378 seconds, public availability and landscape 16:9 formats. English automatic captions were reviewed privately as a topic and timestamp aid. Their SHA-256 is `c6d95a76711fce98ddb2c93c8130007a3295692eb0d474899fac9a5f3f84f082`. They can mishear wording; no verbatim caption quotation is published, and the audio was not fully cross-checked. Private caption text and signed download metadata stay outside this repository. No qualified full private ReasonPack is claimed.

The caption aid confirms the video's own sequence: moving historical lines at 00:51–09:32; Chinese room and octopus objections at 09:32–12:20; a Hinton-derived representation explanation at 12:20–18:01; and the narrator's functional-understanding verdict at 18:01–21:33. The exact chapter starts are also present in the public source description. These observations establish what the creator argues, not whether the argument is correct.

## Independent direct-source check

| Consequential point | Direct source checked | What it supports and cannot establish |
| --- | --- | --- |
| Dreyfus's 1965 argument | [RAND publication P-3244](https://www.rand.org/pubs/papers/P3244.html) | Verifies the historical paper argues then-current digital methods miss named human cognitive processes. It is not a present AI benchmark. |
| 73% human judgment | [Jones and Bergen, 2025](https://arxiv.org/abs/2503.23674) | Reports GPT-4.5 with a humanlike persona was judged human 73% in five-minute, three-party conversations. The protocol does not directly test semantic grounding or experience. Preprint result was not independently replicated here. |
| Meaning from form objection | [Bender and Koller, ACL 2020](https://aclanthology.org/2020.acl-main.463/) | Primary position paper argues form-only training has no a priori route to meaning. It is a theoretical counterargument, not a universal empirical test of current systems. |
| Spatial and temporal representations | [Gurnee and Tegmark, version 3](https://arxiv.org/abs/2310.02207) | Reports linear representations in studied Llama-2 models and datasets, with further investigation needed. It does not prove generally reliable world understanding. |
| Synthetic board representation | [Li et al., ICLR 2023, version 5](https://arxiv.org/abs/2210.13382) | Reports an internal Othello state representation and interventional output effects. The synthetic game does not settle open-world grounding. |

Sources were checked on 2026-10-19; the paper versions and creator's interpretation remain distinct. The video's Hinton talk clip is attributed to the creator's public source list but the source talk's exact quoted wording has **not** been independently checked; the draft makes no exact quote from it.

## Editorial judgment

**Interesting, unproven.** The historical argument is a useful warning against lazy impossibility claims, and the representation papers complicate a “mere string lookup” account. The narrator's closing claim that current systems understand much as people do exceeds the scopes of the cited imitation and representation studies. The intended audience is researchers and product teams setting evaluation criteria. Watch selectively at 08:10, 09:32, 12:20 and 18:01. For operational decisions, define a task and failure criterion, test grounding and changed premises, and keep authority boundaries explicit. The draft makes no claim about subjective experience.

## Candidate and checks

Authored source: `content/readers/the-test-must-name-its-target.html` and the corresponding `content/catalog.json` entry, seven claim assessments, five direct references, one qualified relationship to `the-microscope-is-not-a-soul`, and a sanitized generated receipt. All 14 incumbent Reader routes remain. The public knowledge source inventory is pinned to generated page hashes; no external graph admission is asserted.

`python3 scripts/generate_site.py --check`: 43 deterministic projections pass. `python3 scripts/knowledge_contract.py --check`: seven deterministic outputs, source hashes and provenance pass. `python3 scripts/check_site.py`: Reader, evidence, relationship, URL, sitemap and privacy checks pass. `python3 -m unittest discover -s tests -q`: 39 tests pass. `git diff --check`: pass. Local Chrome rendered the candidate at desktop 1440 and mobile 390; one H1 and zero page overflow at each. Screenshots are task-local, not hosted preview acceptance. Independent editorial/source review and optional audio spot checks remain before a PR or publication decision.
