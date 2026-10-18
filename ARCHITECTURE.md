# GhostMesh Public Knowledge Contract v0.1

## Scope and authority

This is a **public, source-only projection** of existing GhostMesh Reader text. It identifies all 13 normalized Reader pages, and transcribes one exact claim and citation from the evidence ledger at `/the-inbox-was-a-boundary/`. Other Readers have identity records only; absence of projected claims does not mean their claims were verified or absent. The site remains a static Netlify publication. Reader routes, layouts, playback behavior, and GhostMesh identity remain the source experience. The contract does not assert live deployment parity.

The projection is not a new canonical knowledge graph, SharePlane KOS admission, Library Atlas corpus authority, Tony Brain context export, or Control Tower writer. Its `urn:ghostmesh-readers:*` IDs identify records only within this Reader projection. They must not be treated as SharePlane `artifact:*` or `relationship:*` IDs. `source-declared` means an exact public page already contains the claim and link; it does not mean an owner accepted a mesh relationship.

## Contract

`knowledge/v0.1/contract.schema.json` pins the v0.1 JSON shape. Each node has a stable local ID, a type, visibility and an epistemic status. A Claim also has exact published wording, a Reader source ID, an HTML anchor, the full source file SHA-256, and the SHA-256 of its UTF-8 statement. The EvidenceSource has the SHA-256 of its URL string. Its `contentSha256` is `null` because the external report bytes are outside this repository's custody. No content hash is inferred from a URL or from the article's own description of the report.

The only v0.1 relationship is a Claim-to-EvidenceSource `cites` link that must already exist in the Reader page. The validator rejects other endpoint classes, predicates and authority values. A future contract version may add kinds only after source owner and semantic owner review. Existing IDs must remain stable for unchanged referents; changed meaning requires a new claim ID and explicit supersession design.

The state axes are deliberately separate:

| Axis | v0.1 value in the reference | Meaning |
|---|---|---|
| Visibility | `public` | Eligible for this public static projection after source checks |
| Epistemic status | `source-editorial`, `attributed-report`, `external-primary-report` | What the Reader source says about origin and certainty |
| Relationship authority | `source-declared` | A citation present in the published page, without graph admission |
| Publication mode | `source-only` | Static representation; no writeback or downstream promotion |

## Deterministic build and public surfaces

`python3 scripts/knowledge_contract.py` checks the closed JSON Schema vocabulary offline, validates each record against the schema and complete public catalog, verifies all 13 Reader file hashes, checks exact claim text at its declared anchor and the cited URL, rejects nonpublic classification and private markers, then writes the public outputs. `--check` verifies byte-for-byte regeneration without writing. `scripts/generate_site.py` owns the homepage and sitemap links to `/knowledge/`; the knowledge page uses the normalized site's shell and theme controls.

The generated outputs are:

| Path | Role |
|---|---|
| `site/knowledge/v0.1/readers.json` | Versioned typed records |
| `site/knowledge/v0.1/readers.jsonld` | JSON-LD representation using Schema.org types and projection-local properties |
| `site/knowledge/v0.1/contract.schema.json` | Public schema copy |
| `site/knowledge/index.html` | Branded semantic HTML with visible status and evidence links |
| `site/.well-known/ghostmesh-knowledge.json` | Agent discovery pointers |
| `site/llms.txt` | Plain text discovery pointer |
| `site/knowledge/v0.1/publication-manifest.json` | Source/schema hashes, output path/byte/hash inventory and aggregate output digest |

The manifest intentionally omits a self-hash. Entries are sorted by path and encoded with sorted JSON keys, UTF-8 and a terminal newline. No clock, build machine path, Git branch name, provider response, or network fetch participates in the output. The root page advertises discovery; `/knowledge/` is in the sitemap.

## Security and failure behavior

Only checked-in public Reader HTML is eligible. The contract requires `public` on every node and relationship. No adapter reads Tony Brain, Atlas, SharePlane, credentials, local private media, or source transcripts. A missing source, changed source hash, changed quote, missing anchor/link, unrecognized schema keyword, or stale generated output fails closed. The leakage scan rejects private path markers, token-like strings, private key markers, and email addresses in the knowledge model and generated outputs. This scan is a defense in depth check; source ownership and human privacy review remain required.

Static hosting serves the generated files only after a separately authorized merge and deployment. This branch and any draft PR are review candidates, not publication.

## Ownership evidence inspected

| Repository | Bound `main` | Existing custody |
|---|---|---|
| `pinklon/ghostmesh-readers` | `8a7d9a8e2f394708d44ef7d31ee0f3c8740b877e` | Public static Reader source, `scripts/check_site.py`, sitemap, Netlify `site/` |
| `pinklon/shareplane-platform` | `358f1fd9bec93c0b30a66979e0e412c5d8abc746` | Admitted Work/relationship authority in `control/kos`; #1471 directs reuse of #929 graph admission and source owners |
| `pinklon/shareplane-control-tower` | `f5d4d7f0153c5ac3d8f9906acb3926ab63812117` | Admission, orchestration and owner projection; `architecture/mesh-state-authority-registry.v1.json` |
| `pinklon/tony-brain` | `b6109881c47082d169bf58fbfeef1925c664fb0c` | Owner-controlled context, evidence and privacy rules in `AGENTS.md` and `90-system/` |
| `pinklon/library-atlas` | `8ee62192cacdc43403dad5b76c59aeb7209ef9a8` | Implementation and projections; corpus identity and sensitivity remain in the owner Atlas control plane per ADR-0001 |

These are inspection snapshots, not permanent currentness claims. No file in the other four repositories was changed.
