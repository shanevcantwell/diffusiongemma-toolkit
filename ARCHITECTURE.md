# Architecture

## Status

This document records the **settled target architecture**, not an implemented or stable API. The repository currently contains selected historical source only. Packaging, the public export inventory, consumer conversion, and installed-artifact validation have not begun.

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

A future documented set of `dgemma` exports will provide one transport-neutral, typed interface. Thin delegates may expose existing load/status/generate/encode/decode/KV/cancel/capture/control/constraint capabilities while preserving native result and canonical type identities.

The exact export list, signatures, error behavior, compatibility policy, and internal module layout are intentionally unresolved until the contract-inventory phase. The retained tree is not that declaration.

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

1. **Common contract missing.** Retained MCP commands and the downstream Comfy adapter historically called implementation-level functions through different routes. Typed delegates and a documented public export set must be established first.
2. **Historical ADR-CDG-019 recipe is dated.** Its accepted intent remains historical context, but neutral placement, import-depth arithmetic, and encode coverage require an explicit future amendment. The historical body is frozen here.
3. **Standalone packaging missing.** There is intentionally no `pyproject.toml`, requirements file, wheel configuration, extra, or entry point at bootstrap.
4. **Generic helper ownership unresolved.** Analysis, audit, and run-log helpers were not extracted wholesale. Each must be assigned by responsibility later.
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
