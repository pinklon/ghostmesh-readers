# The Approval Must Survive the Summary

*An agent that remembers the work still needs a reliable account of who may authorize it, which execution owns it, and whether it already happened.*

Consider an agent that has finished a report and asked a person to approve publication. The person has not answered. Hours later, another worker picks up the job with a shortened account of the conversation: “The report is ready to publish.”

The work sounds complete. The decision is still missing.

For anyone relying on agents to carry work across sessions, restarts or handoffs, that distinction matters. A system can remember the assignment and lose the condition that prevents it from acting. It can also lose track of the unanswered decision and leave the work stranded.

Summarizing old conversation is a reasonable way to keep long-running work manageable. The difficult part is deciding what may be shortened. An explanation can lose detail. An unanswered approval must remain unanswered, attached to the exact work awaiting a decision.

A recent OpenAI Agents SDK fix illustrates one part of the problem: an unresolved tool call caused automatic compaction to fail before an approval interruption reached the caller. The report describes an interrupted workflow, not an unauthorized action.

## GhostMesh judgment

Approval continuity belongs in the execution design. A persistent agent should be able to recover the exact pending decision, establish who may resolve it, and determine which worker may continue. A readable summary helps the next worker understand the job. Permission to act needs a trusted record that survives the handoff.

That is the practical standard we would apply before adding more persistent-agent machinery. The application also needs to retain the observed result or an explicit unknown outcome, so the next worker can establish whether the action already happened. Fluent recollection provides little comfort to an operator trying to determine whether a report went live twice.

## A small SDK fix exposes the boundary

An October 13 change to the OpenAI Agents SDK for Python provides a concrete starting point. The reported failure was automatic compaction sending an unresolved tool call to the API and receiving HTTP 400 before the approval interruption reached the caller. The pull request was merged. The documented incident concerns a failed continuation sequence; it does not establish that an unauthorized action executed. [Upstream pull request](https://github.com/openai/openai-agents-python/pull/5363)

The fix defers automatic compaction when the history selected for it contains incomplete tool exchanges. It checks ordinary tool-call pairs and approvals for hosted tools accessed through the Model Context Protocol (MCP). Hosted MCP approvals have their own request IDs; responses refer back to them with an `approval_request_id`. The patch checks that these references match before allowing compaction. [Pinned implementation](https://github.com/openai/openai-agents-python/commit/5eb47a5bdeab8ba9f6087de288c7e606816c76c6)

The patch addresses that sequencing problem. It does not establish that a generated summary will preserve the meaning of an approval. Our publication example is a hypothetical design risk, not an additional incident reported by the SDK authors.

The architectural inference is that unresolved work needs deliberate treatment at the compression boundary. A system can shorten the explanation while retaining access to the pending decision and the rules for resolving it.

## Preserve the decision the person actually made

For the hypothetical report, the retained record needs enough detail to distinguish “approve revision three for publication” from a general expression of enthusiasm. It must also distinguish an unanswered request from an approval or rejection. If the draft or requested action changes, the application has to determine whether the earlier decision still applies.

A summary can help the next worker find and understand that record. The permission check belongs to the application, using information it trusts. This is where the apparent simplicity of “save the conversation and resume it” starts acquiring responsibilities.

The SDK's human-in-the-loop guide states that restoring serialized `RunState` does not authenticate the snapshot or the reviewer. The application must establish ownership and authority, validate decisions against its trusted pending records, and coordinate an atomic, owner-checked transition before resumed execution. Possession of an identifier alone does not grant permission. [Pinned approval guidance](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/docs/human_in_the_loop.md#keep-approval-state-on-the-server)

Saving an accurate approval is useful. Checking that it came from an authorized reviewer and applies to this action is still application work.

## One approval can still produce two continuations

Now let two workers load the same paused report. Both see the same valid approval. Both are capable of publishing it.

Faithful memory has preserved the human decision, but the application still needs to decide which execution can consume that continuation. Checking that the request is pending and changing it to claimed must be indivisible from the competing workers' perspective. Otherwise both can read a valid pending request before either records that it has taken responsibility.

The upstream server-side example demonstrates consumption of a pending request within one event loop. Its documentation explicitly leaves shared storage responsible for an atomic implementation. It is an illustration of the boundary, not a deployable distributed service. [Server-side example](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/examples/agent_patterns/human_in_the_loop_server.py)

Approval determines whether the action may proceed. Claiming the continuation determines which execution may proceed with it. A persistent workflow needs to preserve both decisions.

## A crash can leave the outcome unknown

Even an atomic claim cannot guarantee exactly-once effects in an external service. A worker can consume the request, publish the report, and fail before saving the result. The SDK example leaves production recovery responsible for reconciling tool side effects before retrying. [Recovery boundary](https://github.com/openai/openai-agents-python/blob/17d994bd3045dae71acda676a4ef4762ed8ecd94/examples/agent_patterns/human_in_the_loop_server.py)

The next worker therefore needs an honest unknown state. “The process stopped” does not reveal whether publication happened. An immediate retry can duplicate the action; a permanent refusal to retry can strand recoverable work. Recovery needs to inspect the destination and decide what the observed state permits.

The record should keep the approval, continuation ownership, and execution outcome distinguishable. Each answers a question an operator may need to ask after a failure. Compressing them into one reassuring completion message makes that operator's job harder.

## The objection: how much machinery does this need?

A team trying to shorten chat history could reasonably object that this sounds like a distributed workflow project arriving through the side door. Keeping every conversation forever has costs, too. Elaborate persistence rules can consume more attention than the modest automation they were intended to support.

The SDK's local fix deserves credit on those terms. Deferring compaction around an unfinished exchange is a reasonable way to solve the reported failure. Another architecture might compact completed context while retaining pending work separately. Neither choice, by itself, establishes the rest of the application's authorization or recovery behavior.

For GhostMesh, the first step would be to inspect what the existing task and approval records already preserve. Reuse that mechanism where it can bind the decision, control one continuation, and retain an uncertain result. A new coordinator or storage service has to earn its place by closing a demonstrated gap. Define the obligations first, then choose the smallest mechanism that can meet them.

## Test the obligation through the interruption

The upstream patch includes regressions for approval and rejection, streaming and non-streaming runs, serialized resume, and later compacted replay. The compaction result is mocked. Those tests exercise sequencing and retained pairs; they do not measure the fidelity of generated summaries. [Regression tests](https://github.com/openai/openai-agents-python/blob/5eb47a5bdeab8ba9f6087de288c7e606816c76c6/tests/memory/test_compaction_model_visibility.py)

An application relying on persistent summaries needs additional checks at its own boundary. Start with a disposable fixture and a harmless publication substitute, using the existing implementation:

- Leave a request unanswered, trigger the application's compaction path, restart, and check that it remains pending.
- Where the application permits individual decisions, approve one action in a batch and check that the others remain unresolved.
- Submit an approval from an unauthorized reviewer, or attach a valid decision identifier to another owner or run, and check that the pending request remains unresolved.
- Change a material argument or revision and check that recovery cannot silently reuse an inapplicable decision.
- Let two workers attempt the same continuation and observe whether only one can claim it.
- Simulate a crash around the external action and check whether recovery preserves uncertainty until it can establish what happened.

These are proposed acceptance tests. None was performed for this essay. No installed SDK behavior, summary quality, application security, concurrency result, or recovery guarantee has been measured here.

The useful outcome would be a precise account of what the existing system preserves and where it needs repair. After the conversation gets shorter, the next worker should still inherit a decision it can check and an outcome it can account for.
