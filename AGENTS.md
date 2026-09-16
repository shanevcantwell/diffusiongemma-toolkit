# Agent instructions

Read these pointers before acting:

1. [README.md](README.md) — current maturity and explicit non-claims.
2. [docs/HANDOFF.md](docs/HANDOFF.md) — current resumable state and phase gates.
3. [docs/EXTRACTION_PLAN.md](docs/EXTRACTION_PLAN.md) — settled boundary and phased future work.
4. [ARCHITECTURE.md](ARCHITECTURE.md) — intended architecture versus retained historical code.
5. [docs/FOUNDING.md](docs/FOUNDING.md) and [docs/provenance/SOURCE.md](docs/provenance/SOURCE.md) — identity and provenance.
6. [decisions/README.md](decisions/README.md) — how to interpret frozen historical ADRs.

Portable doctrine references:

- [Ground Physics](https://github.com/shanevcantwell/operating-doctrine/blob/main/ground-physics/GROUND_PHYSICS.md)
- [Code Constitution](https://github.com/shanevcantwell/operating-doctrine/blob/main/ground-physics/CODE_CONSTITUTION.md)

## Current constraints

- This repository has B01 root re-exports, is not installable, and has no stable public API.
- Do not infer present behavior or support from retained historical source/tests.
- Fresh-context A/B refactor authorization is satisfied. Phase A and V01 CPU F0 are PASS. B01 root re-exports PASS; B02 enforcement and 184 focused tests PASS (docs/refactor/b02.md). Actual MCP consumer gate FAIL is expected pending B03; B03/B04/V02 remain PENDING.
- B01 changes production only in dgemma/__init__.py; native definitions are untouched. No packaging/Comfy changes. The authorized CPU rerun is separately recorded as V01 PASS; the original BLOCKED baseline is unchanged. The shared-base environment is non-hermetic and pip check exited 1; do not infer dependency health or wider certification.
- C packaging, D installed Comfy conversion, E live certification and F publication remain separately deferred. Preserve existing files; cleanup only positively identified run-owned artifacts.
- Do not modify historical `decisions/adr-cdg-*.md` bodies or statuses.
- Do not make consumers reach through the future public contract into engine internals.
- Preserve existing ownership of lifecycle/residency, cancellation, observers, payloads, and per-run state.
- Fully qualify source issues as `https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/...`.
- Resume from [docs/refactor/manifest.json](docs/refactor/manifest.json), [docs/refactor/gates.md](docs/refactor/gates.md) and [issue #3](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3). Runtime verification and package publication are distinct gates; minting is not a package release.

When documents disagree, report the conflict rather than silently widening scope. Repository-local status and the linked dashboard issue are the cold-start handoff; no local-machine scratch file is authoritative.
