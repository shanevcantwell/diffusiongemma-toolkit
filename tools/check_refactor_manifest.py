#!/usr/bin/env python3
"""Read-only B02 manifest gate; full mode additionally gates current consumers.

Run: python -B tools/check_refactor_manifest.py --repo CHECKOUT --source-repo SOURCE
Default mode is manifest-only (including native AST/root/candidate accounting).
--mode full reports real pending MCP violations, without granting exceptions.
No model/framework imports, third-party dependencies, refresh, or Git writes.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

# Support both direct execution and namespace-package import in focused tests.
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.consumer_edges import candidate_edges
from tools.refactor_contracts import check_contracts
from tools.refactor_records import content_hashes, historical, indexes, references
from tools.refactor_support import (Invalid, Shapes, blob, git, load, local,
                                    require, tree, unique)


def check(repo, source_repo=None, *, mode='manifest-only', git_repo=None):
    """Inspect candidate bytes at repo; git_repo is a read-only fixture object store.

    Source defaults to repo only when its pinned source objects are available.
    Missing objects report the exact read and ask for --source-repo; no discovery.
    """
    require(mode in {'manifest-only', 'full'}, f'unknown mode {mode}')
    repo = Path(repo).resolve()
    source_repo = Path(source_repo).resolve() if source_repo else repo
    git_repo = Path(git_repo).resolve() if git_repo else repo
    doc = repo / 'docs/refactor'
    m = load(doc / 'manifest.json')
    # Bootstrap schema location only after guarding its shape/path.
    require(isinstance(m, dict) and isinstance(m.get('schema'), str), 'manifest: missing string schema')
    shapes = Shapes(load(local(doc, m['schema'])))
    shapes.check(m, 'manifest', 'manifest')
    c = load(local(doc, m['contracts']))
    t = load(local(doc, m['tasks']))
    e = load(local(doc, m['evidence']))
    h = load(local(doc, m['historical_selection']))
    ec = load(doc / 'evidence-content.json')
    indexes(shapes, c, t, e, h, ec)
    rows = []
    require(len(m['paths']) == len(set(m['paths'])), 'duplicate path shard reference')
    for shard in m['paths']:
        path = local(doc, shard)
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            try:
                row = json.loads(line)
            except ValueError as exc:
                raise Invalid(f'{shard}:{lineno}: malformed JSON: {exc}') from exc
            shapes.check(row, 'path', f'{shard}:{lineno}')
            local(repo, row['source']['path'])
            rows.append(row)
    unique(rows, lambda r: (r['scope'], r['source']['path']), 'path row')
    tasks = references(doc, m, c, rows, t['tasks'], e['records'])
    trees = {}
    for scope, store in [('source', source_repo), ('target', git_repo)]:
        base = m['baselines'][scope]
        actual = tree(store, base['revision'])
        require(git(store, 'rev-parse', base['revision'] + '^{tree}').strip() == base['tree'], f'{scope}: pinned tree mismatch')
        require(len(actual) == base['count'] == m['counts'][scope + '_baseline'], f'{scope}: baseline count mismatch')
        selected = [r for r in rows if r['scope'] == scope + '-baseline']
        require({r['source']['path']: r['source']['blob'] for r in selected} == actual, f'{scope}: baseline path/blob census mismatch')
        require(all(r['source']['repository'] == base['repository'] and r['source']['revision'] == base['revision'] for r in selected), f'{scope}: repository/revision mismatch')
        trees[scope] = actual
    authored = {r['source']['path'] for r in rows if r['scope'] == 'target-authored'}
    require(len(authored) == m['counts']['target_authored'], 'authored count mismatch')
    require(not authored & trees['target'].keys(), 'authored paths cannot replace immutable target origins')
    destinations = set()
    modified = set()
    for row in rows:
        path = row['source']['path']
        dest = row['destination']
        if row['scope'] == 'target-authored':
            require(row['source']['blob'] is None and row['source']['revision'] is None
                    and row['source']['repository'] == m['baselines']['target']['repository']
                    and dest is not None and dest['path'] == path
                    and row['disposition'] == 'target-authored', f'{path}: invalid authored origin/disposition')
        if dest:
            require(dest['repository'] == m['baselines']['target']['repository'], f'{path}: destination repository mismatch')
            require(local(repo, dest['path']).is_file(), f'{path}: missing destination {dest["path"]}')
            destinations.add(dest['path'])
        if row['scope'] == 'target-baseline':
            if row['disposition'] == 'modified':
                require(dest is not None, f'{path}: modified path lacks destination')
                modified.add(dest['path'])
            elif row['disposition'] == 'retained':
                require(dest is not None and blob(local(repo, dest['path'])) == row['source']['blob'], f'{path}: retained blob changed')
            else:
                require(row['disposition'] == 'previously-removed' and dest is None, f'{path}: invalid target disposition')
    # Use candidate worktree with an immutable/read-only object/index store. Git
    # accounts for ignored tooling caches; missing tracked paths still fail above.
    candidate = {p for p in git(git_repo, '--work-tree=' + str(repo), 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split('\0')
                 if p and (repo / p).is_file()}
    require(candidate == destinations, f'candidate file accounting mismatch: missing={sorted(destinations-candidate)}, undeclared={sorted(candidate-destinations)}')
    # These cannot be waived merely by changing a row to "modified".
    frozen = {p for p in trees['target'] if p.startswith(('decisions/adr-cdg-', 'docs/provenance/'))
              or p in {'LICENSE', 'docs/FOUNDING.md'}}
    for path in frozen:
        require((repo / path).is_file() and blob(repo / path) == trees['target'][path], f'{path}: frozen ADR/provenance/LICENSE changed')
    historical(repo, doc, h, trees['source'], trees['target'], rows)
    require(m['counts']['historical_selected'] == 67 and m['counts']['public_exports'] == 30, 'historical/export manifest counts mismatch')
    records = []
    shards = c['public_shards'] + c['error_shards'] + c['owned_shards']
    require(len(shards) == len(set(shards)), 'duplicate contract shard reference')
    for shard in shards:
        data = load(local(doc, shard))
        shapes.check(data, 'contract_shard', shard)
        records.extend(data['records'])
    texts = {}
    def source_text(path):
        if path not in texts:
            texts[path] = git(source_repo, 'show', m['baselines']['source']['revision'] + ':' + path)
        return texts[path]
    check_contracts(records, c['exports'], source_text, trees['source'], m['baselines']['source'], repo, tasks)
    digests = content_hashes(repo, ec, authored, modified)
    paths, violations = candidate_edges(repo, rows, c['exports']) if mode == 'full' else ([], [])
    return dict(status='FAIL' if violations else 'PASS', mode=mode,
                path_rows=len(rows), scopes=dict(Counter(r['scope'] for r in rows)),
                candidate_files=len(candidate), contracts=len(records), public_exports=len(c['exports']),
                content_digests=digests, frozen_files=len(frozen),
                consumer_gate='FAIL' if violations else 'PASS' if mode == 'full' else 'NOT_RUN',
                consumers=paths, violations=violations)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-repo', type=Path, help='repository containing pinned source objects (default: --repo)')
    parser.add_argument('--mode', choices=['manifest-only', 'full'], default='manifest-only')
    args = parser.parse_args(argv)
    try:
        result = check(args.repo, args.source_repo, mode=args.mode)
    except (Invalid, OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, SyntaxError) as exc:
        print(json.dumps(dict(status='FAIL', mode=args.mode, error=str(exc)), indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
