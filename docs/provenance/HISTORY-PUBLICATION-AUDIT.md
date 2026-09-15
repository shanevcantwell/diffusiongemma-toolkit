# History Publication Privacy Audit — filtered `main`

**Original source-history scan:** PASS — no credential, private-key, token, credential-bearing URL, private-corpus blob, binary/weight payload, or other disclosure blocker was identified in the audited object set. This historical verdict applies only to the original scan's object scope, method, and recorded inventory time (`2026-09-15T21:31:42.813328+00:00`) and its completed manual classifications. It authorizes no posting by itself; no public operation was performed.

**Corrected quoted-key rescan:** MANUAL ASSESSMENT COMPLETE — the corrected inventory was generated at `2026-09-15T22:10:05.108405+00:00`. Its machine status is `collection_status=COMPLETE` and `assessment_status=NOT_ASSESSED`; exit 0 certifies collection only. Subsequent manual assessment classified every candidate and identified no disclosure blocker. This result comes from the manual assessment recorded here, not an automatic generator verdict.

**Audited ref/object boundary:** both scans covered `refs/heads/main` at `6a290854c038194c3f79f038a10a912e36b94c34`, derived from source baseline `fed377afc7b54f03cb7faa4dd798c80c15279d8a`. They read Git objects, not concurrent checkout files.

## Verdict and severity

| Measure | Original scan | Corrected rescan | Result |
|---|---:|---:|---|
| Critical / High / Medium / Low disclosure findings | 0 | 0 | No blocker |
| Informational reviewed scanner occurrences | 521 | 521 | All classified; 0 unclassified |
| Unique pattern+digest review groups | 73 | 73 | Exact set retained |
| Added / removed occurrences | — | 0 / 0 | No candidate delta |
| `generic_secret_assignment` occurrences | 0 | 0 | No quoted-key candidate was emitted |

In both inventories, the 521 heuristic occurrences reduce to the same 73 unique pattern+digest review groups: 497 occurrences are public GitHub/project/model/document references, 19 are placeholders or standard local paths, 3 are intentional references to the named private-annex namespace in the publication-policy ADR, and 2 are source/test identifiers. Every corrected-rescan occurrence exactly matched an original manually classified occurrence on pattern, digest, axis, object, path, line, byte count, and redacted representation; classifications were carried only on that grounded basis. There were no new quoted-key hits to inspect. No hit contains an annex URL, host, credential, or private-corpus content. Authorship contains source-public identity metadata (5 author identity tuples, including two personal Gmail addresses, plus 6 committer tuples); it was preserved rather than arbitrarily redacted.

## Scope and containment

- Allowlist: 67 unique relative paths; SHA-256 `18aa059dc5567ea8e13a715d5456b8d760207097e3731a36070c2685e8a6d0bb`.
- Every path in every retained commit tree was enumerated: 8,898 tree-entry occurrences, 67 unique historical paths, all 67 allowlisted. Tip has exactly the same 67 paths.
- Retained history: 213 commits (1 root, 179 one-parent, 33 two-parent), 358 trees, 368 unique blobs; 939 reachable objects total.
- Point-in-time refs: only `refs/heads/main` and `refs/heads/mint/founding-records`; both resolved to the audited SHA. No remotes, tags, remote-tracking refs, or stash refs. All 939 packed objects were reachable from audited `main`; `git fsck --full --strict` passed and the no-reflog unreachable census was empty.
- Publication must target the audited `main` SHA/ref only, not mirror future branch movement. The active branch working tree/index was intentionally outside scope.

## Provenance and license

All 213 filtered commits map uniquely to commits reachable from the source baseline. For every mapped commit, the complete filtered tree (path, mode, type, blob ID) exactly equals the 67-path allowlist projection of that source commit, and author/committer headers are unchanged. All 368 retained blob IDs are reachable from the source baseline, so no dirty/untracked/private blob was introduced. Of 213 messages, 190 are byte-identical to source; all 23 differences were mechanically verified as only `git-filter-repo` mapped abbreviated commit-ID substitutions (0 unexplained tokens).

