# Common-boundary handoff — Phase A reviewed (A04 PASS)

**Current, 2026-09-16:** the founding stop/fresh-context regroup has been fulfilled. The operator authorized bounded behavior-preserving A/B work. [Phase A records](refactor/manifest.json) are independently reviewed (A04 PASS); **B is not implemented**. V01 original baseline remains **BLOCKED** (16 collection errors, 2 collected, zero executed); the distinct [authorized CPU F0 rerun](refactor/baseline-v01-cpu-f0.md) is **PASS** (295 collected/292 passed/2 skipped/1 strict xfail). Independent **A04 is PASS**; B01 is PENDING, not implemented. The shared-base environment is non-hermetic; pip check exit 1 is not dependency-health PASS. No installable artifact or stable API exists. C–F remain separately deferred.

Resume from [manifest](refactor/manifest.json), [compatibility](refactor/compatibility.md), [gates](refactor/gates.md), [amendment](refactor/adr-019-topology-amendment.md) and [sanitized baseline](refactor/baseline-v01.md). Original founding facts below remain historical, not a renewed unsatisfied authorization gate.

## Phase A review closure — 2026-09-16

Independent review `b996829e-6816-457` found no critical/warning defects. A separate worker supplied the Python/schema/digest execution unavailable in the review sandbox: initial and final non-refresh validator PASS, without product test reruns or environment changes. Detailed scope and limitations are in gates.md (EV-A-REVIEW), separate from author validation. Original baseline and CPU observation records remain immutable; their A04-pending statements describe observation-time status, not the current gate. Next: documentation checkpoint/push by the git lane, then pending B implementation; C–F remain deferred.

## Authoritative live pointers

| Record | Pointer |
|---|---|
| Public repository | https://github.com/shanevcantwell/diffusiongemma-toolkit |
| Founding PR — consult its live merge status and merge commit | https://github.com/shanevcantwell/diffusiongemma-toolkit/pull/2 |
| Fulfilled fresh-context continuation authority (historical gate) | https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/1 |
| Original authorization and run ledger | https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/310 |
| Current bounded refactor ledger | https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3 |
| Original V01 result | https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3#issuecomment-5690521128 |
| Distinct successful CPU F0 result | https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3#issuecomment-5690879296 |
| CPU provisioning grant | https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3#issuecomment-5690837393 |
| Initial reviewed founding commit | `b87b7eb4311a72f2549bc6e897fdfc68eb038bcd` |

The final merged SHA, branch/ref disposition and final source-preservation readback are recorded on the target gate and source ledger after merge. This document deliberately does not embed its own commit SHA: use the PR's merge metadata and those readbacks, rather than a self-referential value. A PR that has not merged is not evidence of a completed mint.

## Immutable provenance

- Source repository: https://github.com/shanevcantwell/ComfyUI-DiffusionGemma
- Source baseline: `fed377afc7b54f03cb7faa4dd798c80c15279d8a`; source tree `83f3876b7ba335b2f8d1585451baacd865f5fb24`.
- Filtered historical main: `6a290854c038194c3f79f038a10a912e36b94c34`; tree `6e51394d7d483559519ed18acdd914953aa8d0c5`.
- 67 matching selected baseline files; 213 mapped commits and 118 dropped; 23 tool-produced commit-message hash substitutions, with original author/committer headers preserved.
- GNU GPLv3 license blob `f288702d2fa16d3cdf0035b15a9fcbc552cd88e7` is unchanged.
- Source worktrees, refs and dirty research were not inputs to the filtered working tree. Only the committed source main lineage and selected paths were retained.

Read [FOUNDING.md](FOUNDING.md), [provenance/SOURCE.md](provenance/SOURCE.md), the selection manifest, commit/ref maps and HEAD blob manifest for reproducible lineage. Historical `ADR-CDG-*` bodies/statuses retain their original identities. No new ADR prefix or registry was invented; no private catalog or corpus was modified.

## What is—and is not—established

The repository/distribution name is `diffusiongemma-toolkit`, the Python namespace is `dgemma`, and the planned optional adapter extra is `diffusiongemma-toolkit[mcp]`.

ComfyUI, the optional MCP adapter and direct Python users will use one public, typed, transport-neutral contract above the engine. Consumers must not reach into engine internals. Existing lifecycle/residency, cancellation, observers, payloads and per-run state placement is preserved. The existing ComfyUI product retains its registry identity, UI, offloading, sockets and workflows. Generic helper ownership remains follow-on work.

This repository is **not installable and has no stable public API or wheel**. Legacy engine/MCP source and selected tests were preserved unchanged. No public-contract implementation, package metadata, extra, entry point, consumer conversion, bugfix, SDK upgrade, lifecycle ratification, version/tag, package release or runtime deployment is delivered by minting.

## Verification boundaries

- Selected-history and source/blob/license fidelity: recorded PASS.
- Retained-history privacy/provenance review: inspect the original and corrected-scan results in [provenance/HISTORY-PUBLICATION-AUDIT.md](provenance/HISTORY-PUBLICATION-AUDIT.md), with its coverage and limitations. The inventory generator's exit zero means collection completed—not automatic PASS.
- Bootstrap scope, authored links/content, evidence checksums, source syntax and focused audit-regression checks: final results are recorded in the founding PR and ledger.
- At mint, the 17 retained product tests were **NOT RUN** due to missing dependencies; no dependencies were installed for that mint. The subsequent original V01 attempt is separately recorded as **BLOCKED** at collection in [baseline-v01.md](refactor/baseline-v01.md), not a behavioral PASS. It remains byte-for-byte preserved beside the distinct CPU F0 PASS evidence (903/1315 statement coverage; no branch measurement or global floor).
- Installed-wheel/public API/optional-extra validation, Comfy compatibility, strict MCP stdio, live/GPU/model execution and product-release readiness are **NOT certified**.

No missing product/runtime gate is silently converted to green. The mint is a provenance and founding-record milestone, not a behavioral release.

## Fresh-context entry

1. Read [AGENTS.md](../AGENTS.md), this handoff, [EXTRACTION_PLAN.md](EXTRACTION_PLAN.md), [ARCHITECTURE.md](../ARCHITECTURE.md), [FOUNDING.md](FOUNDING.md) and the target gate issue.
2. Verify current isolated branch/main/PR and ledger state; A/B continuation and external CPU provisioning were granted, not waiting for a new general authorization. Preserve pre-existing files/research; cleanup only positively run-created artifacts.
3. Phase A independent review and mechanical readback are PASS (see gates.md, EV-A-REVIEW). V01 is PASS; B01 is PENDING and may start under existing bounded authority after the documentation git lane. No B implementation is claimed. Do not install dependencies yourself, fake collection with stubs, or silently fix adjacent defects. The subsequent C–F order remains independently installed package, pinned Comfy conversion, independent certification and separately approved publication.
4. Use small coherent incremental branches/PRs. Keep adjacent legacy findings separately scoped; do not ratify proposed lifecycle policy or fix unrelated defects through extraction.

The source issue links, remaining obligations and complete plan are committed in [EXTRACTION_PLAN.md](EXTRACTION_PLAN.md) and the target continuation issue. A fresh session needs no prior chat or local scratch directory.
