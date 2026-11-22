# Scout Connection Thesis: independent comparison trial v0

Status: research-only, unscored. This is a reviewer packet, not an evaluation result.
Prepared: 2026-10-23. No outreach, publication, merge, or scheduling authority.

## Purpose

Test whether an independent reviewer can distinguish promising complementary work from merely adjacent work, without popularity-based cues or prior Scout recommendations.

## Candidate intake

Evaluate the six source URLs in `research/scout-connection-blind-set.json`. The identifiers and ordering are opaque. Every entry came from a topic-directed web discovery query; this is **not** a randomly sampled internet population. No candidate is declared a positive or negative ground truth. Read the primary artifacts directly, not merely search snippets. Capture source revision/date and mark inaccessible evidence UNKNOWN.

## Reviewer procedure

1. Before seeing Scout's existing recommendations or earlier narrative, record the fixed GhostMesh need: authorized continuation of agent work, provenance of actions and claims, model interchangeability, human review, and reliable recovery.
2. Evaluate each source against the same five dimensions, 0-2 points each: original technical contribution, inspectable evidence, relevance to a concrete GhostMesh gap, *complementarity* rather than duplication, and falsifiability of a proposed joint experiment. A zero means absent or unsupported, not proven failure.
3. Record the strongest disconfirming argument, one concrete experiment, whether a suitable public collaboration interface is evidenced, and the exact supporting source sections. If evidence is missing, use UNKNOWN and do not impute zero.
4. Assign ARCHIVE, FOLLOW, INVESTIGATE, or CONSIDER_INTRODUCTION. An introduction is an editorial suggestion only; outreach_authorized remains false.
5. After submitting frozen ratings, separately reveal the earlier Scout recommendations and identify disagreements. Report disagreements without forcing consensus.
6. Repeat with a second independently selected discovery pool, including material outside the agent-continuity domain. Do not claim accuracy without a preregistered ground-truth process, negative controls, and independent judges.

## Review record schema

One record per candidate: id, captured_source_revision, captured_at_utc, evidence_urls, independent_rater_id, original_contribution_0_to_2, evidence_0_to_2, relevance_0_to_2, complementarity_0_to_2, falsifiability_0_to_2, unknown_dimensions, strongest_objection, proposed_experiment, connection_interface_evidence, recommendation, outreach_authorized=false.

Do not embed personal contact details, private direct messages, full transcripts, or speculative claims about maintainer motivations.

## Interpretation

A high score means priority for further technical reading, not confidence in a person's character, availability, or willingness to collaborate. Compare rank stability and disagreement rates only when actual independent ratings exist. No precision, recall, calibration, or collaboration conversion is measurable from this packet.

## Scope and rollback

This packet and its JSON intake are additive research files only. No imports into the live weekly Scout, no changed ranking, no scheduler, no Netlify exposure, no outbound contact. Rollback is removal of these two draft-only files before merge. The draft PR stays unmerged pending owner choice.
