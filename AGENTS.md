# Agent instructions

Read these pointers before acting:

1. [README.md](README.md) — current maturity and explicit non-claims.
2. [docs/HANDOFF.md](docs/HANDOFF.md) — current resumable state and mandatory stop gate.
3. [docs/EXTRACTION_PLAN.md](docs/EXTRACTION_PLAN.md) — settled boundary and phased future work.
4. [ARCHITECTURE.md](ARCHITECTURE.md) — intended architecture versus retained historical code.
5. [docs/FOUNDING.md](docs/FOUNDING.md) and [docs/provenance/SOURCE.md](docs/provenance/SOURCE.md) — identity and provenance.
6. [decisions/README.md](decisions/README.md) — how to interpret frozen historical ADRs.

Portable doctrine references:

- [Ground Physics](https://github.com/shanevcantwell/operating-doctrine/blob/main/ground-physics/GROUND_PHYSICS.md)
- [Code Constitution](https://github.com/shanevcantwell/operating-doctrine/blob/main/ground-physics/CODE_CONSTITUTION.md)

## Current constraints

- This repository is pre-implementation, not installable, and has no stable public API.
- Do not infer present behavior or support from retained historical source/tests.
- Do not add code, packaging, APIs, dependencies, releases, or behavior changes during the founding bootstrap.
- Do not modify historical `decisions/adr-cdg-*.md` bodies or statuses.
- Do not make consumers reach through the future public contract into engine internals.
- Preserve existing ownership of lifecycle/residency, cancellation, observers, payloads, and per-run state.
- Fully qualify source issues as `https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/...`.
- Implementation and package publication remain gated as recorded in [docs/HANDOFF.md](docs/HANDOFF.md); repository minting is not a package release.

When documents disagree, report the conflict rather than silently widening scope. Repository-local status and the linked dashboard issue are the cold-start handoff; no local-machine scratch file is authoritative.
