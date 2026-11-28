# The 12 GB GPU Has a Three-Budget Problem

*Running a 27-billion-parameter model locally is possible. Buying its advertised speed and context at the same time is a different proposition.*

A 12 GB graphics card appears to have become a small miracle. One benchmark promises more than 60 tokens per second. Another demonstrates a context window above 200,000 tokens. Both involve Qwen3.8-27B. The temptation is to put the numbers together and conclude that a single inexpensive card delivers both.

That is where the reasoning breaks. The benchmarks use different quantizations, context lengths, cards, memory arrangements, and sometimes multiple GPUs. Two correct measurements do not become one valid configuration merely because they appear in the same discussion.

In *Is 12GB of VRAM Enough for Local AI Now?*, Cloud Codes asks what must fit, what must be read, and what happens when it does not. The answer is useful well beyond this particular model.

## GhostMesh assessment

The headline combines numbers from different experiments. The interesting question is what the underlying runs actually establish, and which tradeoffs a buyer must accept. The evidence deserves a closer reading.

## The reading in three questions

- **Where did the speed come from?** Start with the actual card, quantization, context depth, and measurement procedure.
- **What occupies the last gigabyte?** Model weights are only one component of the memory budget.
- **What changes when the prompt becomes long?** A context limit is not a measured guarantee of usable speed or answer quality at that depth.

## The original video

