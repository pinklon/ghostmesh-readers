# What Survives a Checkpoint

A workflow pauses on Friday. On Monday, it resumes from the right checkpoint, with the right task identifier and the expected state. Somewhere between those two events, somebody changed the prompt, replaced the retrieval index, or deployed a different implementation behind the same tool name.

Nothing in that hypothetical requires a broken database. The saved state can be perfectly intact while the meaning of the next operation has changed.

That is a useful place to begin an argument about agent continuity. Before adding another coordinator, determine what the existing system actually preserves. A position in a workflow is one answer. The conditions under which its intermediate conclusions remain usable are another.

The practical question is smaller than “Which durable runtime should we adopt?” It is this: which dependencies must remain compatible when work continues, and which decisions must be made again?

## The code on Monday

LangGraph documents a particularly clear boundary. Its latest deployed graph applies to existing threads, including those resumed from checkpoints. Graph topology is not saved with the checkpoint. Its compatibility guidance proposes recording a `flow_version` in state when old and new threads should follow different branches. That preserves an intended routing distinction; it does not automatically freeze remote resources. The illustrated node bodies are stubs, not evidence of a fully executed application. [1]

Current source corroborates the narrower claim. The loop supplies its node definitions alongside checkpoint state when preparing tasks. Task preparation resolves the named process and passes that process's node into the executable task. This was static inspection of a pinned revision, not a restart experiment or a finding about any deployed installation. [2]

Consider a hypothetical document-review agent. Its saved notes say a passage satisfied rubric version one. After a deployment, its next step uses rubric version two to combine those notes into a recommendation. Perhaps that is exactly what the owner intended. Perhaps it creates a recommendation whose parts were judged by incompatible standards. Successful continuation alone cannot decide between those possibilities.

The design needs an explicit answer. Reuse the old judgment, recompute it under the new rubric, or stop because the available versions cannot be combined. Leaving that choice implicit does not remove it. Deployment timing then determines the choice.

## The interesting result favors the smaller solution

The August preprint *BEGIN AI TRANSACTION* studies semantic consistency across durable AI workflows. Its proposed SemIso mechanism addresses changing versions, incompatible dependencies, lost child constraints and incompatible branch merges. The controlled comparison contains a useful restraint: static pinning and SemIso both prevent all four tested closed-world anomalies. Static pinning fails a late-discovery case when a dependency was not bound; predeclaring both possible tools succeeds. [3]

Those are author-reported results, not independently reproduced observations here. The study used LangGraph 0.6.7 and Qdrant 1.16.1. Its source audit found four exposed workflows among 54 durable workflows examined, not four demonstrated production incidents. Compatibility remains declared rather than inferred. External writes and effects are outside the established protection. [3]

The inference is that the first implementation decision should depend on whether the dependency set is actually open-ended. A research lane with a known reader, a known scoring rubric and a known output schema may need a small inherited manifest. A lane that discovers arbitrary tools halfway through its work presents a different problem.

Calling both situations “agent orchestration” hides the difference that determines the amount of machinery required.

There is an ordinary precedent for explicit dependency accounting. DVC's lockfile records resolved dependencies, parameters and hashes so that changes can invalidate previous work. That is not an agent-control solution, and installing DVC would not establish authorization. It does demonstrate that a useful answer can begin with an inspectable artifact rather than a new service. [4]

## Permission has to stay live

A proposed manifest should distinguish three things: the identity of a dependency, the compatibility claim that permits reuse, and the authority to perform the next action.

The first two can sometimes be preserved. Authority must be checked again when the task resumes.

Suppose a paused task retains an old model revision and an old document-classification rubric. Keeping those stable may be appropriate for comparison. If access to the document is subsequently revoked, the earlier task state must not become a reason to continue accessing it. If publication permission is withdrawn, a reproducible draft remains an unauthorized publication.

This is a proposed safety boundary, not a capability demonstrated by the sources above. Evaluate current authorization before the protected action. Preserve historical inputs only where retention and reuse remain permitted. Record the distinction clearly enough that an operator can tell “the result is reproducible” from “the action is currently allowed.”


