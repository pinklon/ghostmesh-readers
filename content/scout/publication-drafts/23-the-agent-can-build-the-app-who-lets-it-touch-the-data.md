# The Agent Can Build the App. Who Lets It Touch the Data?

*Scout editorial draft | November 6, 2026 | Not approved for publication*

An AI agent can now create a small application inside a data platform, attach existing queries, and put a working interface in front of a person. That is useful. It also changes the question an operator has to ask. Once an agent can assemble the interface, who decides which data operations the application is permitted to invoke?

The November 4 pre-release of `datasette-apps` 0.3a0 offers a concrete example. Datasette Apps hosts custom HTML applications inside Datasette, with Datasette Agent helping people create and edit them. The release adds tools for assigning stored queries to apps and requires a user decision before granting write-capable queries. It also checks that a requested query exists and is visible to the acting user. These are specific product changes, not a demonstration that agent-built applications are safe in every configuration. [Release 0.3a0](https://github.com/datasette/datasette-apps/releases/tag/0.3a0)

## GhostMesh judgment

**Generating an application must not grant it authority over the data behind it.** An agent may propose an interface and request a capability. The application must independently bind that capability to the actual user, the actual resource, and the particular operation. The visible approval step matters, but the enforcement point and the scope of the grant matter more.

This is not an argument against agent-generated software. It is an argument for separating authorship from authority. A helpful agent can produce an app quickly; it should not be able to turn the app's existence into permission to run a write query or access a dataset the user cannot see.

## What the release actually changes

The upstream pull request describes two new agent tools: one adds stored queries to an existing app, and one removes them. An addition first requires permission to edit the app, validates each named query, and checks the actor's permission to view it. Read-only queries can be granted immediately. New write-query grants pause for one user approval covering the call; the prompt identifies the application and shows the SQL involved. If the user declines, the call is cancelled and the agent is instructed not to retry without a new request. If interactive approval is unavailable, the agent path returns an error directing the user to the ordinary edit interface. [Implementation PR #43](https://github.com/datasette/datasette-apps/pull/43)

That same change applies validation to app creation. Previously, the agent path could accept stored-query strings without that validation. The pull request reports tests for pending, accepted and declined decisions, invalid and inaccessible queries, permission checks, and a real `ToolContext` question/resume sequence. The merge page reports 16 passing checks. These are upstream development receipts, not independent tests performed by GhostMesh. [PR #43](https://github.com/datasette/datasette-apps/pull/43)

There are two particularly sound details. First, the write grant does not partially save the read-only grants in the same call while the approval is unanswered. Second, changes are recorded through the app registry's revision path. Those choices reduce ambiguity about what was authorized and what state was actually changed. They do not, by themselves, settle all questions about later execution or revocation.

## Approval is a transaction boundary, not a decorative dialog

Imagine an agent building a quality dashboard for a laboratory team. Reading a qualified metrics query and issuing a corrective update are materially different operations. A single natural-language instruction to “make the dashboard useful” does not carry an unambiguous grant for both. The application needs to identify the proposed write operation and ask the authorized person before granting it.

The harder requirement comes after the dialog. A permission decision should apply to a defined app, query, actor and version of the request. If the query changes, the app is shared, or a different viewer runs it, execution-time policy still needs to govern what can happen. The upstream description explicitly warns that an app executes stored queries with the viewer's permissions. That is a useful boundary: the app's grant does not become an unrestricted service identity. It also means operators must understand the difference between *an app is allowed to call this query* and *this viewer is allowed to execute it*. [PR #43](https://github.com/datasette/datasette-apps/pull/43)

For a regulated workflow, the design questions grow sharper: Was the write approved for this purpose? What record identifies the approver and query revision? Can permission be withdrawn? What happens if an interrupted agent resumes the approval request? What does the audit trail prove about actual execution? Those are evaluation questions here, not claims that this Datasette release fails them.

## The useful limit in the upstream evidence

The pull request expressly excludes two areas from its new approval behavior. `app_create` still does not validate `sql_databases`, and grants involving `sql_databases` or `csp_origins` do not use this approval prompt. That does not establish a vulnerability. It establishes the *scope* of the change: the new safeguards concern stored-query grants, not every capability an agent-built app may request. [PR #43, “Not in this PR”](https://github.com/datasette/datasette-apps/pull/43)

That boundary is more instructive than an exaggerated security headline. Product teams should inventory capabilities separately: viewing queries, granting stored-query access, changing app settings, broad database access, external-origin behavior, and actual writes. Different operations may need different controls. A passing test for write-query approval should never be summarized as “all app authority is approved.”

## The objection: why not simply trust the user's session?

For a small, local, low-risk tool, a team may reasonably prefer fewer prompts. If the user already has permission to execute a read-only query, requiring another approval every time an agent attaches it to a private app could add friction without materially reducing risk. Datasette's distinction between ordinary read grants and write grants reflects that tradeoff.

But the user's session alone does not answer which capabilities the generated app should retain, how they change over time, or whether a shared app should expose the same operations to someone else. App-level scope and viewer-level permission serve different purposes. Keeping both explicit makes the system easier to reason about without introducing a heavyweight approval ritual for every harmless action.

## What GhostMesh should learn

The reusable pattern is simple: let the agent assemble the proposed artifact; validate resource identity and current rights at the boundary; require a specific human decision for consequential new capabilities; commit the permitted state as an auditable revision; and enforce viewer permissions when the capability is exercised.

A practical independent test would attempt an ordinary read grant, an unapproved write grant, a declined write grant, a modified query after approval, an inaccessible query, and a grant through an unsupported approval surface. The expected results should be specified before testing. We have not run those tests against Datasette Apps, and this article makes no security-certification claim.

The broader point is that agent development speed is real value only when permission remains comprehensible. **An agent can write the interface. It should not get to write its own authority.**

## Follow the thinking

These links connect distinct arguments. They are not independent corroboration of Datasette's implementation.

- **Policy parallel: [Assisted permissions and the meaning of human approval](https://youtube.shareplane.malott.ai/scout/essays/assisted-permissions-and-human-approval/).** The earlier Scout essay asks whether an `ask` rule still means human approval when an AI system can decide that a request is safe. This piece examines a narrower product boundary where a write-query grant expressly pauses for a person. Both concern the semantics of delegated authority, but the products and evidence differ.
- **Architectural extension: [The Approval Must Survive the Summary](https://youtube.shareplane.malott.ai/scout/essays/the-approval-must-survive-the-summary/).** The November 3 essay explains why a pending decision, its authorized resolver, and continuation ownership must survive agent handoffs. This Datasette analysis raises the same continuity questions when app permissions are requested, declined, or later revised. It does not assert a compaction or recovery defect in Datasette.

Publication projection requirement: show these two relationships visibly in the article's related-reading section, record their distinct types and rationale in the Scout relationship graph, and verify both target URLs. Do not add a link merely because it shares a keyword.

## Primary sources and evidence limits

- [Datasette Apps 0.3a0 release](https://github.com/datasette/datasette-apps/releases/tag/0.3a0), November 4, 2026.
- [Datasette Apps PR #43](https://github.com/datasette/datasette-apps/pull/43), merged November 4, 2026; design, tests, explicit exclusions.
- [Simon Willison's release note](https://simonwillison.net/2026/Nov/4/datasette-apps/), November 4, 2026.

Source-based editorial analysis only. No local installation, runtime experiment, penetration test, or independent validation of the upstream passing checks. Hypothetical laboratory examples illustrate design consequences, not observed incidents.
