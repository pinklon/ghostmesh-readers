# Paper Reader successor qualification

**Stage:** local draft candidate for independent exact-head review and hosted preview, 2026-10-19 UTC. Sole writer `codex:/root/paper_reader_intake`, Readers [Issue #23 claim](https://github.com/pinklon/ghostmesh-readers/issues/23#issuecomment-6268858036). Branch `codex/paper-reader-preview-20261019` starts exactly at reviewed PR29 design head `ae2cb8cae3cf0aa48ecbbaf6e3c6ffadca32faf7` and does not modify PR29.

## Change and public boundary

The draft adds one paper Reader, `/the-experiment-ran-did-the-research-advance/`, for Peter Kirgis and coauthors' [arXiv:2607.27191v2](https://arxiv.org/abs/2607.27191v2). Its original analysis distinguishes completed engineering from research judgment and links directly to the pinned [HTML](https://arxiv.org/html/2607.27191v2) and [PDF](https://arxiv.org/pdf/2607.27191v2). The page uses the shared Reader brief, evidence register, receipt, related-thinking disposition, search and theme controls. Paper cards are link-only on home and archive; no player or media aspect is fabricated. The existing 17 video Reader IDs, permalinks, player rules, historical anchors and source-specific calls remain in place. No topical relationship is inferred for the paper.

The paper catalog carries seven attributed, **unverified** claims. The public knowledge v0.1 model adds one Reader, one exact attributed score claim and one source-declared citation to the original arXiv HTML; source hashes rebind to the generated 18-Reader pages. The citation does not certify the study's experiments or paper contents. Raw paper/PDF/HTML extraction, logs, manuscripts, figures and captions are not copied into this repository or generated site. The private adapter's PDF and HTML extractions remain partial and are not installed as a Readers runtime.

## Local verification

- `python3 scripts/generate_site.py --check`: 49 deterministic projections pass.
- `python3 scripts/knowledge_contract.py --check`: schema, exact page/source hashes, citation provenance, privacy and seven deterministic outputs pass.
- `python3 scripts/check_site.py`: all Readers, existing permalinks/anchors, claims, relationships, URLs, sitemap, editorial text and public boundary pass.
- Direct comparison against `ae2cb8c`: all 17 existing generated Reader pages differ only in the shared search label changing from 17 to 18 Readers. No original article body, anchor or media control changed.
- `python3 -m unittest discover -s tests -v`: 47 pass, including paper schema/source-shape negatives, video-only field rejection, pinned-link rejection, forbidden player/embed checks, no-JavaScript browse, source-only knowledge and existing video contracts.
- `git diff --check`: pass.
- Local loopback browser, Chrome headless: 200 response; visually inspected paper page at desktop 1440px and at true 390px iframe viewport in dark and light themes. The 390px document measured 375px scroll width inside a 390px viewport. With JavaScript disabled, DOM still included the paper title, pinned arXiv source link and claim register. No remote third-party player is required to read it. These local browser checks do not constitute a hosted Netlify preview or full accessibility audit.

## Unresolved release decisions

Tony should review the final headline, `Worth studying` verdict, claim wording, the paper route and the visual page at the hosted preview. The two cases were selected; original-author grading was non-blind; human research used substantially more time/GPU; TabPFN detailed logs and agent paper were withheld. The arXiv v2 revision date (August 7) and experimental HTML title-block date (August 24) remain discrepant. Figures, tables, equations, OCR, reading order, full logs and experiments were not independently verified; none can be promoted by extraction anchors. This candidate is reversible by closing its draft PR and dropping the successor branch. No merge or production deployment is authorized by this qualification.
