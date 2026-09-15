# Contributing

`diffusiongemma-toolkit` is in a founding, pre-implementation state. It is not installable and does not yet declare a stable public API.

## Before contributing

Read:

- [README.md](README.md) for current non-claims;
- [ARCHITECTURE.md](ARCHITECTURE.md) for the settled layer cut;
- [docs/EXTRACTION_PLAN.md](docs/EXTRACTION_PLAN.md) for sequencing and gates;
- [docs/HANDOFF.md](docs/HANDOFF.md) for the current publication/approval stop;
- [decisions/README.md](decisions/README.md) before citing historical ADRs.

The governing dashboard is [ComfyUI-DiffusionGemma issue 310](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/310) until the target repository and its gate issue are published and linked from the handoff.

## Founding-bootstrap limits

Until mandatory human regroup completes, contributions must not add or claim:

- package metadata, dependencies, install commands, entry points, extras, wheels, versions, tags, or releases;
- a stable API or final public export inventory;
- consumer conversion, engine-boundary repairs, behavior fixes, SDK upgrades, lifecycle policies, or offload changes;
- rewrites or status changes to historical `ADR-CDG-*` files.

Documentation corrections and provenance-review findings should be narrowly scoped and must preserve the honest bootstrap status.

## Future implementation expectations

Once explicitly authorized, implementation should proceed in small reviewable changes following the gates in the extraction plan. Changes must preserve ownership boundaries, include focused evidence for behavior they alter, and report unrun GPU/live/installed-artifact axes as unrun—not passed.

Use fully qualified source issue URLs when referring to the source project. Do not use bare issue-number references that could be mistaken for target-repository issues.