## The objection is real

Freezing dependencies has costs. It can retain a known defect, strand work on unavailable versions, or force unnecessary restarts when a harmless change occurs. A manifest also cannot make an opaque provider's mutable alias immutable.

Temporal supplies an important counterexample to any universal claim about resumed code. Its Worker Versioning documentation supports pinning workflow executions to a Worker Deployment Version, alongside auto-upgrading behavior. It also acknowledges the burden of retaining worker versions for long-running executions. Code pinning is therefore a real option with an operating consequence, not a promise that every external resource has been preserved. [5]

For the proposed smaller approach, compatibility declarations are the difficult part. Somebody must define which changes invalidate an intermediate judgment. A checksum can show that bytes changed. It cannot, by itself, decide whether a revised rubric makes yesterday's conclusion unusable.

The honest alternative may sometimes be recomputation. If a report is inexpensive to regenerate and its dependencies change frequently, restarting from a clean input can be easier to inspect than maintaining a growing compatibility policy. That is a hypothesis to measure, not a claim that recomputation is always cheap.

## A bounded experiment

The experiment below has not been performed. Before adding a resolver, use a small offline continuation fixture with synthetic documents and deterministic tool substitutes. No paid model calls, new controller or production changes are needed for the proposed test.

Start with a fixed reader revision, rubric and output schema. Pause after collecting intermediate judgments. Change one dependency to an incompatible revision, then resume. Compare the existing behavior with a variant that inherits a small manifest through child work and checks it before combining results.

Add two controls. First, introduce an undeclared dependency after the pause. The system must identify that it lacks a compatibility decision rather than silently blessing the new dependency. Second, revoke a synthetic grant after the pause. Both variants must refuse the protected action, regardless of whether their semantic inputs match.

Record incompatible outputs, justified stops, legitimate continuations incorrectly blocked, and the time required to prepare and recover each case. Also compare clean recomputation. No improvement, effort reduction or waiting-time benefit is measured yet.

The simpler approach loses if necessary dependencies cannot be identified or retained, if compatibility checks repeatedly prevent useful work, or if dynamic discovery is essential rather than incidental. A larger mechanism earns consideration when the test demonstrates that boundary.

A checkpoint is useful because it lets work continue. The next engineering decision is to specify what may change while it waits.

---

## Evidence and provenance register

1. **LangGraph compatibility documentation.** [Pinned source](https://github.com/langchain-ai/docs/blob/4506df5fb4105a39b84c2b7390d21bed89e28668/src/oss/langgraph/backward-compatibility.mdx). Repository revision October 23, inspected October 25. Documented behavior; page existed before this research pass, not a new October feature.
2. **LangGraph implementation.** October 25 revision `a25bfafe4858d2a85bede09ba83f9a591d1f1133`: [loop](https://github.com/langchain-ai/langgraph/blob/a25bfafe4858d2a85bede09ba83f9a591d1f1133/libs/langgraph/langgraph/pregel/_loop.py#L662-L672) and [task preparation](https://github.com/langchain-ai/langgraph/blob/a25bfafe4858d2a85bede09ba83f9a591d1f1133/libs/langgraph/langgraph/pregel/_algo.py#L592-L735). Static inspection only.
3. **Barzan Mozafari, BEGIN AI TRANSACTION.** [Version 1, August 5, 2026](https://arxiv.org/html/2608.05412v1). Preprint, controlled experiments and source audit. No independent reproduction or runnable artifact established in this pass.
4. **DVC lockfile documentation.** [Primary documentation](https://doc.dvc.org/user-guide/project-structure/dvcyaml-files), retrieved October 25. Rendered source unpinned; precedent only.
5. **Temporal Worker Versioning documentation.** [Pinned October 23 repository revision](https://github.com/temporalio/documentation/blob/013b6f8b13f0613056250b17a5034960b3a440ae/docs/production-deployment/worker-deployments/worker-versioning/index.mdx). Documented operating model, not a deployment inspected here.
