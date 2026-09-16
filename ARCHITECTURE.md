# Architecture

## Status

This document records the **settled target architecture**, not a stable API. Native runtime definitions remain selected historical source. Phase A ownership/API records are [reviewed (A04 PASS)](docs/refactor/manifest.json); [B01](docs/refactor/b01.md) implements 30 canonical root re-exports with 63 focused tests passing. B02–B04/V02 remain pending. V01 has a distinct [CPU F0 PASS](docs/refactor/baseline-v01-cpu-f0.md); the original BLOCKED result is preserved. This shared-base baseline is not installed-artifact or dependency-health certification. Packaging, consumer conversion and installed-artifact validation have not begun.

## One contracted cut

```text
ComfyUI-DiffusionGemma ─┐
optional MCP adapter ───┼──> transport-neutral typed dgemma contract ──> engine
Python callers ─────────┘
```

The split is **at one layer**, not a redistribution across layers.

### 1. Engine

The DiffusionGemma implementation remains below the callable contract. Computation, canonical payload implementations, validation, and per-run construction stay there. Internal modules are not public merely because they live below the `dgemma` namespace.

### 2. Public Python contract

The [Phase A inventory](docs/refactor/contracts.json) records the 30 B01 root exports with exact native signatures, canonical types, defaults and caller evidence. Prefer direct re-exports of already typed native objects: they preserve signatures and identity structurally without redundant `_api.py` wrappers. Engine definitions stay in place; implementation submodules remain private.

Load/generate/encode/decode and native KV/callback/cancel/capture/control/constraint arguments share that cut. Status, residency, LRU handles and cancellation registration remain adapter-owned; there is no engine status or new Session/unload API. This record does not implement or stabilize the contract.

### 3. Consumers

- Direct Python callers use the public contract without ComfyUI or MCP.
- The optional MCP adapter owns protocol schemas, dispatch unpacking, serialization, transport handles, and adapter registry/plumbing.
- ComfyUI-DiffusionGemma remains a separate downstream project and owns its nodes, UI, sockets, graph/tensor envelopes, workflows, observers, offloading, and registry identity.

Every consumer must use the same public contract. Packaging cannot create an exception for importing engine internals.

## Preserved ownership invariants

The extraction must preserve, not redesign:

- model residency and lifecycle ownership;
- cancellation polling and forwarding;
- observers/callback forwarding;
- payload and canonical type identity;
- transient per-run state and existing statelessness expectations;
- encode/decode and KV-cache behavior;
- native Python returns without protocol serialization.

There is no authorization to invent a catch-all `Session`, move adapter registry state into the engine, make ComfyUI consume MCP registries, add an MCP SDK dependency to ordinary Python imports, or impose a new lifecycle/tenancy policy.

## Known gaps before this boundary is real

1. **Consumer boundary incomplete.** Retained MCP commands and the downstream Comfy adapter still call implementation-level functions through different routes. B01 root native re-exports exist; B02 direct-edge enforcement and B03 MCP redirection remain pending. Root tests alone do not close the gap.
2. **Historical ADR-CDG-019 recipe is dated.** Its accepted intent remains historical context, but neutral placement, import-depth arithmetic and encode coverage are addressed by the [unnumbered Phase A amendment](docs/refactor/adr-019-topology-amendment.md), reviewed (A04 PASS). The historical body is frozen here.
3. **Standalone packaging missing.** There is intentionally no `pyproject.toml`, requirements file, wheel configuration, extra, or entry point at bootstrap.
4. **Generic helper extraction deferred.** Analysis, audit, and run-log helpers were not extracted wholesale. The path manifest now classifies analysis/audit/run-log as downstream responsibility; extraction remains deferred, with no helper move authorized by this record.
5. **Behavioral issues remain separate.** Prompt/cache parity, malformed-payload cancellation cleanup, Comfy cancellation forwarding, quantization, and other adjacent defects are not repaired by repository movement.

## Enforcement required during implementation

Future work must prove, rather than assume:

- static direct-import edges allow only documented public exports/types;
- Python-only use works without MCP SDK or ComfyUI installed;
- native results, callbacks, observers, cancellation, state, and type identity survive delegation;
- wheels install and run outside any checkout without editable installs or path injection;
- optional MCP installation does not shadow the external `mcp` SDK;
- downstream Comfy compatibility is validated in its actual environment;
- protocol and live/GPU axes are reported independently.

See [docs/EXTRACTION_PLAN.md](docs/EXTRACTION_PLAN.md) for phased gates. See [decisions/README.md](decisions/README.md) before treating any historical ADR as current target authority.
