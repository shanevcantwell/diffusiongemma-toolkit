# diffusiongemma-toolkit

> [!CAUTION]
> **Bootstrap status: pre-implementation.** This repository is **not installable**, publishes no wheel or release, and exposes **no stable public API**. The retained Python and MCP files are selected historical source material, not a supported package. Do not use `pip install`, depend on `dgemma`, or treat the current module layout as a compatibility promise.

`diffusiongemma-toolkit` is the settled name for a future standalone DiffusionGemma capability package. Its intended Python namespace is `dgemma`; a future optional transport extra is intended to be spelled `diffusiongemma-toolkit[mcp]`. Neither distribution form exists yet.

## Intended product boundary

The planned architecture has one typed, transport-neutral Python contract:

```text
ComfyUI-DiffusionGemma ─┐
optional MCP adapter ───┼──> public dgemma contract ──> engine internals
Python callers ─────────┘
```

All three consumers will use the same public contract. Consumers will not reach into engine internals. The split preserves current ownership of model residency/lifecycle, cancellation, observers, payloads, and per-run state; it does not redistribute those responsibilities or invent a session abstraction.

The existing [ComfyUI-DiffusionGemma](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma) project keeps its identity, nodes, UI, sockets, workflows, and offloading integration. Generic consumer helpers have not been extracted or assigned here.

## What is here now

- selected `dgemma/` and `surfaces/mcp/` history;
- dependency-safe historical tests, not a certified runnable suite;
- 17 frozen historical `ADR-CDG-*` records with their original statuses;
- GPL-3.0 license lineage and repository-local provenance evidence;
- the settled extraction plan and current [Phase A manifest/contract inventory](docs/refactor/manifest.json), authored for review;
- a [sanitized original V01 baseline](docs/refactor/baseline-v01.md): BLOCKED, 16 collection errors, 2 collected, zero executed; isolated CPU provisioning authorized, actual rerun pending.

## What is deliberately absent

- packaging metadata, dependency declarations, extras, entry points, and install commands;
- an implemented public contract or stable API (the proposed export inventory is documentation only);
- a released artifact, version, tag, or compatibility guarantee;
- consumer conversion, boundary repair, behavior fixes, SDK upgrades, lifecycle policy, or offload changes.

Start with [ARCHITECTURE.md](ARCHITECTURE.md), [docs/EXTRACTION_PLAN.md](docs/EXTRACTION_PLAN.md), and [docs/HANDOFF.md](docs/HANDOFF.md). Historical provenance is recorded in [docs/FOUNDING.md](docs/FOUNDING.md) and [docs/provenance/SOURCE.md](docs/provenance/SOURCE.md).

## License

The selected source lineage remains licensed under GNU GPL v3; see [LICENSE](LICENSE).
