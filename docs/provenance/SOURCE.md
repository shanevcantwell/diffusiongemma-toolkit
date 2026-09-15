# Source and extraction provenance

## Public source

- Source repository: https://github.com/shanevcantwell/ComfyUI-DiffusionGemma
- Mint authority: https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/310
- Selected source ref: source `main` only
- Source baseline commit: `fed377afc7b54f03cb7faa4dd798c80c15279d8a`
- Source baseline tree: `83f3876b7ba335b2f8d1585451baacd865f5fb24`
- Filtered historical tip: `6a290854c038194c3f79f038a10a912e36b94c34`
- Filtered historical tree: `6e51394d7d483559519ed18acdd914953aa8d0c5`
- Staging creation recorded: `2026-09-15T21:23:38Z`
- License: GNU GPL v3; `LICENSE` blob retained unchanged as `f288702d2fa16d3cdf0035b15a9fcbc552cd88e7`

The selected history also retains source prose crediting the public [semantic-kinematics-mcp](https://github.com/shanevcantwell/semantic-kinematics-mcp) project as an influence on the historical MCP shape. That credit is provenance, not imported history.

## Ref and path selection

A fresh non-local, single-branch, no-tags clone was made from source `main`, pinned to the baseline above. Before filtering it contained only local `main`, `origin/main`, and symbolic `origin/HEAD`, all at the selected baseline. The normal `git-filter-repo` flow removed `origin`. The filtered result contained only `refs/heads/main` and no remote.

No source tag, archive, rescue, draft, pull, remote-tracking, or unrelated branch ref was selected. Dirty/untracked research and all paths outside the 67-entry allowlist were excluded.

The literal allowlist is [selected-paths.txt](selected-paths.txt), SHA-256 `18aa059dc5567ea8e13a715d5456b8d760207097e3731a36070c2685e8a6d0bb`.

## Tool and command

Filtering used `git-filter-repo` package `2.47.0`, executable version `a40bce548d2c`, with the normal fresh-clone safety check and without `--force`.

Reproducible invocation shape (placeholders are public/reviewer-selected paths, not original machine paths):

```sh
set -eu
BASE=fed377afc7b54f03cb7faa4dd798c80c15279d8a
SOURCE=https://github.com/shanevcantwell/ComfyUI-DiffusionGemma.git
STAGE=/path/to/new/disposable-clone
ALLOWLIST=/path/to/selected-paths.txt
TOOL=git-filter-repo

test ! -e "$STAGE"
git clone --no-local --single-branch --branch main --no-tags -- "$SOURCE" "$STAGE"
test "$(git -C "$STAGE" rev-parse refs/heads/main)" = "$BASE"
test "$(git -C "$STAGE" remote)" = origin
test "$(git -C "$STAGE" rev-parse refs/remotes/origin/main)" = "$BASE"
(
  cd "$STAGE"
  "$TOOL" --paths-from-file "$ALLOWLIST"
)
test -z "$(git -C "$STAGE" remote)"
test "$(git -C "$STAGE" for-each-ref --format='%(refname)' refs/heads refs/remotes refs/tags)" = refs/heads/main
```

## Repository-local evidence

- [commit-map](commit-map) — unedited filter-repo old→new commit map.
- [ref-map](ref-map) — unedited filter-repo ref map.
- [HEAD-MANIFEST.tsv](HEAD-MANIFEST.tsv) — source and pre-bootstrap filtered blob equality for all 67 selected tip paths; all matched.
- [HISTORY-PUBLICATION-AUDIT.md](HISTORY-PUBLICATION-AUDIT.md) — complete sanitized audit report for immutable filtered history.
- [audit-summary.json](audit-summary.json) — compact machine-readable history inventory.
- [audit-history-publication.py](audit-history-publication.py) — deterministic, collection-only inventory generator used to enumerate and scan selected history; exit 0 means collection succeeded, not audit PASS.
- [test_audit_inventory.py](test_audit_inventory.py) — stdlib regression evidence for generic quoted/unquoted assignment matching, exclusions, and machine-readable collection/assessment status semantics; it extracts literals with AST and does not import the CLI or run Git.
- [AUDIT-CHECKSUMS.sha256](AUDIT-CHECKSUMS.sha256) — verified hashes for the included audit records and regression evidence.

Detailed scanner match inventories and review worksheets were deliberately not published in this compact provenance bundle: some source-side evidence contains local paths or raw/redacted match context requiring separate publication screening. The original and corrected-rescan dossiers remain external, not beside this public report; the original evidence was preserved unchanged. The included report, corrected summary, method, maps, manifest, regression evidence, and checksums carry the public verification record without making an external temporary directory the sole evidence. In `audit-summary.json`, `collection_status: COMPLETE` and `assessment_status: NOT_ASSESSED` are the corrected generator's actual output, and `scan_findings_unclassified: 521` is its pre-assessment candidate count. The manual classification and no-blocker conclusion are recorded in `HISTORY-PUBLICATION-AUDIT.md`, not invented as an automatic PASS in the summary.

## Verified extraction results

- 67 selected tip paths; all 67 source blobs equal their pre-bootstrap filtered blobs.
- 213 retained commits from 331 source-main commits; 118 no-selected-effect commits dropped.
- Author and committer headers unchanged for all retained commits.
- 190 messages byte-identical; 23 changes mechanically verified as only mapped abbreviated commit-ID substitutions.
- Source snapshot comparison passed: refs, worktrees, remotes, status, and dirty-file fingerprints remained identical.
- `git fsck --full --strict` passed on the audited filtered history.
- The original immutable-history scan passed for its recorded inventory time (`2026-09-15T21:31:42.813328+00:00`), object scope, method, and pattern set: 213 commits/messages, 368 unique blobs (all text), 67 historical paths, no credential-pattern hits, and all 521 heuristic occurrences manually classified with no disclosure blocker.
- The corrected quoted-key inventory was generated at `2026-09-15T22:10:05.108405+00:00` over the same 213 commits/messages, 368 unique blobs, 67 historical paths, and 939 reachable objects. Collection completed with generator assessment `NOT_ASSESSED`; manual assessment classified all 521 occurrences in the same 73 exact pattern+digest groups, found 0 added or removed occurrences and 0 generic-secret-assignment hits, and identified no disclosure blocker. All 213 source mappings passed complete tree-projection and author/committer checks.

## Evidence limits

Neither immutable-history scan covered bootstrap working-tree documents authored after the filtered tip, excluded source paths/refs, external services, or runtime/dependency/model behavior. No trusted third-party secret scanner was installed; the included deterministic inventory generator was used and its candidates required manual assessment. Its assignment heuristic is not a language parser, and unknown or transformed secret formats can evade it. Bootstrap HEAD content still requires its separate publication review. No runtime, install, GPU, model-quality, safety, or correctness claim follows from this provenance audit.
