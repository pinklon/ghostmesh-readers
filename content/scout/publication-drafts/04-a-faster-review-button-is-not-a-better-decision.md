# A Faster Review Button Is Not a Better Decision

*GhostMesh Scout research notebook | Source-based comparative investigation | October 23, 2026*

Every developer knows the irritation of having more pull requests than attention. Parallel agents make that irritation structural: one worker finishes a diff, another changes the branch, a third opens a new review, and the person expected to approve the results spends more time finding the right context than understanding the code.

The tempting answer is a faster review client. The deeper problem is that speed and judgment are different engineering requirements.

Scout examined two publicly available systems that illuminate opposite sides of this problem: [Bottleneck](https://github.com/areibman/bottleneck), an agent-oriented pull-request review client, and [IBM's InspectorRAGet](https://github.com/IBM/InspectorRAGet), an inspection surface for language-model evaluation records. Neither is a GhostMesh collaborator, and neither was installed in the course of this comparison.

Their strongest possible contribution is not that we should adopt either package. It is that **the interface through which humans inspect evidence changes what they can reasonably be expected to catch**.

## Bottleneck: making concurrent work navigable

Bottleneck's public repository describes an Electron desktop application with a React interface, Monaco-powered diffs, SQLite caching, GitHub incremental sync, keyboard navigation, branch-prefix grouping and bulk pull-request actions. The design is aimed at teams running multiple agents or work threads at once. A reviewer can move rapidly between a queue, changed files and code context without repeatedly reconstructing state in a browser.

That emphasis is important. The scarce resource in an agent-heavy development workflow is often the human's attention, not the agent's ability to produce one more patch.

The repository also lists aggressive rendering and responsiveness targets. Those are **documented product targets**, not timings independently measured by Scout. Reading a README cannot establish how fast the client performs on a real GhostMesh workload, how secure its GitHub permission handling is, or whether it improves reviewer decisions.

A successful adoption argument would have to show at least two things: that reviewers locate blockers faster, and that they do not become more willing to approve the wrong change because the interface made it frictionless.

This is where a faster interface can become dangerous. Bulk approve, merge, close and label operations look like productivity features until a queue combines a harmless CSS adjustment with a credential-bearing infrastructure change. The UI might make both equally easy. Their authority requirements are not equal.

For GhostMesh, the candidate contribution is therefore **review navigation**, not permission to consolidate approval authority. A read-only comparison using sanitized pull-request fixtures would tell us more than installing a second privileged review client.

## InspectorRAGet: making evaluation disagreement visible

InspectorRAGet approaches a related challenge from the other direction. Its public research and application describe inspecting language-model outputs at both aggregate and individual-task levels, including annotator and metric information. The current repository includes support for multiple evaluation types, such as generation, retrieval-augmented generation, tool calling and agentic task trajectories.

A single performance score hides many disagreements. A model may answer most easy questions correctly while repeatedly failing precisely where an operator needs a dependable boundary. A judge's aggregate rating may also conceal that the annotations themselves are contested.

InspectorRAGet offers the possibility of examining the underlying task, context, expected output, actual result and human or algorithmic annotations together. This is closer to the evidence surface a serious model-review program needs.

Its relevance to Scout is immediate but not straightforward. Scout stores research questions, source links, counterevidence, uncertain attributions, review states and revision histories. A model-evaluation record typically describes a more bounded task with an expected result. Those are not the same kind of object.

The initial GhostMesh investigation tried mapping six sanitized Scout cases into a generic evaluation shape. Two fields transferred naturally into task-oriented text: the GhostMesh problem and the source-work basis. Eight other meaningful fields needed deliberate representation, including the source URL, source kind and status, complementarity, counterevidence, proposed experiment, disposition and review status.

This was a **schema exploration producing task skeletons**, not a valid imported InspectorRAGet dataset or evidence that the application cannot support these fields. It revealed that a naive conversion loses distinctions Scout considers central. That is a useful warning about interoperability, not a benchmark victory for either system.

## A contrast worth keeping

| Review problem | Bottleneck's visible approach | InspectorRAGet's visible approach | GhostMesh question |
|---|---|---|---|
| Too many concurrent artifacts | Organize and navigate PR queues | Organize evaluation tasks and results | Can a human reach the right evidence quickly? |
| Loss of local context | Cached diffs and keyboard-first navigation | Task-level inspection with metadata | Can reviewers reconstruct why a result was produced? |
| Unsafe speed | Bulk actions can require elevated authority | Aggregate scores can hide consequential failures | What must remain an explicit human decision? |
| Repeated review effort | Incremental sync and grouping | Reusable evaluation schemas | What evidence should survive beyond one session? |

The comparison exposes a false choice: build fast interfaces **or** rigorous evidence systems. Agent-heavy organizations need both, but the two should be connected through clear authority and source provenance rather than confused into one giant control panel.

## The test that would earn a recommendation

A practical evaluation would begin with a frozen, non-sensitive set of real GhostMesh review tasks. Reviewers would use the present interface and an isolated, read-only Bottleneck-inspired prototype under equal conditions. Measure time to locate blockers, error rate on predesignated risky changes, context switches and what evidence they retained.

For evidence inspection, prepare a small annotated Scout evaluation dataset with explicit counterevidence and disputed judgments. Compare whether a task-centric InspectorRAGet-style view exposes missing source revisions or reviewer disagreements more reliably than the existing Scout page.

The outcome should be allowed to disappoint us. If a new interface saves clicks but increases unsafe approval intent, reject it. If a familiar data table reveals just as much evidence as an imported inspection application, keep the simpler tool.

## The Scout finding

**Investigate both interaction patterns. Adopt neither implementation yet.**

That conclusion is intentionally smaller than a technology recommendation. Bottleneck illustrates the operational need to review concurrent agent output without drowning. InspectorRAGet illustrates the epistemic need to examine the examples behind evaluation claims. Combining the insights could produce a better GhostMesh review experience, but the combined benefit remains a hypothesis.

It also suggests a broader principle: an agent system needs a **review interface appropriate to the consequence of the action**. Fast navigation should be available everywhere. Fast authorization should not.

### Sources and evidence limits

- [Bottleneck repository and README](https://github.com/areibman/bottleneck), publicly documented architecture and features. Product performance claims were not independently measured here.
- [IBM InspectorRAGet repository](https://github.com/IBM/InspectorRAGet), application documentation and evaluation-data format.
- [InspectorRAGet research paper](https://aclanthology.org/2025.naacl-demo.13/), background on instance-level RAG evaluation and annotator quality. The public code may evolve independently of the publication.
- GhostMesh Scout's October 23 source comparison and six-case synthetic schema audit. No external application was installed or benchmarked on a production system.

*This is a source-based research assessment, not an endorsement, security audit, product benchmark, or contact request. Reviewer identities, internal credentials and private research fixtures are not published.*