`LICENSE` is allowlisted and retained byte-for-byte: source and filtered blob `f288702d2fa16d3cdf0035b15a9fcbc552cd88e7`, mode `100644`.

## Blob, size, and MIME inventory

All 368 unique blobs (7,412,728 uncompressed bytes) are valid UTF-8, contain no NUL byte, and classify as text; 0 binary blobs. Extension-derived MIME inventory (libmagic unavailable): 174 Python, 153 Markdown, 41 plain text. Maximum blob is 91,213 bytes; median 14,816.5; p95 60,184; 0 exceed 100 KiB or 1 MiB. No historical path has a model-weight, checkpoint, tensor, archive, database, or common binary extension.

## Secret/private-reference scan

No trusted scanner was installed (`gitleaks`, `trufflehog`, `detect-secrets`, and `git-secrets` absent), so the original run of `audit-history-publication.py` collected a byte-scan inventory over **all 368 unique retained blobs, including any binary bytes, and all 213 complete commit messages**. It used explicit patterns for private-key/PGP headers; GitHub/GitLab/Slack/Google/AWS/Stripe/npm/PyPI/Hugging Face token formats; JWTs; Authorization headers; generic secret/password/API-key assignments; netrc passwords; credential-userinfo and credential-query URLs; POSIX/Windows/private-config paths; file URLs; and base64/hex entropy candidates. The generator is collection-only; the historical PASS came from the manual assessment recorded in this report, not from its successful exit status.

Credential/private-key/token/credential-URL patterns produced 0 hits in the original scan. Review candidates were 503 entropy matches, 16 private-config-path matches, and 2 POSIX-home matches. Every original occurrence was annotated and manually classified in the original audit dossier.

The corrected generator reran over the same complete scope: 213 commits and complete commit messages, 368 unique blobs (all text), 67 historical paths, 8,898 tree-entry occurrences, and 939 reachable objects. It again emitted 503 entropy matches, 16 private-config-path matches, and 2 POSIX-home matches, with no generic-secret-assignment candidate and no added or removed occurrence. Its provenance inventory mapped all 213 retained commits uniquely to source commits reachable from the baseline, with complete tree projections and author/committer headers matching; provenance failures and non-allowlisted historical paths were both 0. The heuristic still is not a parser and cannot establish absence of every secret format.

## Explicit exclusions and limitations

**Scanned:** all objects reachable from immutable filtered `main`; every historical tree path; every unique retained blob byte; every complete retained commit message; author/committer metadata; source-baseline projection and blob provenance; ref containment; license; size/MIME/extension anomalies.

**Not scanned:** concurrent checkout/index/untracked working documents; excluded source paths and their blobs; other source refs, private corpus/annex, failed first-stage repository contents, or external services. No provider-side token validity/revocation check, OCR/steganography, archive decompression, encrypted-content inspection, or unknown proprietary-token detection was possible. There were no retained binaries/archives to unpack. MIME is content-class plus Python extension inference because `file`/libmagic was unavailable. This is a pre-publication privacy/provenance gate, **not** a runtime, dependency, model-quality, safety, or correctness claim.

## Durable evidence

The original audit dossier and corrected-rescan dossier contain the detailed inventories, review worksheets, and procedural materials, including per-occurrence and pattern+digest classifications. Those detailed artifacts are deliberately omitted from the compact public bundle for the screening reasons stated in [SOURCE.md](SOURCE.md); they are not claimed to sit beside this report, and the original evidence was preserved unchanged.

The bundled public evidence consists of this manually assessed report, the corrected collection output `audit-summary.json`, the collection-only `audit-history-publication.py` method, its stdlib regression test `test_audit_inventory.py`, the extraction maps and manifest, and source notes. The summary deliberately retains `assessment_status=NOT_ASSESSED`: manual assessment lives in this report, not in the inventory generator's output. `AUDIT-CHECKSUMS.sha256` authenticates the changed bundled audit evidence and regression test.
