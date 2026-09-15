# Founding handoff

## Stop state

**Publication and review are pending. Implementation is not authorized.**

The selected-history mint and immutable-history audit are complete. Bootstrap documents are authored locally on branch `mint/founding-records`, but the bootstrap change is not yet committed, reviewed, pushed, published, or merged. The staging repository has no remote. After publication and dashboard setup, stop for mandatory HITL; implementation begins only in a fresh context after operator regroup.

## Known immutable stage facts

| Item | Value |
|---|---|
| Public source | https://github.com/shanevcantwell/ComfyUI-DiffusionGemma |
| Authority/dashboard | https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/310 |
| Source baseline | `fed377afc7b54f03cb7faa4dd798c80c15279d8a` |
| Source tree | `83f3876b7ba335b2f8d1585451baacd865f5fb24` |
| Filtered historical `main` | `6a290854c038194c3f79f038a10a912e36b94c34` |
| Filtered tree | `6e51394d7d483559519ed18acdd914953aa8d0c5` |
| Bootstrap branch | `mint/founding-records` from the filtered tip |
| Filtered refs before bootstrap | `main` and local founding branch, both at filtered tip; no remote/tags |
| Filter results | 67 matching tip blobs; 213 mapped commits; 118 dropped; 23 automatic message-hash rewrites |
| License blob | `f288702d2fa16d3cdf0035b15a9fcbc552cd88e7` (unchanged GPLv3) |
| History audit | PASS; 213 commits/messages, 368 text blobs, all 67 paths, zero credential-pattern hits, 521 heuristic occurrences fully classified, no disclosure blocker |
| Source preservation | PASS; compared source snapshots identical |
| Runtime/install/live tests | NOT RUN |

Repository-local evidence is indexed in [provenance/SOURCE.md](provenance/SOURCE.md). The immutable audit explicitly excluded concurrent bootstrap working documents; bootstrap HEAD content and the final founding diff still require review.

## Settled product contract

- Future repository/distribution: `diffusiongemma-toolkit`.
- Public namespace: `dgemma`.
- Future optional install: `diffusiongemma-toolkit[mcp]`.
- ComfyUI-DiffusionGemma retains its existing identity, UI, offloading, sockets, and workflows.
- Direct Python, optional MCP, and Comfy all use one typed transport-neutral contract.
- No consumer reaches into engine internals.
- Lifecycle/residency, cancellation, observers, payloads, and per-run state are preserved rather than redistributed.
- Generic consumer helpers have not been extracted or assigned.

This remains pre-implementation: no package metadata, dependencies, wheel, extra, entry point, stable API, version, tag, release, consumer conversion, boundary repair, bugfix, SDK upgrade, lifecycle policy, or offload change exists here.

## Parent publication checklist

1. Review authored bootstrap documents and links, including privacy/content screening of current HEAD and verification that only declared bootstrap files changed.
2. Verify preserved `dgemma/`, `surfaces/mcp/`, tests, all 17 historical ADR bodies/statuses, and `LICENSE` remain byte-identical to the filtered result.
3. Verify `pyproject.toml` and `requirements.txt` are deleted and no replacement packaging/install stub exists.
4. Commit the bootstrap on `mint/founding-records`; record the real commit below.
5. Reverify target absence, create the authorized public repository, and publish only intended refs without force or tags.
6. Open/review/merge the founding-record PR through normal flow after gates pass.
7. Create the target `user:gate` continuation issue carrying [EXTRACTION_PLAN.md](EXTRACTION_PLAN.md), remaining choices, and the explicit fresh-context stop.
8. Cross-link target repository, PR, issue, and commits from the source authority issue.
9. Fill every pending pointer below and read it back from the public repository/dashboard.
10. Stop for mandatory HITL. Do not open an implementation branch.

## Publication pointers — parent must replace `PENDING`

| Pointer | Value |
|---|---|
| Public repository URL | `PENDING` |
| Filtered public `main` SHA | `PENDING` |
| Founding bootstrap commit SHA | `PENDING` |
| Founding PR URL and disposition | `PENDING` |
| Merged founding `main` SHA | `PENDING` |
| Target `user:gate` issue URL | `PENDING` |
| Source issue cross-link/comment URL | `PENDING` |
| Final public branch/ref readback | `PENDING` |

## Mandatory next-context entry

A fresh implementation context starts by reading [AGENTS.md](../AGENTS.md), this handoff, [EXTRACTION_PLAN.md](EXTRACTION_PLAN.md), [ARCHITECTURE.md](../ARCHITECTURE.md), [FOUNDING.md](FOUNDING.md), and the target gate issue. It must confirm the publication pointers and operator continuation gate before any code or packaging work.

The first implementation activity is Phase A contract/ownership inventory—not consumer repair, package release, lifecycle redesign, or adjacent bugfixing.
