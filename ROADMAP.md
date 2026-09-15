# Roadmap

This roadmap records sequence, not implementation authorization. The current stop is **founding records prepared locally; review and publication pending; mandatory human regroup required before implementation**.

## 0. Founding mint — current

- [x] Filter selected source history from baseline `fed377afc7b54f03cb7faa4dd798c80c15279d8a`.
- [x] Audit immutable selected history for containment, provenance, authorship, content, and disclosure risk.
- [x] Author target-specific bootstrap records without code or replacement packaging.
- [ ] Review bootstrap HEAD content and founding diff.
- [ ] Create and publish the authorized public repository.
- [ ] Open/review/merge the founding-record PR and create the target `user:gate` issue.
- [ ] Fill final repository, PR, issue, and commit pointers in [docs/HANDOFF.md](docs/HANDOFF.md).
- [ ] Stop for mandatory HITL.

## A. Inventory the contract

After fresh-context authorization, map exact public exports, signatures, types, callbacks, ownership, errors, dependencies, and compatibility. Prepare the necessary amendment to the dated ADR-CDG-019 recipe without rewriting its historical body.

## B. Establish one typed boundary

Implement thin transport-neutral delegates and redirect adapters to them. Add static direct-edge and focused contract-fidelity tests. Preserve lifecycle, cancellation, observers, payloads, per-run state, encode/decode, and KV behavior.

## C. Prove standalone packaging

Only after the contract is real, add package discovery, dependencies, optional `[mcp]`, and entry points. Build and inspect wheels; test clean installs and representative calls outside every checkout, without editable installs or path injection.

## D. Convert the downstream consumer

Make ComfyUI-DiffusionGemma depend on a pinned installable artifact and use only the public contract. Keep its identity, nodes, UI, sockets, workflows, offloading, and graph/tensor envelopes unchanged. Remove duplication only after installed-consumer gates pass.

## E. Validate independent axes

Run no-GPU contract, Python-only, MCP-extra, downstream Comfy, protocol, dependency-resolution, and separately authorized live/GPU/model gates. Record each axis independently; a skipped axis is not a pass.

## F. Authorize release separately

Publication of a package, MCP offering, downstream release, tag, or registry artifact requires separate evidence and authorization. Preserve a usable rollback path.

Full gates, prerequisites, adjacent findings, and obligations are in [docs/EXTRACTION_PLAN.md](docs/EXTRACTION_PLAN.md).