Cloud Codes, *Is 12GB of VRAM Enough for Local AI Now?*, 15:52. [Watch the original](https://www.youtube.com/watch?v=r2KBVvh_8Do). The source is an interpretive seed, not independent benchmark verification.

Source cues: [00:00](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=0s) claim; [02:16](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=136s) cache; [04:03](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=243s) capacity; [04:59](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=299s) 3080 speed; [06:56](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=416s) MTP; [08:07](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=487s) 3060 depth; [09:34](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=574s) pooled GPUs; [12:31](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=751s) sizing method; [14:17](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=857s) long context; [14:38](https://www.youtube.com/watch?v=r2KBVvh_8Do&t=878s) speed. These cues derive from source chapter metadata cross-read against captions, not independent listening certification.

## The full analysis

### Three budgets, one physical card

The first budget is **weights**. Qwen3.8-27B is a dense model, so the representation matters continuously during decoding. The Unsloth GGUF inventory lists roughly 7.21 GB for an aggressive IQ2_XXS quantization and 15.4 GB or more for common four-bit variants. Those are file sizes, not total application memory. Smaller files buy capacity by trading numerical precision; a benchmark must not treat all quantizations as quality-equivalent. [Qwen model card](https://huggingface.co/Qwen/Qwen3.8-27B) · [Unsloth GGUF inventory](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF).

The second budget is **context**. The key/value cache grows with retained tokens. Qwen's hybrid architecture keeps that growth below what a full-attention 64-layer model would require, but it does not make context free. From the maker's 16 attention layers, four KV heads, and 256-dimensional heads, a conventional 16-bit cache is approximately 65,536 bytes per token. At 262,000 tokens that is about 17.2 decimal GB before weights. Four-bit caching changes the arithmetic dramatically, to roughly 4.8 GB in the video's estimate, but implementation overhead, fixed state and buffers remain. This is derived sizing arithmetic, not a measured runtime allocation. [Qwen architecture](https://github.com/QwenLM/Qwen3.8).

The third budget is **bandwidth**. Even a model that can be loaded may decode slowly if the system cannot feed the accelerator efficiently. Offloading selected weights to system RAM can enable a long window on a smaller card, but it does not produce the same behavior as an entirely GPU-resident model. Dividing peak memory bandwidth by weight bytes estimates an optimistic ceiling, not actual tokens per second.

### Three measurements that cannot be added together

A community experiment reports approximately **9.7 tokens per second at 96K context** on a single RTX 3060 **12 GB**. It uses Q4_K_S weights, a Q4_0 KV cache, selective feed-forward tensor offload and MTP. The author's command and logs make the setup inspectable, but the result remains self-reported, not an independently reproduced GhostMesh benchmark. [First-hand discussion](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/61).

The eye-catching **64.4 tokens per second** comes from an RTX 3080 with **10 GB**, aggressive two-bit weights, a **16K** context, headless operation and MTP. The community author describes paired runs and records the artifact and backend. This proves a particular short-context configuration can be fast. It does not prove that the same speed survives a populated 262K window on one 12 GB card. In fact, that report describes a 32K setup falling from approximately 45.4 to 24.7 tokens per second as PCIe spill becomes material. [Paired community measurements](https://github.com/sudoingX/qwen38-mtp).

A **262K context** report pools an RTX 3080 Ti 12 GB with an RTX 3060 12 GB. Two cards and their arrangement change the premise. A pooled 24 GB setup must not be advertised as a single 12 GB result. [Multi-GPU configuration](https://github.com/bytefjord/qwen3.8-27b-dual-3060-12gb-llama.cpp).

### MTP is an optimization with a bill attached

Multi-token prediction uses a draft head to propose several next tokens, which the main model checks. Successful acceptance can increase output per expensive pass. But acceptance depends on prompts and configuration, the draft path occupies memory, and prompt processing can slow. The upstream llama.cpp PR's roughly 1.85-times decoding improvement was demonstrated on a Qwen3.6 setup, not universally on Qwen3.8 or every GPU. [Upstream implementation and measurements](https://github.com/ggml-org/llama.cpp/pull/22673).

The counterevidence matters. A separate two-RTX-3060 community study of Qwen3.8-27B Q4_K_M found that MTP did **not** outperform ordinary decoding in its three tested workloads, even though GPU-based MTP improved on CPU-based MTP. This does not invalidate the faster RTX 3080 result. It demonstrates why the same flag is not a transferable performance guarantee. [Independent community comparison](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/77).

### The arithmetic is a filter, not a benchmark

A quick capacity estimate is useful: identify the exact GGUF artifact and size, add a backend-specific cache estimate at the intended *populated* context, allow for draft head and compute buffers, then compare against available VRAM. A 12 GiB card is approximately 12.9 decimal GB before software and display overhead. The video's 7.27 GB tiny-weights figure differs from the current Unsloth listing near 7.21 GB; revision and file identity must be pinned before presenting a precise total.

Then ask whether any overflow crosses into system memory. Finally, measure the workload. A theoretical pass-rate ceiling cannot establish prompt-processing latency, accepted tokens per second, quality under compression, or performance near the end of a long context.

## The GhostMesh implication

GhostMesh has a different optimization problem from the video's single-budget-card scenario. A high-memory GPU lane and CPU-oriented workloads offer additional choices, but large VRAM does not settle prefill, bandwidth, model warmup, concurrency or context quality.

For image-generation prompt assistance, the relevant outcome is the time to rewrite an actual prompt while preserving intent and model-specific constraints. A CPU-only route that does not contend with a rendering GPU could be operationally preferable to a faster synthetic GPU result. That is an architecture hypothesis, not a GhostMesh benchmark.

For long-document reasoning, we need correctness at the **actual context depth**. A backend accepting a large context parameter does not prove that the model can retrieve and reason over the entire span reliably. Prefill time, source-citation accuracy, and output rate near the filled window belong in the same result.

For future multi-GPU evaluation, count pooled capacity, interconnect, layer placement and contention. Two 12 GB cards are not interchangeable with one 24 GB card simply because their installed memory sums to the same number.

### The bounded qualification

We do not need another grand qualification framework to answer this. Two matched configurations are enough to begin:

- **Speed recipe:** short, representative prompt-assist work; record the exact artifact hash, backend, context, occupied VRAM, latency distribution, sustained output and whether intent survives.
- **Depth recipe:** long-source questions with a known answer key; record context actually populated, correct citations, prefill latency, decode near the beginning and end, CPU offload and MTP acceptance.

If a smaller or lower-precision configuration completes the task with acceptable quality and less contention, use it. If more memory or precision produces demonstrably better accepted answers, that is a reason to pay for it. The recommendation follows the work, not the card's marketing label.

A reproducible single-12GB run that actually sustains both the high claimed throughput and full populated context, without hidden offload or unacceptable quality loss, would change the present conclusion. We should be prepared to update it.

## GhostMesh verdict

**Fitting a model is capacity evidence. Generating tokens quickly is performance evidence. Producing correct answers on the intended workload is qualification evidence.** A hardware decision requires all three.

The 12 GB card is not obsolete. It may be entirely adequate for a deliberately constrained inference task. But measurements taken under unlike conditions cannot be combined into a purchasing promise. The useful output of this video is a better test for the hardware we already own, not permission to buy another accelerator.

## Corroboration, counterevidence and limits

The Qwen model card establishes architecture; Unsloth publishes specific quantized artifacts. The 3060 long-context, 3080 short-context and pooled-GPU numbers are first-hand community reports. The llama.cpp pull request shows an implementation and setup-specific MTP result; another community study offers counterevidence to any universal MTP speed claim. The source video is commentary. None of these measurements has been independently reproduced by GhostMesh.

The video chapter metadata and caption-derived transcript were inspected privately. They were not independently listened through; caption errors are possible. Source media, captions, raw transcripts and local source paths are excluded from the public Reader. No private hostnames or credentials are disclosed.

## Related thinking

These are **editorial comparisons, not source corroboration**:

- **The Model Fits. Does the Intelligence Survive?** Compression and capacity are not the same as useful model quality.
- **The Operator Is Part of the Denominator.** Service latency and workload conditions matter more than a peak token figure.
- **The Engine Is Not the Service.** A fast decoding engine is not the whole inference service.

## SharePlane Work comparison

**The Most Expensive Model Is Often Compensation for Missing Control.** This Work challenges the reflex to buy bigger compute when the surrounding architecture or workload definition is weak. Reader #59 supplies a concrete hardware-sizing example of that broader decision error. This is a conceptual comparison, not empirical proof. https://shareplane.malott.ai/artifacts/the-most-expensive-model-is-often-compensation-for-missing-control/
