# When More Agent Skills Make Agents Worse

**Reader #51 editorial working draft. NOT PUBLISHED. NOT IN THE PUBLIC CATALOG.**

Source: David Ondrej, *More skills = worse agents (do this instead)*, November 9, 2026, 42:25. https://www.youtube.com/watch?v=45-qbcAeUbM

## Thesis

The useful warning is not that an agent should have fewer skills. It is that indiscriminate skill exposure can make discovery noisier, consume context, and confuse tool selection. Total files installed, descriptors visible to the model, and skill bodies actually invoked are different variables. An agent with 100 narrowly indexed, lazy-loaded skills may be better behaved than one with ten broad, always-injected instructions. Skill-count quotas are a poor proxy for system quality.

## The argument and its limits

At [00:00](https://youtu.be/45-qbcAeUbM?t=0s), Ondrej recommends deleting most installed skills. At [01:42](https://youtu.be/45-qbcAeUbM?t=102s), he distinguishes skill descriptions from their full bodies; at [02:09](https://youtu.be/45-qbcAeUbM?t=129s), he argues that even descriptions can become costly at scale. This is a plausible mechanism, but implementation-dependent. Some harnesses discover skills through a bounded index, some inject metadata into model context, and others retrieve on demand. Counting directory entries alone cannot establish token cost.

At [03:00](https://youtu.be/45-qbcAeUbM?t=180s), he describes broad or overlapping skill descriptions. This raises a second, independent failure mode: selecting the wrong tool or skill. The causal question is whether the model sees ambiguous alternatives, not whether unused files exist on disk. Test skill-selection precision and false invocation rate rather than extrapolating from installed counts.

At [07:05](https://youtu.be/45-qbcAeUbM?t=425s), Ondrej argues for converting repeatedly performed work into narrowly useful skills. At [11:18](https://youtu.be/45-qbcAeUbM?t=678s) and [14:19](https://youtu.be/45-qbcAeUbM?t=859s), he recommends pruning infrequently used entries. Usage can inform retirement, but infrequent does not mean unnecessary: incident response, recovery, compliance and emergency procedures may be rarely invoked yet operationally essential. Remove or archive only after checking criticality, ownership and reversibility.

His examples from [14:33](https://youtu.be/45-qbcAeUbM?t=873s) onward include cross-model code review, research and conversation-state workflows. They illustrate personal practice, not a controlled comparison. The examined transcript does not establish a universal 50-skill inflection point or demonstrate that deleting 80–90% improves task success across harnesses. Product demonstrations, security claims and promotional material require separate source review before endorsement.

At [29:00](https://youtu.be/45-qbcAeUbM?t=1740s), he compares skills to standard operating procedures. The analogy works if the procedure is narrow, versioned and permission-aware. It fails when a markdown file silently grants authority, circumvents approvals or replaces an auditable execution path. A skill is a way to guide behavior, not an authorization system.

At [33:40](https://youtu.be/45-qbcAeUbM?t=2020s) and [36:56](https://youtu.be/45-qbcAeUbM?t=2216s), he turns to cloud portability and global-versus-project scope. This is the strongest architectural lesson: scope discovery to the work and execution surface. A globally advertised skill should earn its context cost and its trust exposure; project-specific instructions should not contaminate unrelated tasks.

At [39:00](https://youtu.be/45-qbcAeUbM?t=2340s), Ondrej recommends team reuse. Reuse has value only when provenance, versioning, review and ownership travel with the instructions. Copying a trusted teammate's workflow does not automatically make it safe on another machine or repository.

## Independent technical fact-check: skill loading is harness-specific

Anthropic's [Agent Skills documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) describes three levels of progressive disclosure: skill name and description are available for initial discovery, the full `SKILL.md` is read on invocation, and references or scripts are loaded as needed. This supports the distinction between visible metadata and invoked content, **not** a universal claim that every installed skill body is always in context. Its [authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) explicitly recommends precise, bounded descriptions to improve matching.

OpenAI's [ChatGPT/Codex skill authoring documentation](https://learn.chatgpt.com/docs/build-skills?product=breeze) similarly says name and description precede loading full instructions. For Codex, the initial list has a context budget, may shorten descriptions and may omit skills when the list grows. This is a concrete **discoverability** tradeoff, not proof that a larger installed catalog necessarily reduces task quality. The relevant threshold is configuration- and version-dependent; avoid turning one documented default into a universal limit.

**Fact-check verdict:** The metadata/context mechanism is supported by vendor documentation for these specific harnesses. The video's implied performance curve, the proposed 80–90% deletion percentage and any claimed universal 50-skill threshold remain **unverified**. A proper test must control the harness and its skill discovery configuration. No vendor documentation reviewed here establishes an improvement in task success after bulk deletion.

## A falsifiable engineering test

Hold model, harness, task suite, tool permissions and compute constant. Compare 5, 20, 50 and 100 skill descriptors under two discovery strategies: always-visible metadata and scoped/on-demand retrieval. Measure input tokens, selection accuracy, false invocations, latency, task completion and critical-skill recall. Include ambiguous near-duplicate descriptions and rare-but-critical tasks. Repeat trials; report distributions, not one anecdote. Do not interpret absence of benchmark evidence in the video as evidence the claim is false.

## GhostMesh interpretation

Inventory skills by **visibility**, **invocation**, **criticality**, **owner**, **trust level** and **scope** before proposing deletion. Prefer a small relevant working set, lazy discovery where supported, and reversible retirement for redundant entries. Keep rarely used recovery and regulated workflows discoverable through explicit routing. Reuse the existing telemetry and configuration rather than building a new skill-management platform.

## Evidence boundary and editorial gates

The private ReasonPack package was verified with `reasonpack verify` (exit 0). Manifest SHA-256 `0060da049408edbc81df1f6ba8e9e61f730d3e254085a1e9905c3093326551f7`; 803 machine-ASR VTT cues cover 00:00.000–42:24.560. This is source attribution, not independent audio/video validation or proof of the creator's technical assertions. Timecodes require spot-checking before publication; claims about harness internals need vendor documentation and/or direct reproducible tests. No full transcript, caption file or media belongs in the public repository.

**Pending:** technical fact-check, independently reviewed Reader and SharePlane relationships (including legitimate zero), source-map evidence, editorial/depth receipts, canonical HTML conversion, responsive preview UAT and explicit publication authorization. Do not add this draft to `content/catalog.json` or publish it before those gates.
