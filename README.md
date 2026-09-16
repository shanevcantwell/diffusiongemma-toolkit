# diffusiongemma-toolkit

> [!CAUTION]
> **Bootstrap status: partial boundary implementation (B01 only).** This repository is **not installable**, publishes no wheel or release, and exposes **no stable public API**. The retained Python and MCP files are selected historical source material, not a supported package. Do not use `pip install`, depend on `dgemma`, or treat the current module layout as a compatibility promise.

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
- the settled extraction plan and current [Phase A manifest/contract inventory](docs/refactor/manifest.json), reviewed (A04 PASS);
- a preserved [original V01 baseline](docs/refactor/baseline-v01.md): BLOCKED, 16 collection errors, 2 collected, zero executed; a distinct [authorized CPU F0 rerun](docs/refactor/baseline-v01-cpu-f0.md): PASS, 295 collected/292 passed/2 skipped/1 strict xfail. Independent A04 is PASS; [B01 root re-exports](docs/refactor/b01.md) PASS (63 focused tests). B02–B04 and V02 remain PENDING. Shared-base pip check exit 1 is not dependency-health PASS.

## What is deliberately absent

- packaging metadata, dependency declarations, extras, entry points, and install commands;
- a stable API or completed common consumer boundary (B01 implements only the root exports);
- a released artifact, version, tag, or compatibility guarantee;
- consumer conversion, behavior fixes, SDK upgrades, lifecycle policy, or offload changes.

Start with [ARCHITECTURE.md](ARCHITECTURE.md), [docs/EXTRACTION_PLAN.md](docs/EXTRACTION_PLAN.md), and [docs/HANDOFF.md](docs/HANDOFF.md). Historical provenance is recorded in [docs/FOUNDING.md](docs/FOUNDING.md) and [docs/provenance/SOURCE.md](docs/provenance/SOURCE.md).

## License

The selected source lineage remains licensed under GNU GPL v3; see [LICENSE](LICENSE).
