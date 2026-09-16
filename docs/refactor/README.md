# Common-boundary continuity records

**A04 reviewed; B01 root re-exports PASS, 2026-09-16.** B01 adds root re-exports and 63 focused tests; no packaging/Comfy implementation. No stable API or installable artifact. A/B authorization and isolated CPU environment provisioning authorization are satisfied; V01 has distinct [CPU F0 PASS evidence](baseline-v01-cpu-f0.md); independent A04 review is PASS; [B01](b01.md) is PASS; B02–B04/V02 remain pending. The original BLOCKED result is preserved; shared-base pip check exit 1 is not dependency-health PASS. Start with [manifest.json](manifest.json), [gates](gates.md) and the [live ledger](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3).

## How to resume without local scratch

- [Manifest](manifest.json): versioned index, immutable source/target trees, shards and counts.
- [Tasks](tasks.json): stable dependencies, owners, current states, test obligations and evidence IDs.
- [Contracts](contracts.json): ordered AST parameter/default/annotation records, dataclass fields, constants, callback semantics, consumer evidence and explicit raise inventory. Follow its bounded shards; internal ownership signatures are not new public exports.
- [Compatibility](compatibility.md): native identity/mutation/lifetime, adapter-owned state and separate known defects.
- [Topology amendment](adr-019-topology-amendment.md): scoped correction to frozen historical MCP ADR-CDG-019, not a new numbered ADR.
- [Evidence](evidence.json): observed vs pending axes. [Original V01](baseline-v01.md) retains the actual blocked result; the distinct [CPU F0 rerun](baseline-v01-cpu-f0.json) records PASS with two skips and one strict xfail, never relabeling the original.
- [Historical selection](historical-selection.json): exact reconciliation of the 67 filtered source paths with target bootstrap, including rewritten docs and removed packaging.

## Path accounting semantics

Each JSONL row follows `$defs.path` in [manifest.schema.json](manifest.schema.json). Scope keys are `source-baseline`, `target-baseline`, `target-authored`; uniqueness is `(scope, source.path)`, not path alone. The same source/target path legitimately has two provenance rows. Source and target baselines are complete committed tree censuses (202 and 79 paths), not a sampled subset. Dirty/untracked source research is outside both immutable baselines and was neither read as a body nor copied.

`source` is the row's origin repository/ref/path/blob; target baseline rows therefore originate in the target. `destination` records the current accounting destination, **not a performed move**. Null means no target copy. A source-only deferred path remains source-owned, with its task identifying where later review belongs. Target-authored records have null revision/blob and are included in their own path census without recursive self-hashes. Implemented B01 files are accounted; later B/C files remain tasks, not falsely claimed existing files.

- **retained:** baseline bytes kept in the current target candidate.
- **modified:** baseline path changed in the current candidate, including B01 root exports; source/target scope pins its origin. The separate historical-selection record remains the immutable founding projection.
- **target-authored:** new record or test absent from the pinned target baseline; null origin revision/blob, explicit ownership/tasks.
- **source-only-deferred:** source code/test/config/asset responsibility accounted, no target copy now.
- **excluded:** corpus/history outside selected extraction; metadata only, no body publication or import.
- **previously-removed:** selected source packaging path deleted by founding bootstrap, not deleted by A.

Ownership assigns responsibility, not extraction authority. `public-root` is only the root module; canonical types/functions remain defined in `private-engine` files. `test-obligation` records preserve source-only tests even where the retained 17 files omit them. Analysis/audit/run-log helpers remain downstream; source workflow/assets stay source-owned. No source metadata pathname in the pinned census was identified as containing a credential, personal local path or genuinely private identifier; corpus rows publish names/blob IDs only. This metadata review does not certify excluded bodies or all source history.

## Validation and integrity

The schema is JSON Schema 2020-12; A's correction validation uses the already provisioned jsonschema validator for schema-defined objects plus external stdlib cross-record assertions; no dependency installation. There is no new repository checker, test file or required dependency in A. [Gates](gates.md) specifies B's durable checker and negative fixtures. Consumers must not depend on the external authoring scripts; all inputs needed to reconstruct the check are committed records and immutable public Git trees.

`evidence-content.json` lists SHA-256 and its explicit current B01 assessed coverage set. The byte-preserved `evidence-content-a04.json` is historical A04 evidence, not a current-content assertion. The current index excludes both digest indexes, evidence.json and both baseline JSON evidence records to avoid recursive evidence hashes; both baseline Markdown records remain covered. New CPU JSON lock/artifact digests and original frozen-baseline hashes are independently checked. Baseline integrity uses Git blob IDs independently, including every frozen ADR and founding provenance file. A static PASS certifies data/accounting/AST/link/size checks only; independent review, runtime behavior, coverage, installed artifact and live axes remain distinct.
