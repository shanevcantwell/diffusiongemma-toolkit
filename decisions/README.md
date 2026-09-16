# Historical decision records

The 17 `ADR-CDG-*` files in this directory are **frozen historical records copied with selected ComfyUI-DiffusionGemma history**. Their bodies, handles, links, and statuses are preserved exactly. They do not establish a new `diffusiongemma-toolkit` ADR namespace and must not be rewritten to look target-native.

Some historical links point to files, ADRs, issues, pull requests, or experiments outside this selected subset. That is expected. Consult each record in its original source-baseline context:

`https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/blob/fed377afc7b54f03cb7faa4dd798c80c15279d8a/decisions/<filename>`

Before adding the first genuinely new target ADR, ground the current ADR-namespace authority. Do not invent or register a prefix from this index.

## Retained records and original status

| Record | Historical status |
|---|---|
| [ADR-CDG-001](adr-cdg-001-native-socket-types.md) | accepted |
| [ADR-CDG-003](adr-cdg-003-node-engine-seam.md) | accepted |
| [ADR-CDG-004](adr-cdg-004-diffusers-pipeline-drive-seam.md) | accepted |
| [ADR-CDG-005](adr-cdg-005-canvas-state-resumable-savestate.md) | accepted (implementation pending) |
| [ADR-CDG-006](adr-cdg-006-advanced-sampler-step-window-resume.md) | proposed |
| [ADR-CDG-008](adr-cdg-008-mcp-center-multi-surface-topology.md) | accepted |
| [ADR-CDG-010](adr-cdg-010-constraint-composite-and-pinned-mask.md) | accepted |
| [ADR-CDG-011](adr-cdg-011-control-signal-cv-lfo-mod-matrix.md) | accepted |
| [ADR-CDG-012](adr-cdg-012-mitm-seam-ar-diffusion-kv-cache.md) | accepted |
| [ADR-CDG-014](adr-cdg-014-frame-capture-discipline.md) | accepted |
| [ADR-CDG-018](adr-cdg-018-decompose-loop-py.md) | accepted |
| [ADR-CDG-019](adr-cdg-019-mcp-as-contract-topology-remediation.md) | accepted |
| [ADR-CDG-021](adr-cdg-021-per-surface-vram-tenancy-ownership.md) | proposed |
| [ADR-CDG-022](adr-cdg-022-publish-policy-public-tree-vs-session-residue.md) | accepted |
| [ADR-CDG-023](adr-cdg-023-mcp-2x-port-strategy.md) | accepted |
| [ADR-CDG-024](adr-cdg-024-prompt-under-injection-composition.md) | Accepted |
| [ADR-CDG-025](adr-cdg-025-mcp-kv-cache-handle-registry.md) | Accepted |

This table is an index, not a ratification act. When detail differs, the untouched historical file is the record.

## Current topology amendment

The [unnumbered ADR-CDG-019 topology amendment](../docs/refactor/adr-019-topology-amendment.md) (2026-09-16) records the target common-root cut, direct native re-exports, encode coverage and corrected same-depth arithmetic. It is Phase A reviewed (A04 PASS), not implemented. It amends the target migration recipe without changing any historical body/status or minting a new ADR identity.
