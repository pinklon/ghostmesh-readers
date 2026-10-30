# Qualifying a Connected Apps integration before building it

**Source-based analysis; no integration tested**
First observed October 29, 2026 · Sources rechecked October 30 · Announcement: October 28

Google's Connected Apps preview offers a shared route into Search and the Gemini app through remote MCP or Android AppFunctions, with registration, testing and submission in a common console. Access is opening in phases; the announcement does not establish admission for a particular developer. [Google's announcement](https://blog.google/innovation-and-ai/technology/developers-tools/connected-apps-one-place/)

For an agent-platform team, the interesting question is not just whether its server speaks MCP. It is **whether the service, the declared tools, the account permissions and the action the user expects describe the same boundary.** Passing a protocol check would answer only part of that question.

The useful pre-build artifact is therefore a small integration contract: a record of what is being offered, under whose authority, and how that offer stays true when the implementation changes. This is a proposed review method, not a Google requirement or a tested integration recipe.

## Start with the service, not the adapter

Google's policy prohibits apps primarily passing through third-party APIs that the developer does not own, manage or have explicit proprietary rights to. It separately permits third-party APIs supporting a larger proprietary service. [Connected Apps policy](https://developers.google.com/connected-apps/connected-apps-policy)

That distinction changes the first design question. A tool inventory explains how an adapter works; it does not explain what service the developer is providing. Start with one paragraph describing the service's own function, the records it controls and which external APIs merely support it. If the paragraph is just a list of systems it relays, adding better schemas will not resolve the admission question.

This is not an eligibility ruling on any product. The point is sequencing: establish the service proposition before investing in its distribution adapter. A plausible technical integration can still be the wrong product submission.

## A tool snapshot is not a server revision

The registration guide describes versioned tool snapshots, a new app version for published-definition changes, and a per-tool confirmation setting preselected for destructive annotations. [Registration guide, steps 6–7](https://developers.google.com/connected-apps/gpc/perform-the-steps)

Our inference is that the reviewed declaration and the running implementation are different evidence objects. A frozen description does not, by itself, prove that code behind a URL cannot change. The contract should identify both the declared tool version and the service revision intended to answer it. A change in side effects matters even if the tool name and input schema stay the same.

The same separation applies to permission. Account linking answers who has delegated access; it is not a complete description of which individual operation should require confirmation. For a hypothetical task service, reading status and changing status could share an account while having different consequences. The proposed contract should make that difference visible without depending on a reviewer to infer it from a tool name.

## Narrow the OAuth uncertainty rather than declaring it solved

The October 28 registration guide's user-delegated path offers pre-registration or automatic registration, checking Client ID Metadata Documents (CIMD) before falling back to Dynamic Client Registration (DCR). [Registration guide, step 4](https://developers.google.com/connected-apps/gpc/perform-the-steps)

The September 14 OAuth guide still says its discovery JSON needs a `registration_endpoint` even when CIMD is supported. Elsewhere it permits manually supplied client credentials and refers to Play Console. [OAuth guide](https://developers.google.com/connected-apps/mcp/oauth)

Two additional checks sharpen the reading. Google's October 27 troubleshooting page recognizes CIMD and DCR alternatives and points unsupported providers toward static credentials. The MCP client-registration specification linked by the newer guide distinguishes the mechanisms and puts CIMD ahead of DCR when pre-registered information is unavailable. Neither source proves what Google's deployed client accepts. [Google troubleshooting](https://developers.google.com/connected-apps/gpc/troubleshooting), [MCP client registration](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration)

The most plausible reading is that documentation scopes or generations have not been fully reconciled. That is an inference, not a confirmed migration history. The precise unresolved question is: **in Connected Console's automatic user-delegated path, can a CIMD-capable authorization server omit a DCR registration endpoint?** The newer guide supports that interpretation; the older OAuth error guidance cuts against it. A newer date alone cannot settle actual behavior.

This does not make every authentication choice uncertain, and it is not evidence of an authentication vulnerability. It is a bounded compatibility question to resolve before selecting a CIMD-only implementation. A Google clarification identifying the applicable path, or a separately authorized observation of that path, could settle it. Neither was obtained here.

## The strongest objection: this could duplicate the platform's work

A common console and protocol are valuable precisely because developers should not have to invent a new governance system for every client. If this method turns into a large architecture exercise before a small preview experiment, it will consume the benefit it is meant to protect.

The answer is to keep the contract small and decision-oriented. Do not use one documentation inconsistency as a reason to reject the platform. Use the sheet to identify what would change the build decision: an unsuitable service proposition, an unexplained action boundary, an implementation change hidden behind a stable declaration, or an authentication dependency whose support remains unknown. None of those is established merely by completing the sheet; the sheet makes the assumptions inspectable.

## One practical test: proposed, not performed

Use two hypothetical tools: one reads an owned task-status record; one changes that record. Prepare a single page with one row per tool and these fields:

- The owned service function and supporting external dependencies.
- The minimum data and account authority the operation needs.
- Its intended effect and the point at which a person should confirm it.
- The declared tool version and intended server revision.
- The chosen authentication path, with the CIMD-only question marked unresolved if relevant.

Give the page to a second reader without the adapter design. Ask them to describe the permitted read, the permitted change, what requires confirmation, and which change would trigger another review. Record every place they need to guess.

**Pass condition:** the reader can distinguish the two operations and their review boundaries from the page alone, while identifying unresolved assumptions as unresolved. **Failure condition:** they must invent a permission, side effect or version relationship. Revise the contract rather than reporting a successful integration. Even a passing paper review would show only that the description is legible, not that Google accepts it or that the service enforces it.

This exercise has not been performed. It needs no deployed endpoint, credentials, account linking or API calls. No console session, service code, authentication flow, enforcement or interoperability was tested. Sources were checked in their current public form; original documentation publication dates and immutable revisions were not established. The conclusion is a pre-build review method with one explicit compatibility question, not a claim of eligibility, safety or operational readiness.
