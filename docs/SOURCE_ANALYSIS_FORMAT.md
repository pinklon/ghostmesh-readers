# Public-record source analysis contract

This source type supports an owner-approved GhostMesh article built from several public records on the existing Readers site. It does not imply that any related video was heard or reviewed. The site remains a static Git-to-Netlify publication with `site/` as the publish directory.

## Catalog and article inputs

Keep the normal `reader:<slug>` catalog identity, claim map, dated references, counterevidence, review and revision fields. Use this closed source variant:

```json
{
  "kind": "analysis",
  "identity": "analysis:<slug>",
  "sourceReferenceIds": ["<reference-id>"]
}
```

Every ID must name a distinct HTTPS entry in the article's `references` array. The authored `content/readers/<slug>.html` must have exactly one `<section id="sources">` containing a direct link to every declared URL. Place the generated `<!--GM_BRIEF-->` slot before the source section. The generated brief labels the first answer **What the records establish**. The page should name who should read, what to verify and what GhostMesh infers; it must label itself **source analysis** and explicitly exclude unheard speech when a video prompted the research. Claims about a source belong in dated references and the claim register. Do not use video, audio, captions, transcripts, screenshots of third-party pages, opt-in player, PDF iframe or the paper-only source fields for this type.

The shared home and archive card shows original typographic art and links to the article's `#sources` section. It does not fabricate a single external original URL. The Knowledge projection labels this type **Source analysis · public records**; it remains a source-only projection, not SharePlane or Tony Brain admission. Existing media and arXiv paper variants keep their current behavior.

## Release qualification

Source owners must supply complete approved article copy and a claim-level source dossier. A single integration writer then adds the four locked article templates, catalog records and source-grounded archive calls, regenerates `site/`, and updates the pinned Knowledge source hashes after reviewing exact published passages. Run `generate_site.py`, `knowledge_contract.py`, both `--check` modes, `check_site.py`, the Python suite, `git diff --check`, and desktop/390px dark/light/no-JavaScript visual review. Check source links, privacy, canonical URLs, receipts and all earlier Reader routes. A draft Netlify preview supports owner semantic review. A production merge requires a separate exact-head decision.

This contract branch adds no article, new permalink, catalog record or deployment by itself.
