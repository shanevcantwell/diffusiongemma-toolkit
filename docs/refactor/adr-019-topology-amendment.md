# Historical ADR-CDG-019 topology amendment (unnumbered)

**Authored:** 2026-09-16. **State:** Phase A decision record independently reviewed (A04 PASS); implementation not performed. No new ADR identity, prefix or registry entry is minted.

**Amends for this target:** the MCP-primitives/directory-morph recipe in [frozen ADR-CDG-019](../../decisions/adr-cdg-019-mcp-as-contract-topology-remediation.md), source baseline [fed377af](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/blob/fed377afc7b54f03cb7faa4dd798c80c15279d8a/decisions/adr-cdg-019-mcp-as-contract-topology-remediation.md). This is the MCP topology record, **not** an identically numbered rescue-branch latent-preview document. Its original accepted status/body remain unchanged. The [decision index](../../decisions/README.md) supplies the reverse link without modifying frozen history.

## Context and authority

The fresh-context regroup has occurred. The operator authorized a behavior-preserving A/B refactor in the [live ledger](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3), following the [continuation gate](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/1). Repository/distribution identity is `diffusiongemma-toolkit`, namespace `dgemma`; MCP is optional, not the core. C packaging, D installed Comfy conversion, E live certification and F publication remain separate. V01 now has distinct CPU F0 PASS evidence; its original infrastructure-blocked result remains unchanged. Independent A04 review is PASS; B01 is PENDING, not implemented.

The historical recipe would put a transport-neutral contract inside an MCP-named primitives module, duplicate engine signatures, move directories, and leave encode as a sanctioned bypass. Current callers already use typed native functions and canonical classes. Source main now has an MCP encode command and KV handle registry; the older “no MCP tool wrapping encode” rationale no longer describes this baseline.

## Decision for the bounded refactor

1. Establish the explicit root `dgemma` export set recorded in [contracts.json](contracts.json), shared by Python, MCP and Comfy. Engine definitions remain in their current modules. Public means the documented root names, **not** every implementation submodule below that namespace.
2. Directly re-export already typed native callables and canonical classes. Binding the original object preserves exact signatures/defaults/annotations, function and class identity, exception propagation and accepted duck typing structurally. An extra `_api.py` wrapper duplicates those signatures, can drift, and changes callable identity without a concrete adapter need. A delegate is warranted only for a demonstrated adaptation need; a substantive semantic change is surfaced, not hidden in extraction.
3. Include native `encode_sequence`, `decode_frames` and `tokenizer_fingerprint`, plus the canonical payload vocabulary and consumer-used constants. Remove the historical encode exception: no consumer may import `dgemma.kv_cache` directly merely because it performs encode. Add `QUANT_CHOICES` as an alias to native `_QUANT_CHOICES`; do not rename the mint.
4. Do not extract MCP status/registry/cancel plumbing into the engine. `StateManager.status`, model residency, the model-scoped 8-entry LRU and transient cancel registration remain adapter-owned. Preserve native run callbacks, controls, constraints and capture through existing arguments. No new status function, Session, unload, lifecycle or tenancy abstraction.
5. Keep existing layout for B; redirect retained MCP internal imports to the root and test the boundary. Source Comfy call sites are inventoried now, not edited. Their installed-package conversion is D after C evidence. No intermediate `dgemma_mcp/primitives.py` or `consumers/comfyui` migration is necessary. Optional packaging layout/entry-point proof belongs to C and must not shadow the real `mcp` SDK.

## Import arithmetic correction and enforcement

Historical `surfaces/comfyui` → `consumers/comfyui` is a **same-depth** change: both have two path segments below the pack root. For a module with package `<pack>.surfaces.comfyui`, `...dgemma` climbs to `<pack>`; the directory-loaded branch is distinguished by `__package__.count('.') >= 2`, while standalone `surfaces.comfyui` has one dot. Renaming the first segment alone does not justify `>= 3`. Three leading dots are not a claim that the package must contain three dots.

B does not move those directories. Current MCP `state_manager` has analogous two-level positioning; command modules are a level deeper. Resolve relative imports using actual package context and `level - 1` climbs, not textual dot-count substitutions. D's installed `from dgemma import ...` has no pack-relative climb to the toolkit, while Comfy sibling imports remain consumer-owned. Existing Comfy loader/dual-context tests remain obligations, not proof delivered by A.

Static boundary fixtures must distinguish **direct** consumer imports from legitimate transitive engine imports caused by root re-exports. Permit `from dgemma import load_model as load` and root aliases only for declared names; reject `from dgemma.model import load_model`, `import dgemma.loop as loop`, `from dgemma import model`, relative internal reaches and wildcard imports. Include negative alias/relative fixtures. Runtime `sys.modules` containing engine submodules is not itself a boundary violation. Exact enforcement obligations are in [gates.md](gates.md).

## Trade-offs and consequences

The root cut has less directory churn and fewer duplicated type/default definitions than the dated recipe. It does not visually hide implementation modules or make accidental Python access impossible; explicit static edge checks and a documented public allowlist must enforce the cut. Current eager import behavior and heavy dependency requirements are preserved, not solved by lazy-import redesign. Root/native identity alone does not prove installed isolation or behavior: those are separate gates.

Thin typed delegates remain an available mechanism when necessary, not an unconditional extra layer. Promoting every engine-test import, cloning payload types, rewriting old ADR bodies and manufacturing status parity are rejected because each changes the contract rather than exposing the existing one.

## Open conditions (not undecided topology)

- A01–A04 are PASS for completeness, canonicality, behavior and amendment scope; see gates.md for independent review evidence.
- V01 original result remains [BLOCKED](baseline-v01.md); the distinct [authorized CPU F0 rerun](baseline-v01-cpu-f0.md) is PASS with two skips and one strict xfail. Shared-base pip check exit 1 is not dependency-health certification. A04 independent review is PASS.
- B implementation and enforcement are pending. C–F still require their separately scoped acts and evidence. Adjacent defects remain in [compatibility.md](compatibility.md), not repaired here.
