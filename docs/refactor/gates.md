# Gates and manifest enforcement

**2026-09-16:** A authored for review; B not implemented. Refactor authorization and isolated CPU provisioning authorization are satisfied. V01 remains **BLOCKED**, not PASS. [Tasks/evidence](manifest.json) · [compatibility](compatibility.md) · [baseline](baseline-v01.md).

## Task graph and transition rules

`A01 census → A02 contract → A03 amendment → A04 independent review`.
`V01 actual baseline + A04 → B01 root exports → B02 static/identity tests → B03 MCP redirection → B04 obligation census → V02 post-change verification`.
`V02 → C01 installed artifact → D01 installed Comfy conversion → E01 independent certification → F01 separately authorized publication`.

The manifest is authoritative for exact dependencies and status. AUTHORED_FOR_REVIEW is not DONE; planned tests are not PASS. BLOCKED records name cause/evidence. A04 cannot close itself through authorship. No runtime/packaging/test-source writes occur in A. B remains gated on reviewed A and actual usable V01 results; environment consent alone does not execute tests. C–F are separately deferred, not silently authorized by A/B.

## B01–B04 implementation obligations (all pending)

1. **Root export identity/signatures (B01/B02).** Exact 30-name allowlist from contracts; compare root `__all__`, resolved imports and each native object with `is`. Compare `inspect.signature`, default object identity where meaningful, annotation resolution and dataclass fields/frozen flags against native definitions. Keep `__module__` and canonical exception identity. Test root constants and QUANT_CHOICES alias, including mutable KNOB_DOCS identity. Reject unaccounted exports and private-module promotion.
2. **Direct-edge AST gate (B02).** Scan every accounted consumer, including source-only Comfy obligations when D is implemented. Resolve `Import`, `ImportFrom`, relative levels and aliases from actual package context. Positive fixtures: explicit root symbol, root alias, permitted consumer siblings. Negative fixtures: internal `from`, internal module aliases, `from dgemma import model`, wildcard, relative bypass, root alias followed by private-module attribute reach. Check both branches of dual-context imports. Dynamic import strings/unknown computed imports require explicit reviewed disposition, not silent acceptance. Do not reject root-triggered transitive implementation imports via `sys.modules`.
3. **Native fidelity/error/callback paths (B02/B03).** Exact call args/defaults, no transport wrapping, dataclass constructors and duck-typed payload acceptance; load poll callback and canonical LoadInterrupted; on_frame propagation and retention independence; should_cancel partial results/capture-first ordering; hook cleanup normal/cancel/error; caller logit_hook rejection; fresh per-run state; encode new wrapper with possible shared mutable cache; decode raw semantics and empty frames. Tests preserve known defects rather than idealizing behavior. Use existing test seams/fakes only where tests already define them, never dependency stubs to fake V01.
4. **Python import isolation (B02/V02).** Subprocess root import and representative CPU calls with neither Comfy nor MCP SDK available; prove ordinary engine import does not depend on adapter modules or import either framework. Distinguish dependency availability from boundary correctness. This is checkout evidence, not installed-artifact evidence.
5. **MCP redirection (B03).** Redirect direct engine edges to root only. Preserve JSON unpacking/serialization, state manager residency/LRU, cancellation registration, schemas and current differences. No new session/status/unload service and no parity repair. Root signature tests do not alone prove MCP behavior.
6. **Source obligation census (B04).** Every source test path has an ownership/deferred disposition in paths shards. Rehome applicable engine, seam, ingress, KV, callback and MCP obligations with fixtures reviewed for actual dependency/Comfy coupling. Source tests were not all selected at mint; 17 retained files are not the whole obligation set. Preserve Comfy-specific tests for D, live/e2e for E, packaging/install for C, generic analysis/audit/run-log for consumer responsibility. Source conftest/config are provenance inputs, not blindly transplanted.

## Manifest checker to implement in B (not delivered as code in A)

Use stdlib JSON/AST/path tooling with the [schema](manifest.schema.json); no mandatory validator dependency. A's external validation uses equivalent explicit structure/type/enum/required-key checks, not a claim that stdlib implements general JSON Schema.

