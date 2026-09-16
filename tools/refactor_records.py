"""Cross-record shapes, task graph and nonrecursive content evidence."""
from collections import Counter
import re

from .refactor_support import (INTEGER, STRING, VERSION, array, load, local,
                               obj, require, sha, unique)


def indexes(shapes, contracts, tasks, evidence, history, content):
    shapes.check(contracts, obj(
        schema_version=VERSION, status={'enum': ['AUTHORED_FOR_REVIEW', 'PASS']},
        expression_format=STRING, exports=array(STRING), public_shards=array(STRING),
        error_shards=array(STRING), owned_shards=array(STRING), error_coverage=STRING,
        callbacks=obj(**{k: STRING for k in ('load_model.check_interrupted', 'run_diffusion.on_frame',
                    'run_diffusion.should_cancel', 'run_diffusion.logit_hook')}),
        identity_rule=STRING, non_exports=array(STRING), related=array(STRING)), 'contracts')
    shapes.check(tasks, obj(schema_version=VERSION, tasks=array({'$ref': '#/$defs/task'})), 'tasks')
    shapes.check(evidence, obj(schema_version=VERSION, ledger=STRING,
                              records=array({'$ref': '#/$defs/evidence'})), 'evidence')
    shapes.check(history, obj(schema_version=VERSION, selected_count=INTEGER,
        selection=STRING, historical_manifest=STRING, selection_sha256=STRING,
        counts=obj(retained=INTEGER, modified=INTEGER, **{'previously-removed': INTEGER}),
        rows=array(obj(path=STRING, source_blob=STRING,
            target_blob={'type': ['string', 'null']}, outcome={'enum': ['retained', 'modified', 'previously-removed']}))), 'history')
    shapes.check(content, obj(schema_version=VERSION, algorithm={'enum': ['sha256']},
        coverage_semantics=STRING, excluded=array(STRING),
        coverage=array(obj(path=STRING, sha256=STRING))), 'content')


def references(doc, manifest, contracts, rows, tasks, evidence):
    ids = unique(tasks, lambda t: t['id'], 'task ID')
    eids = unique(evidence, lambda e: e['id'], 'evidence ID')
    for t in tasks:
        label = t['id']
        require(set(t['dependencies']) <= ids.keys(), f'{label}: dangling dependency')
        require(set(t['evidence']) <= eids.keys(), f'{label}: dangling evidence')
        require(t['enforcement_tests'], f'{label}: missing enforcement tests')
        if t['status'] == 'PASS':
            require(all(ids[d]['status'] == 'PASS' for d in t['dependencies']), f'{label}: PASS with incomplete prerequisite')
            require(any(eids[e]['status'] == 'PASS' and label in eids[e]['tasks'] for e in t['evidence']),
                    f'{label}: PASS missing actual PASS evidence')
            require(any(not text.lower().startswith(('planned:', 'future:')) for text in t['enforcement_tests']),
                    f'{label}: PASS with planned tests only')
    for e in evidence:
        require(set(e['tasks']) <= ids.keys(), f"{e['id']}: dangling evidence task")
        for path in e['records']:
            require(local(doc, path).is_file(), f"{e['id']}: missing evidence record {path}")
        if e['status'] == 'PASS':
            observed = e['observed'].lower()
            require(e['records'] and observed.strip() and not observed.startswith(('planned', 'not run')),
                    f"{e['id']}: PASS missing observed evidence")
            require(not any(term in observed for term in ('0 executed', 'zero executed', 'collection failed', 'collection failure', 'exit 2')),
                    f"{e['id']}: PASS contradicted by failed/zero-execution observation")
    for row in rows:
        require(row['tasks'] and set(row['tasks']) <= ids.keys(), f"{row['source']['path']}: dangling task")
        require(all(row[k].strip() for k in ('reason', 'owner', 'role')), f"{row['source']['path']}: missing ownership/rationale")
    done = set()
    def visit(key, stack):
        require(key not in stack, f'task cycle: {" -> ".join((*stack, key))}')
        if key not in done:
            for dep in ids[key]['dependencies']:
                visit(dep, (*stack, key))
            done.add(key)
    for key in ids:
        visit(key, ())
    paths = manifest['records'] + [manifest[k] for k in ('schema', 'contracts', 'tasks', 'evidence', 'historical_selection')]
    paths += contracts['related']
    for path in paths:
        require(local(doc, path).is_file(), f'missing referenced record {path}')
    return ids


