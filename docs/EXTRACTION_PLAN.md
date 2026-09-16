# DiffusionGemma extraction plan

## Status and authority

This is the complete repository-local continuation plan. It supersedes scratch planning and is written so a fresh context can resume from this repository and the public dashboard.

The operator authorized a bounded public repository mint in [ComfyUI-DiffusionGemma issue 310](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/310), followed by mandatory HITL. Selected history has been filtered and audited. The founding records and final review/branch state are recorded in [HANDOFF.md](HANDOFF.md) and its live dashboard pointers. That mint required a fresh context and operator regroup; this historical condition has now been fulfilled. Current authority is bounded A/B behavior-preserving refactor work on [issue #3](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3), not package publication. Phase A records are [reviewed (A04 PASS)](refactor/manifest.json); B01 root re-exports and [B02 enforcement](refactor/b02.md) are implemented; B02 focused tests PASS; [B03 MCP redirection](refactor/b03.md) and actual edge gate PASS (203 focused tests). B04 scoped CPU rehoming PASS; V02 independent verification remains pending. Original V01 remains [BLOCKED](refactor/baseline-v01.md); a distinct [authorized CPU F0 rerun](refactor/baseline-v01-cpu-f0.md) is PASS (295 collected/292 passed/2 skipped/1 strict xfail). Independent A04 review is PASS; [B01](refactor/b01.md) PASS has 63 focused tests, not a complete consumer-boundary or V02 result. The shared-base environment is non-hermetic, with recorded pip check exit 1; no wider certification follows. C–F remain separately deferred.

The source baseline is `fed377afc7b54f03cb7faa4dd798c80c15279d8a`; the filtered historical tip is `6a290854c038194c3f79f038a10a912e36b94c34`. See [provenance/SOURCE.md](provenance/SOURCE.md).

## Confirmed product identities

- Repository and future Python distribution: `diffusiongemma-toolkit`.
- Public Python import namespace: `dgemma`.
- Future optional transport install: `diffusiongemma-toolkit[mcp]`.
- Existing downstream consumer: [ComfyUI-DiffusionGemma](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma), unchanged in repository and registry identity.

These names are settled. Recording them does not create a wheel, release, extra, or stable API.

## Confirmed architecture

The new product is intended to become an independently usable Python capability package. MCP is an optional adapter, not the core.

```text
ComfyUI-DiffusionGemma ─┐
optional MCP adapter ───┼──> public typed dgemma contract ──> engine
Python caller ──────────┘
```

### One contracted cut, three logical layers

1. **Engine.** Existing computation, payload implementations, validation, and per-run construction remain below the public boundary.
2. **Transport-neutral typed Python contract.** A documented set of public `dgemma` exports will expose existing capabilities through thin delegates where necessary, preserving canonical types, native results, callbacks, encode/decode, and KV behavior. Importing `dgemma` will not make every implementation submodule public.
3. **Consumers.** Direct Python callers, the MCP adapter, and ComfyUI invoke the same public contract in process. No consumer receives a separate route into engine internals.

Preserve existing placement of model residency/lifecycle, transient cancellation, per-run state, observers, and payloads. Do not invent an empty catch-all `Session`, make Comfy adopt MCP registries, move adapter state into the stateless engine, or make ordinary Python imports depend on the MCP SDK. Packaging cannot create an internal reach-through exception.

The optional MCP adapter owns JSON/protocol schemas, dispatch unpacking, serialization and summaries, transport handles, and its registry/plumbing. Comfy owns nodes, sockets, graph/tensor/UI envelopes, observers, workflows, and offloading. Python calls retain tensors, native objects, and callbacks without JSON round trips. Core ingress remains validation authority; adapters handle transport shape, not duplicate engine policy.

## Product ownership

**This repository** will own `dgemma`, its public typed contract, and optionally the MCP adapter. A plain Python installation must eventually support real contract use without either interface framework installed.

**ComfyUI-DiffusionGemma** stays where it is. It keeps its node-pack identity, UI, sockets, workflows, installer context, and memory/offload integration. It will later depend on a pinned package and call only the public contract.

Generic analysis, tally-audit, and run-log helpers were not extracted in this mint. The [path manifest](refactor/manifest.json) assigns downstream analysis/audit/run-log responsibilities; all helper extraction remains deferred. If run-log support becomes shared, product provenance must be supplied explicitly rather than inferred from the old Comfy distribution.

## Actual prerequisites

### A common consumer boundary remains incomplete

B01 supplies the 30 canonical root exports. The historical MCP commands and downstream Comfy adapter still call engine-level functions through different routes. Before extraction can be called implemented, adapters need the same explicit root contract for native load/generate/encode/decode/KV/callback/cancel/capture/control/constraint capabilities. Already typed native definitions should be re-exported directly, preserving identity/signatures without redundant wrappers. Status, residency and cancellation registration remain adapter-owned; no new engine status or Session is proposed. B redirects retained MCP; installed Comfy conversion stays in D.

### Historical ADR-CDG-019's migration recipe is dated

[ADR-CDG-019](../decisions/adr-cdg-019-mcp-as-contract-topology-remediation.md) remains an accepted historical record and must not be rewritten. The [unnumbered Phase A amendment](refactor/adr-019-topology-amendment.md), reviewed (A04 PASS), records transport-neutral placement, final naming, correct same-depth import arithmetic and encode coverage. Accepted historical intent does not settle those details for this target.

### Standalone packaging is missing

The bootstrap intentionally deletes legacy `pyproject.toml` and `requirements.txt`. Future packaging must explicitly discover the correct packages, declare dependencies and optional MCP support, define any entry points, and be proved through clean installs outside all checkouts. Import success alone is insufficient.

## Future waterfall

A/B authority is granted; transitions require actual evidence, not another blanket regroup gate. [Manifest task dependencies](refactor/manifest.json) govern the current bracket. C–F require their separately scoped authorization/evidence.

### Phase A — Ground the manifest and contract

- Verify current repository/dashboard state and create isolated implementation work.
- Classify each path, export, test, dependency, document, helper, script, and asset as engine, public contract, MCP adapter, Comfy consumer, or excluded.
- Inventory exact public signatures, canonical types/configuration, defaults, errors, forwarding behavior, native result identity, ownership, and lifetime for load/status/generate/encode/decode/KV/cancel/capture/control/constraints.
- Define public versus internal `dgemma` modules without declaring every retained module public.
- Prepare the necessary ADR-CDG-019 amendment and reconcile final topology/naming with tests and documentation.
- Keep accepted/proposed historical statuses explicit; do not ratify [ADR-CDG-021](../decisions/adr-cdg-021-per-surface-vram-tenancy-ownership.md) merely by extracting.

**Exit:** a grounded ownership manifest, API/compatibility contract, and decision amendment are reviewable; intent-changing choices are resolved before dependent work.

### Phase B — Establish the boundary

- Implement the documented root native re-exports (delegates only where a real adaptation requires them) and redirect retained MCP without redistributing responsibilities. Inventory/check source Comfy edges now; installed Comfy edits remain D, not this target-only bracket.
- Include encode in boundary coverage and derive imports from the final layout.
- Add static direct-edge checks that allow documented public exports/types while rejecting adapter imports of implementation internals.
- Add focused tests for native result/type identity, defaults, error forwarding, callbacks/observers, cancellation, state/per-run behavior, encode/decode, and KV handling.
- Account separately for known defects rather than repairing them inside topology work.

**Exit:** declared contract and boundary gates pass; remaining defects have explicit owners and dispositions.

### Phase C — Prove an independently installable artifact

- Add package discovery, metadata, dependencies, the optional `[mcp]` extra, and any launch entry point only after the contract is real.
- Build and inspect wheels.
- Install into clean environments and execute imports, representative Python calls, tests, and entry points outside every checkout, with source directories unavailable.
- Prohibit editable installs, `sys.path` injection, or checkout-dependent success.
- Verify Python-only and MCP-extra configurations, external `mcp` SDK non-shadowing, supported SDK range, and downstream dependency/ABI constraints.

**Exit:** recorded installed-wheel evidence proves the artifact independently usable before consumer extraction.

### Phase D — Switch the downstream consumer

- Make ComfyUI-DiffusionGemma depend on a pinned installable artifact and use only its public contract.
- Keep root node-pack behavior, registry identity, node IDs, sockets/widgets/output shapes, web registration, workflows, interpreter targeting, and Comfy memory integration compatible.
- Remove bundled engine/MCP duplication only after installed-consumer gates prove replacement viability.
- Preserve selected-history provenance and licensing; do not rewrite source history.

**Exit:** the products work independently without duplicated engine code, internal bypasses, or source-path tricks.

### Phase E — Validate independent no-GPU and live axes

- Run contract, isolation, Python-only, MCP-extra, Comfy, protocol, packaging, and dependency gates against installed artifacts.
- Separately run authorized real-weight/hardware scenarios for Python, MCP, and Comfy: load, status, encode/KV, generate, streaming/observers, cancellation, reload, and memory behavior.
- Obtain explicit reproduction/acceptance criteria for [source issue 308](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/308) and verify strict stdio: protocol on stdout, diagnostics on stderr.
- Record exact versions/environments and independent results. A failure is not hidden; unavailable axes remain `NOT RUN`.

**Exit:** each product's no-GPU/live claims are backed by its own evidence.

### Phase F — Authorize publication and transition separately

- Re-run content/privacy/license review for any newly introduced history or artifacts.
- Obtain separate authorization for package, MCP, downstream, registry, tag, and release acts.
- Publish the capability package before a compatible pinned Comfy release; publish MCP only after protocol obligations pass.
- Smoke-test approved installed versions and preserve the prior monolithic Comfy release plus its known-compatible environment and reversal instructions.

**Exit:** approved versions have independent installed evidence, provenance, and usable rollback.

## Enforcement matrix

| Gate | Required evidence |
|---|---|
| One callable boundary | AST/static direct-import analysis permits documented public `dgemma` exports/types and rejects consumer imports of internals; direct and transitive imports are distinguished. |
| Python isolation | Public Python imports and representative no-GPU calls work without MCP SDK or ComfyUI; engine/API import neither framework. |
| Contract fidelity | Native result and canonical type identity/defaults; encode/decode/KV coverage; callback, observer, and cancellation forwarding; ownership and per-run checks. |
| Comfy compatibility | Real loader context, import-depth gates, node/socket/output/web ABI, workflow, and installed-consumer evidence. |
| Packaging | Wheel contents/discovery, clean outside-checkout installs/imports/entry points, Python-only and MCP-extra environments, SDK non-shadowing. |
| Dependency safety | Resolution inspected in the actual Comfy interpreter, including transitive torch/torchvision/numpy/Pillow compatibility; no silent replacement of a working stack. |
| Protocol | End-to-end stdio JSON-RPC with protocol-only stdout and stderr diagnostics on startup and error paths. |
| Existing obligations | Relevant seam and MCP boundary tests are preserved or rehomed by responsibility, not blindly copied by old path. |

## Adjacent findings — separate work

These are not extraction prerequisites and must not be silently fixed in topology work:

- **MCP empty prompt/cache parity.** Historical generate dispatch rejects an empty prompt and treats an empty-string cache handle as absent. Reproduce valid-cache/empty-prompt and invalid-empty-handle behavior; establish missing/empty/unknown semantics before repair.
- **Malformed-payload cancellation cleanup.** Historical generate dispatch registers cancellation before some payload constructors enter cleanup. Reproduce constructor failure with a run ID and verify no active registration remains before choosing a minimal repair.
- **Comfy denoise cancellation forwarding.** The historical downstream denoise route omitted `should_cancel` while the sampler route forwarded it. Reproduce in the Comfy repository; socket parity alone does not prove cancellation.
- Prompt/KV offset and cache mutation remain tracked by [source issue 263](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/263) and [source issue 265](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/265).
- Quantized tie integrity remains tracked by [source issue 264](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/264). Extraction does not claim to fix it.
- MCP parity/run-log ownership remains related to [source issue 103](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/103); SDK migration and protocol work remain separately gated.

Existing bugs follow their owning layer. No blanket backlog or backend rewrite is authorized.

## Content, history, and decision hygiene

- Classify documents, tests, scripts, assets, and helpers by responsibility; do not copy entire old directories by convenience.
- Do not include model weights or unrelated research material.
- Preserve original ADR handles/statuses and fully qualified source issue URLs.
- Historical ADR links may remain unresolved inside this subset; use [decisions/README.md](../decisions/README.md) to find source-baseline context rather than rewriting bodies.
- Maintain ownership/provenance across repositories. Do not automatically close or transfer source issues.
- Keep packaging, implementation, behavior repair, runtime deployment, package release, and downstream release as separately evidenced acts.

## Historical mint completion contract (fulfilled bracket; not current tasks)

The founding mint required the parent publication lane to:

1. review the bootstrap working-tree content, its declared file scope, links, privacy, and absence of packaging/install claims;
2. create the authorized public repository and publish only intended `main` and founding-record branch refs, with no tags or unrelated refs;
3. open and review the founding-record PR, record real commit/PR/repository pointers, and merge normally only after declared gates pass;
4. create a target `user:gate` issue containing the architecture, this plan, remaining decisions, and explicit fresh-context stop;
5. cross-link that issue and founding PR from [source issue 310](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/310);
6. update [HANDOFF.md](HANDOFF.md) with actual URLs and SHAs;
7. stop for mandatory HITL with no open implementation branch, release, tag, package, or implementation work.
