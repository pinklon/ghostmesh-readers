# The Draft Is Gone. The Edit Is Still There.

GitHub's Copilot Fusion documentation contains a small warning with a large operational consequence. Fusion may revise or discard an intermediate draft before showing the user a final response. If a discarded draft has already changed files in the workspace, GitHub says those edits are not automatically undone. The documentation tells users to review changes before committing them. This is a statement about the documented workflow. I have not tested a Fusion session or measured how often a draft leaves edits behind.

The GhostMesh verdict is that a final answer cannot be treated as a complete inventory of what an agent did. A draft belongs to the assistant's process. An edit belongs to the workspace. Discarding the first does not necessarily reverse the second. That boundary matters because the developer may see a polished final response and assume the abandoned path disappeared with it. The working tree can tell a different story.

## Where the state actually lives

The documented workflow allows Fusion to produce intermediate drafts, revise them and present a final response. That is useful when an early approach is poor. It also creates two histories: the history of what the assistant chose to say, and the history of what its tools changed. GitHub's warning establishes that these histories can diverge at least for file edits. It does not establish that every discarded draft changes files, that Fusion hides those changes, or that a particular session is unsafe. The narrower point is enough: the final response is not a rollback receipt.

Consider a hypothetical coding task. An early draft edits a configuration file. Fusion then discards that draft and arrives at a different solution. The final explanation may accurately describe the chosen solution. The configuration edit still needs to be found and judged if it remains in the workspace. A reviewer who reads only the final explanation can miss a change that was never part of the final plan. This example illustrates the documented boundary; it is not a report of an observed Fusion run.

The general failure mode is familiar beyond Fusion. We often let the story of the work stand in for the state of the work. A commit message is not the diff. A successful run is not proof that every intended effect completed. Here the conversational story is especially tempting because the product deliberately presents a refined answer. The closer that answer looks to a finished decision, the easier it is to forget that files can retain traces of a discarded attempt.

## The strongest objection

This may be ordinary development hygiene rather than a product defect. Developers already review their working tree and diff before committing. Git can show tracked changes and untracked files. GitHub's own Fusion page explicitly tells users to review changes. A team that does that reliably may catch the lingering edit without any special control.

That objection is fair. The documentation does not say Fusion commits an unwanted edit, prevents inspection or defeats version control. It identifies a boundary in automatic cleanup. The operational problem appears when a workflow implicitly treats the final response as the review surface. If a person or another agent applies the final answer without checking the workspace state, standard hygiene exists only on paper. The appropriate control is therefore modest: make the diff review an explicit acceptance step, not a new orchestration layer around every draft.

## What a review should prove

For a coding task, start with the files, not the narrative. Inspect the working tree and compare it with the expected baseline. Identify every changed and untracked file. For each change, ask which accepted requirement it serves. Review the diff and run the tests that bear on those changed paths. If a file has no place in the chosen solution, remove or revise it deliberately before committing. This is a proposed workflow, not a claim that GitHub's product performs these checks for the user.

A small reversible experiment could test the boundary in a disposable repository. Record the baseline, use Fusion on a task likely to require a file edit, and inspect the working tree after an intermediate draft is discarded. Compare the remaining changes with the final response. Repeat only enough to learn whether the team's own review process detects unexpected edits. The result would be local evidence about that setup and task, not a universal failure rate. No such experiment was performed for this article.

The useful acceptance question is simple: do the artifacts we are about to keep match the decision we believe we made? GitHub's warning says the answer cannot be inferred from draft disposal alone. The final response can explain the selected path. The workspace is where we verify its effects.

## Sources and limits

- [GitHub, About GitHub Copilot Fusion](https://docs.github.com/en/copilot/concepts/models/copilot-fusion), current documentation inspected October 29, 2026. The limitations section says discarded drafts do not automatically undo earlier workspace changes and advises reviewing changes before commit.
- [Pinned GitHub Docs source](https://github.com/github/docs/blob/6cbe6413ac7177bb692a78c171a74ae8be50d721/content/copilot/concepts/models/copilot-fusion.md), inspected October 29, 2026. The relevant file revision was committed October 28, 2026.
- [Git status documentation](https://git-scm.com/docs/git-status) and [Git diff documentation](https://git-scm.com/docs/git-diff), consulted for the proposed working-tree inspection. These sources describe Git commands; they do not establish Fusion behavior.

No Fusion session, rollback path, account entitlement, performance, security outcome or frequency of lingering edits was tested. The analysis separates GitHub's documented behavior from the GhostMesh inference and proposed review practice.