def historical(repo, doc, history, source, target, rows):
    require(history['selected_count'] == len(history['rows']) == 67, 'historical projection must contain 67 paths')
    selected = unique(history['rows'], lambda r: r['path'], 'historical path')
    selection = local(repo, str((doc / history['selection']).relative_to(repo)))
    require(sha(selection) == history['selection_sha256'], 'historical selection hash mismatch')
    require(set(selection.read_text().splitlines()) == selected.keys(), 'historical selection paths mismatch')
    require(dict(Counter(r['outcome'] for r in history['rows'])) == history['counts'], 'historical outcome counts mismatch')
    for path, row in selected.items():
        require(source.get(path) == row['source_blob'] and target.get(path) == row['target_blob'], f'{path}: historical blob mismatch')
        outcome = 'previously-removed' if path not in target else 'retained' if source[path] == target[path] else 'modified'
        require(row['outcome'] == outcome, f'{path}: historical outcome mismatch')
    for row in rows:
        require(row['historical_selected'] == (row['source']['path'] in selected), f"{row['source']['path']}: historical selection flag mismatch")


def content_hashes(repo, content, authored, modified):
    # Explicit policy, not a recursive scan or an exemption for arbitrary JSON.
    excluded = {'docs/refactor/evidence-content.json', 'docs/refactor/evidence-content-a04.json',
                'docs/refactor/evidence.json', 'docs/refactor/baseline-v01.json',
                'docs/refactor/baseline-v01-cpu-f0.json'}
    require(len(content['excluded']) == len(excluded) and set(content['excluded']) == excluded,
            'coverage exclusions differ from explicit nonrecursive policy')
    covered = unique(content['coverage'], lambda r: r['path'], 'coverage path')
    require(covered.keys() == (authored | modified) - excluded,
            f'coverage set mismatch: missing={sorted((authored|modified)-excluded-covered.keys())}, extra={sorted(covered.keys()-((authored|modified)-excluded))}')
    for path, record in covered.items():
        require(sha(local(repo, path)) == record['sha256'], f'{path}: content SHA-256 mismatch')
    # Historical evidence remains byte-frozen, not rechecked as current content.
    archive = repo / 'docs/refactor/evidence-content-a04.json'
    require(sha(archive) == 'e7d015bc510d1b38e1db4eb272ded85aa644f114bf72bf6b85b47459a5786741',
            'A04 historical evidence archive changed')
    # Preserve the actual historical records, not only their self-reported hashes.
    baseline_hashes = {
        'baseline-v01.json': '37401b87c10897de0a9c3d83f593592dbd672cee1c6efa9460961687a82e524d',
        'baseline-v01.md': 'e06c3483b6159f588274a484cd8976224bffb856cdcd31236e334eb228e41065',
        'baseline-v01-cpu-f0.json': '2738f5310141416a384f71f56b8e91065b3448360b94b466f6c7b111100777be',
        'baseline-v01-cpu-f0.md': '770a6f994dc2953209d477730b15ae8d223a3b7d9dafaa06fe2e417d0d61e732',
    }
    for name, digest in baseline_hashes.items():
        require(sha(repo / 'docs/refactor' / name) == digest, f'{name}: original baseline evidence changed')
    for path in authored | modified:
        if path.endswith('.md'):
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', (repo / path).read_text()):
                if re.match(r'[a-zA-Z]+:', link) or link.startswith('#'):
                    continue
                dest = ((repo / path).parent / link.split('#')[0]).resolve()
                require(dest.is_relative_to(repo) and dest.exists(), f'{path}: dangling local link {link}')
    return len(covered)
