# Founding record

## Identity

The operator-selected canonical identities are:

- repository and future Python distribution: `diffusiongemma-toolkit`;
- public Python namespace: `dgemma`;
- future optional transport extra: `diffusiongemma-toolkit[mcp]`;
- downstream consumer: [ComfyUI-DiffusionGemma](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma), unchanged.

Recording these names does not claim that a distribution, extra, public API, release, or registry artifact exists.

## Authority and scope

The founding mint was authorized in [ComfyUI-DiffusionGemma issue 310](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/310). The authorized act is bounded: preserve selected history, establish honest target documentation and provenance, publish through review, create a target continuation gate, then stop for mandatory human regroup. Implementation belongs to a fresh context after that gate.

The settled architecture is one transport-neutral typed `dgemma` contract used by direct Python callers, the optional MCP adapter, and the existing Comfy consumer. No consumer may reach into engine internals. The split preserves existing ownership of lifecycle/residency, cancellation, observers, payloads, and per-run state.

## Historical lineage

The selected source baseline is ComfyUI-DiffusionGemma commit `fed377afc7b54f03cb7faa4dd798c80c15279d8a`, tree `83f3876b7ba335b2f8d1585451baacd865f5fb24`. The filtered historical tip is `6a290854c038194c3f79f038a10a912e36b94c34`, tree `6e51394d7d483559519ed18acdd914953aa8d0c5`.

The filter retained 67 allowlisted paths and mapped 213 of 331 source-main commits; 118 commits with no selected-path effect were dropped. Author and committer headers were preserved. Of the 213 retained commit messages, 190 are byte-identical and 23 contain only automatic abbreviated commit-ID substitutions made by `git-filter-repo`.

The selected `LICENSE` blob is unchanged (`f288702d2fa16d3cdf0035b15a9fcbc552cd88e7`) and carries GNU GPL v3 lineage. See [provenance/SOURCE.md](provenance/SOURCE.md) and the repository-local maps and manifests.

## Historical decisions

The 17 `ADR-CDG-*` documents are frozen records from the source project. Their original handles and statuses remain unchanged. They are not a newly allocated target ADR namespace, and this founding record is not an ADR. Some links in those historical bodies point to source material outside the selected subset; they are intentionally not rewritten. See [../decisions/README.md](../decisions/README.md).

No new ADR code or registry entry was invented. Before the first genuinely new target ADR, current ADR-namespace authority must be grounded.

## Honest bootstrap

The retained code and tests preserve lineage; they do not establish a supported product. At founding bootstrap:

- no packaging metadata or dependency declaration exists;
- no wheel, extra, entry point, version, tag, or release exists;
- no stable public export set has been declared;
- no consumer repair, generic-helper move, bugfix, SDK upgrade, lifecycle policy, or offload change has occurred;
- installed-wheel, downstream compatibility, protocol, live/GPU/model, and release gates have not run.

The complete future plan is [EXTRACTION_PLAN.md](EXTRACTION_PLAN.md). Current publication state is [HANDOFF.md](HANDOFF.md).
