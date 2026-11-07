# A Comma at the Handoff

A client can request extensions that a receiving agent supports, yet have those requests misread before activation.

On November 4, the A2A Go project merged a fix for a small parsing mistake. A request carrying two extension identifiers in one comma-separated value was being read as one identifier. Asking for `urn:a,urn:b` did not register a request for either `urn:a` or `urn:b`. The earlier implementation copied the incoming values without splitting them. [Affected implementation](https://github.com/a2aproject/a2a-go/blob/b82362f9ff91d5d8ce3774f429cdc771d41840c6/a2asrv/extensions.go#L64-L71)

The representation was legitimate. A2A defines its extension parameter as a comma-separated list, and its HTTP and gRPC bindings recommend combining multiple values into one field or metadata entry. [A2A specification, pinned October 30 revision](https://github.com/a2aproject/A2A/blob/4735f4876449c6f381825d8a841b31b16c6ad0c4/docs/specification.md#326-service-parameters)

That makes this more interesting than a malformed-request bug. The receiver was mishandling the form the protocol tells a sender to use.

For GhostMesh, the position is to make representation equivalence a boundary test: equivalent wire forms must produce equivalent parsed requests and activation or forwarding decisions, including intentional rejection and filtering. The concern is silent loss. A conversation can continue after an optional extension disappears, leaving its caller with no obvious sign that the requested behavior changed.

## The local test can be telling the truth

The issue report describes Go v2.7.0 handling repeated values correctly while mishandling a comma-joined value over REST and gRPC. A client and server that share the same representation can therefore agree with each other while disagreeing with the protocol. The report also identifies Python-to-Go traffic as an affected combination. That is reported reproduction evidence, not an independent test performed for this essay. [Issue 516](https://github.com/a2aproject/a2a-go/issues/516)

Even staying with one language does not eliminate the boundary. HTTP permits a recipient to combine repeated field lines into one comma-separated line when the field semantics allow it. A proxy can preserve the meaning defined by HTTP while exposing an application parser that depended on the original arrangement. [RFC 9110, section 5.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-5.3)

The ordinary deployment path becomes a test input.

## The loss continued downstream

The November 4 patch changes two places. The server parser separates the requested identifiers and trims surrounding spaces and tabs. The propagation interceptor then captures those individual identifiers, allowing the downstream client to forward the extensions the next agent supports. The required-extension check also uses the parsed list. [Merged fix, db838203](https://github.com/a2aproject/a2a-go/commit/db838203cd8561b75509c4d3e8c2b57cb4e11f1d)

This has two operational consequences worth separating.

A required extension can be rejected even though the caller requested it. An optional extension can disappear from the downstream request. The second case is easier to overlook because the surrounding conversation may continue.

Neither outcome establishes an authorization bypass. An extension request is not permission to perform an action. The narrower finding is that a system can misread the requested behavior before its policy or executor gets a useful chance to evaluate it. Whether that changes a citation, a workflow, or an audit record depends on what the particular extension does.

A confident answer from the final agent would not reveal where the request changed. Capture four separate observations for the same request:

1. The raw incoming extension parameter values.
2. The identifiers parsed as requested.
3. The extensions actually activated.
4. The identifiers forwarded to the next hop.

Support, request, activation and forwarding are different facts. Those four observations locate the transition that changed the outcome. Assessing whether filtering was intentional also requires the governing policy or a recorded decision reason. A missing identifier alone does not establish a defect.

## Test equivalent representations

The practical regression is small enough to keep.

Send the same synthetic request through the real ingress path in four forms: repeated values, one comma-joined value, mixed repeated and joined values, and joined values with spaces or tabs. Use a harmless executor that records what it receives. Repeat over every supported transport.

Then add a second agent. Give that agent support for one requested extension and not the other. Configure the same forwarding and activation policy for every representation. Verify that the allowed, supported identifier reaches it, the unsupported identifier is filtered, and an absent required extension is still rejected. A supported extension may also be intentionally declined. The invariant is equivalence of the parsed requests and resulting activation or forwarding decisions, not preservation of every requested behavior.

The upstream patch adds parser, required-extension, and propagation tests for these boundaries. [Parser tests](https://github.com/a2aproject/a2a-go/blob/db838203cd8561b75509c4d3e8c2b57cb4e11f1d/a2asrv/extensions_test.go), [required-extension tests](https://github.com/a2aproject/a2a-go/blob/db838203cd8561b75509c4d3e8c2b57cb4e11f1d/a2asrv/handler_test.go#L2300-L2335), [propagation tests](https://github.com/a2aproject/a2a-go/blob/db838203cd8561b75509c4d3e8c2b57cb4e11f1d/a2aext/propagator_test.go)

Keep normalization specific to the field. This patch is not a reason to lowercase identifiers, split every service parameter, or erase distinctions the protocol preserves.

The strongest objection is fair: this is an ordinary parser bug. Its size does not establish a broad failure of agent protocols. Its value is the concrete failure pattern. A client and server can pass a direct test using one valid representation, then behave differently when an equivalent representation arrives through another client or intermediary. That is enough reason to keep the regression without turning a comma into a security crisis.

There is also a release boundary. At the November 4 source check, the fix was merged, while the latest published Go release remained v2.7.0 from October 21. A closed issue does not establish that an installed dependency contains the change. [Fix PR](https://github.com/a2aproject/a2a-go/pull/519), [v2.7.0 release](https://github.com/a2aproject/a2a-go/releases/tag/v2.7.0)

No end-to-end deployment test or affected production system is claimed here. The source and its regression tests establish a concrete interoperability defect and correction. The proposed GhostMesh acceptance rule is narrower than universal forwarding: change the representation without changing the request, and require equivalent parsing, activation and forwarding decisions under the same policy.

Keep the comma in the test.