- Re-enumerate committed paths against pinned source/target trees and current candidate tree; require exactly one row per `(scope, source.path)`. Distinguish two baseline rows for a shared path from duplicate rows within a scope. New A documents also have exactly one candidate row, including the manifest/index/shards themselves; no recursive content hashes.
- Verify repository/ref/path/blob against immutable tree entries through Git. `target-authored` has null baseline blob; never treat current HEAD as its own baseline. Destination null is explicit absence, not permission to silently lose a path. Retained/modified/previously-removed rows reconcile the 67-path historical projection and target bootstrap.
- Reject unaccounted new/deleted/renamed files, export additions, stale signature/default/annotation/class-field/constant AST, missing consumer rationale and unexplained public/private role. Reject dangling task/dependency/enforcement/evidence/shard references and cycles. Reject completed tasks without actual tests/evidence; reject PASS based only on plans or collection failure.
- Check frozen ADR blobs and founding provenance files against target baseline; amendments link from mutable index only. Check GPL license blob. Source-only rows carry metadata, never dirty instruction/research text. Review newly introduced path names for publication suitability.
- Persist tested-content SHA-256 with an **explicit coverage set**, excluding evidence records/digest indexes themselves. Pin baseline blob IDs separately. A digest proves the listed bytes were assessed, not an untested future commit. Refresh evidence after changes; do not write a self-referential HEAD/hash loop.
- Fixture-test missing path, duplicate row, wrong blob, new undeclared export, signature drift, dangling reference/cycle, missing test evidence and modified frozen ADR. A checker that only accepts its happy-path input is insufficient.

## Independent axes and current results

| Axis / task | Required evidence | Current |
|---|---|---|
| A mechanical data | JSON structure, complete census, AST contracts, links, frozen hashes, bounded artifacts | See EV-A-STATIC in evidence; author validation only |
| A04 review | Independent completeness/canonicality/behavior/amendment assessment | PENDING |
| V01 baseline | Full retained CPU suite, interpreter/deps, exact IDs, separate infra/behavior axes | BLOCKED; 16 collection errors, 2 collected, 0 executed |
| Provenance scanner regression | Separate 3 stdlib tests | PASS original environment; not product behavior |
| B/V02 | Static + fidelity + isolation + relevant obligations, baseline comparison | NOT RUN / NOT IMPLEMENTED |
| C01 packaging | Wheel discovery/contents; clean non-editable install outside checkouts; Python-only and MCP-extra; no sys.path tricks; external SDK non-shadowing | DEFERRED |
| D01 Comfy | Pinned artifact, real loader context, node/socket/widget/output/web ABI and offloading compatibility, interpreter/ABI resolution | DEFERRED |
| E01 protocol/live | Protocol-only stdout/diagnostic stderr including startup/error; independent authorized Python/MCP/Comfy real-weight, cancellation/reload/memory scenarios | DEFERRED; no live authorization inferred |
| F01 publication | Separate content/privacy/license/release approval, approved artifacts, preserved prior release/environment and rollback | DEFERRED |

## Coverage and dependencies

Canonical source `pyproject.toml` declares Python >=3.10, transformers==5.13.0, diffusers>=0.39.0, torch/torchvision, accelerate, Pillow, numpy and auto-round>=0.5; optional MCP >=1,<2. Source Comfy requirements intentionally avoid blindly replacing CUDA/ABI-sensitive packages. They are historical constraints, not new target packaging.

Target has no global coverage floor/config. Source `tests/test_kv_cache_coverage_floor.py` requires 100% row coverage **only** for `dgemma/kv_cache.py`, `dgemma/types.py`, Comfy encode/denoise/socket_types when a coverage dataset exists; it skips absent data. B04 must preserve the obligation by ownership, D/E its downstream portion. Neither a skip nor a missing coverage tool satisfies it. No 93% floor is invented. The original baseline lacked coverage tools; measured coverage remains absent.

Rollback during A is a docs checkpoint revert only. Future B uses small coherent checkpoints; no force-update of source history, dependency stack replacement, release or removal of bundled Comfy code before installed replacement proof.
