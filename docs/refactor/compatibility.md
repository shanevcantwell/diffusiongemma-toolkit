# Common-boundary compatibility record

Status: **Phase A authored for review, 2026-09-16. Phase B NOT IMPLEMENTED.**
[Manifest](manifest.json) · [contracts](contracts.json) · [gates](gates.md) · [ledger](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3).

## The cut, not a new engine

Only the 30 names in `contracts.json.exports` are proposed public root `dgemma` exports. Existing 16 root exports remain; additions are justified by actual adapter calls, constructors, returned payloads, or nested canonical payload vocabulary. Engine-test imports alone confer no public status. `Provenance` and `EditOp` describe returned KV payloads; exporting them does not implement surgery. `QUANT_CHOICES` aliases `model._QUANT_CHOICES`, with no internal rename. `KNOB_DOCS` remains the native dictionary.

Already typed native functions and classes are directly re-exported. This structurally preserves function/class identity, ordered signatures, parameter kinds, defaults, annotations, `__module__`, exceptions and native duck typing. An `_api.py` forwarding wrapper would duplicate signatures and alter callable identity without an adapter need. It is not required by “thin delegates where necessary.” Definitions stay in place; no intermediate directory moves. `dgemma.model`, `.loop`, `.types`, `.payloads` and other implementation modules remain private, even though importing the root loads them transitively. This is an intended contract for B, not a stable API delivered by A.

## Preserved native behavior (B02/B03, V02)

| Capability | Invariant and actual owning code |
|---|---|
| Load | `model.load_model` returns native `DGemmaModel`. Keep quant selection/defaults, placement, dependency guards, auto-round regex patch, warmup bypass and tied-weight guards. Four interrupt phase polls raise canonical `LoadInterrupted`; blocking calls are not made preemptible. |
| Generate | `loop.run_diffusion` returns `(str, CanvasState, CanvasTrace)` without JSON/tensor conversion. Fresh scheduler, pipeline, collector, composite and participants each run; persistent model belongs to caller/adapter. Root re-export introduces no new validation. |
| Ingress | `ingress.validate_ingress`: constraints, control signals, capture, then hook-source rejection. Duck-typed payloads accepted by native validators stay accepted. Public constructors retain actual field order/defaults/frozen flags; they do not replace ingress checks. |
| Cancellation | `StepEndComposite`: capture before cancellation before writers. Internal `DiffusionCancelled` becomes a normal partial native tuple. Preserve no-frame guards. MCP event registry and Comfy interrupt predicate stay adapter-owned. |
| Observe | `on_frame(frame)` runs every captured step independent of retained-frame policy; callback exceptions propagate. Tier-2 streaming sees live distributions; retention budget limits stored copies. `CaptureSpec.keep_frames` is validated but does not override `run_diffusion(keep_frames=...)`. |
| Hook | Signature keeps `logit_hook`, but native ingress rejects any non-None caller value. Constraints may install the native internal hook; context manager removes it on normal, cancellation and error exits. Do not advertise an enabled arbitrary-hook API. |
| Encode | `encode_sequence` uses raw token IDs, encoder parameter device and `torch.no_grad`. Empty IDs raise ValueError. New KV wrapper/geometry/provenance does **not** mean a cloned underlying cache. `into` is not revalidated by encode itself. OOM is enriched and re-raised as native `torch.OutOfMemoryError`. |
| KV | `KVCache`/`Provenance`/`EditOp` remain canonical. Native ingress order V1→V2→V4→V3→V6→V5→V7 stays unchanged. Composed prompt prefill can mutate the supplied live cache; V7 rejects stale minted lengths. No clone, ownership transfer or persistence feature added. |
| Fingerprint | Actual `tokenizer_fingerprint(dgemma_model)` is `f"{repo_id}:{vocab_size}"`, with processor/tokenizer fallback and `None` when vocab size absent. It is not a vocabulary hash. |
| Decode | `decode_frames` returns raw frame strings in order, skips special tokens, does not trim EOS or excise thought channels, selects example zero for 2-D tensor canvases, and returns `[]` for no frames. Final-answer decoding is a separate native path. |
| Telemetry | Native frame/state/trace fields retain absence-vs-zero semantics, scheduler identity/config and per-example commit fractions. Scalar `committed_fraction` raises for batch size other than one. No serialization at root. |

Exact AST-normalized signatures, fields, constants, explicit raise expressions and consumer-use locations are sharded from [contracts.json](contracts.json). Raise inventories identify scope: an internal helper's error is not a new root symbol, and dependency/callback errors cannot be exhaustively enumerated by AST. Source docstrings contain historical stale “not built yet” wording; executable constructors/validators/call sites are authoritative for this inventory.

## Adapter ownership, not invented parity (B03/D01)

- MCP `StateManager.status()` returns `is_loaded`, `repo_id`, `quant`, `device`; there is **no engine status function**. Residency and load replacement stay there. Its 8-entry model-scoped LRU handle registry is cleared before every load attempt, including a failing one. There is no unload operation.
- MCP generates by unpacking JSON into canonical payloads, calls `run_diffusion` in a worker thread, then serializes native results. Transient cancellation registration remains in `commands/generate.py`. No new session/lifecycle abstraction.
- Comfy owns node IDs, sockets, widgets, graph/tensor/output envelopes, UI/web registration, callbacks and offloading. Its `DGEMMA_*` socket strings are not toolkit root exports.
- Analysis parses emitted traces downstream; tally audit evaluates downstream records; run-log encoding/provenance belongs to consumers. These source-only helper responsibilities are classified, not moved or made core imports. A future shared run-log must accept product provenance explicitly, not infer the old distribution.

## Existing differences and defects: preserve, do not repair

| Finding | Owner / follow-on |
|---|---|
| MCP rejects empty prompt even when a valid cache could drive pure injection; empty-string cache handle acts absent | MCP adapter; separate reproduction/semantic repair, not B |
| Cancellation registered before payload construction enters `try/finally`; constructor error can leave registration | MCP adapter; separate cleanup defect |
| Denoise omits `should_cancel`; sampler forwards it | Comfy consumer; separate defect, not silent D parity repair |
| MCP capture unpack only supports `top_k`/`keep_frames`, not Tier-2 fields; frame callback not a protocol streaming contract | MCP schema parity deferred; root preserves existing Python capability only |
| Multi-block composed prompt/cache offset and cache aliasing guards | [source #263](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/263), [#265](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/265) remain separate |
| Quantized tie integrity | [source #264](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/264), no extraction fix claim |
| Run-log/MCP parity and strict stdio | [source #103](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/103), [#308](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/308), separate acceptance/protocol work |

Future B tests compare native/root identity and behavior, not idealized desired behavior. No stable version policy, packaging support matrix or installed compatibility is established here. C–F remain separately deferred; proposed historical ADR-CDG-021 is not ratified.
