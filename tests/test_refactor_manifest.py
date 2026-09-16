"""Portable read-only checker fixtures. Set DGEMMA_SOURCE_REPO for source objects.

Copies candidate files into pytest's external basetemp; never edits real records.
Git reads use the original immutable object/index store and the copied worktree.
"""
import json
import os
from pathlib import Path
import shutil

import pytest

from tools.check_refactor_manifest import check, main
from tools.refactor_support import Invalid, Shapes, git, load

REPO = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('DGEMMA_SOURCE_REPO', REPO))


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


@pytest.fixture
def candidate(tmp_path):
    root = tmp_path / 'candidate'
    root.mkdir()
    # Enumerate current candidate, including new B02 files, without copying .git,
    # caches, or hidden machine state into fixtures.
    for name in git(REPO, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split('\0'):
        if name and (REPO / name).is_file():
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / name, dest)
    return root


def verify(root, **kwargs):
    return check(root, SOURCE, git_repo=REPO, **kwargs)


def edit_json(root, name, edit):
    path = root / 'docs/refactor' / name
    data = load(path)
    edit(data)
    save(path, data)


def edit_rows(root, edit):
    doc = root / 'docs/refactor'
    for shard in load(doc / 'manifest.json')['paths']:
        path = doc / shard
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        edit(rows)
        path.write_text(''.join(json.dumps(r) + '\n' for r in rows))


def test_current_candidate_manifest_and_full_modes():
    result = verify(REPO)
    assert result['status'] == 'PASS' and result['consumer_gate'] == 'NOT_RUN'
    full = verify(REPO, mode='full')
    assert full['status'] == 'FAIL' and full['consumer_gate'] == 'FAIL'
    assert full['violations'] and full['consumers']


@pytest.mark.parametrize('case,diagnostic', [
    ('missing-file', 'missing destination'),
    ('undeclared-file', 'undeclared='),
    ('missing-row', 'baseline path/blob census'),
    ('duplicate-row', 'duplicate path row'),
    ('wrong-blob', 'baseline path/blob census'),
    ('new-export', 'undeclared root export'),
    ('all-export', 'exact ordered 30 root exports'),
    ('signature', 'stale AST'),
    ('annotation', 'stale AST'),
    ('field', 'stale AST'),
    ('constant', 'stale AST'),
    ('owned-method', 'stale AST'),
    ('dangling', 'dangling dependency'),
    ('cycle', 'task cycle'),
    ('no-evidence', 'PASS missing actual PASS evidence'),
    ('planned-pass', 'PASS with planned tests only'),
    ('frozen', 'frozen ADR/provenance/LICENSE'),
    ('cross-shard-id', 'duplicate contract ID across shards'),
    ('unqualified', 'class-qualified'),
    ('rationale', 'missing consumer rationale'),
    ('callsite', 'stale consumer callsite'),
    ('hash', 'content SHA-256 mismatch'),
    ('recursive', 'coverage exclusions'),
    ('coverage-omission', 'coverage set mismatch'),
    ('dangling-shard', 'No such file'),
    ('a04-archive', 'A04 historical evidence archive changed'),
])
def test_negative_candidate_fixtures(candidate, case, diagnostic):
    root = candidate
    if case == 'missing-file':
        (root / 'dgemma/config.py').unlink()
    elif case == 'undeclared-file':
        (root / 'surprise.py').write_text('')
    elif case in {'missing-row', 'duplicate-row', 'wrong-blob'}:
        def change(rows):
            row = next((r for r in rows if r['scope'] == 'source-baseline' and r['source']['path'] == 'dgemma/model.py'), None)
            if row:
                if case == 'missing-row': rows.remove(row)
                elif case == 'duplicate-row': rows.append(row.copy())
                else: row['source']['blob'] = '0' * 40
        edit_rows(root, change)
    elif case in {'new-export', 'all-export'}:
        path = root / 'dgemma/__init__.py'
        text = path.read_text()
        path.write_text(text + '\nsurprise = 1\n' if case == 'new-export' else text.replace('"load_model",', '"unapproved",'))
    elif case in {'signature', 'annotation', 'rationale', 'callsite'}:
        def change(data):
            r = data['records'][0]
            if case == 'signature': r['parameters'][0]['default'] = "'drift'"
            elif case == 'annotation': r['parameters'][0]['annotation'] = 'bytes'
            elif case == 'rationale': r['consumer_reason'] = ''
            else: r['consumer_uses'][0]['line'] = 999999
        edit_json(root, 'contracts/public-01.json', change)
    elif case in {'field', 'constant', 'owned-method'}:
        for path in (root / 'docs/refactor/contracts').glob('*.json'):
            data = load(path)
            match = next((r for r in data['records'] if
                (case == 'field' and r['kind'] == 'type' and r['fields']) or
                (case == 'constant' and r['kind'] == 'constant') or
                (case == 'owned-method' and r['kind'] == 'owned-callable')), None)
            if match:
                if case == 'field': match['fields'][0]['default'] = '123'
                elif case == 'constant': match['expression'] = '123'
                else: match['returns'] = 'bytes'
                save(path, data)
                break
    elif case in {'dangling', 'cycle', 'no-evidence', 'planned-pass'}:
        def change(data):
            task = data['tasks'][0]
            if case == 'dangling': task['dependencies'] = ['NO-SUCH-TASK']
            elif case == 'cycle': task['dependencies'] = ['A02']
            elif case == 'no-evidence': task['evidence'] = []
            else: task['enforcement_tests'] = ['planned: imaginary tests']
        edit_json(root, 'tasks.json', change)
    elif case == 'frozen':
        path = next((root / 'decisions').glob('adr-cdg-*.md'))
        path.write_text(path.read_text() + '\nUnauthorized rewrite\n')
        edit_rows(root, lambda rows: [r.update(disposition='modified') for r in rows
                   if r['scope'] == 'target-baseline' and r['source']['path'] == path.relative_to(root).as_posix()])
    elif case == 'cross-shard-id':
        record_id = load(root / 'docs/refactor/contracts/public-01.json')['records'][0]['id']
        edit_json(root, 'contracts/errors-01.json', lambda d: d['records'][0].update(id=record_id))
    elif case == 'unqualified':
        edit_json(root, 'contracts/owned-02.json', lambda d: d['records'][0].update(name='__call__', id='OWN-composite-__call__'))
    elif case == 'hash':
        path = root / 'docs/refactor/compatibility.md'
        path.write_text(path.read_text() + '\nUnassessed text\n')
    elif case == 'recursive':
        edit_json(root, 'evidence-content.json', lambda d: d['excluded'].remove('docs/refactor/evidence-content.json'))
    elif case == 'coverage-omission':
        edit_json(root, 'evidence-content.json', lambda d: d['coverage'].pop())
    elif case == 'dangling-shard':
        edit_json(root, 'contracts.json', lambda d: d['public_shards'].append('contracts/missing.json'))
    elif case == 'a04-archive':
        path = root / 'docs/refactor/evidence-content-a04.json'
        path.write_text(path.read_text() + '\n')
    with pytest.raises((Invalid, OSError), match=diagnostic):
        verify(root)


@pytest.mark.parametrize('name,edit,diagnostic', [
    ('manifest.json', lambda d: d.pop('counts'), 'missing required keys'),
    ('tasks.json', lambda d: d['tasks'][0].update(status='DONE'), 'expected enum'),
    ('tasks.json', lambda d: d.update(tasks={}), 'expected.*array'),
    ('contracts.json', lambda d: d.update(exports=None), 'expected.*array'),
    ('contracts/public-01.json', lambda d: d['records'][0].update(line=True), 'expected.*integer'),
    ('evidence.json', lambda d: d['records'][0].update(records=42), 'expected.*array'),
])
def test_malformed_shapes_useful_diagnostics(candidate, name, edit, diagnostic):
    edit_json(candidate, name, edit)
    with pytest.raises(Invalid, match=diagnostic):
        verify(candidate)


def test_cli_malformed_json_no_traceback(candidate, capsys):
    (candidate / 'docs/refactor/manifest.json').write_text('{')
    assert main(['--repo', str(candidate), '--source-repo', str(SOURCE)]) == 1
    output = json.loads(capsys.readouterr().out)
    assert output['status'] == 'FAIL' and 'manifest.json' in output['error']


def test_unsupported_schema_vocabulary_fails_closed():
    with pytest.raises(Invalid, match='unsupported schema'):
        Shapes({'$defs': {}}).check('x', {'pattern': 'x'})


def test_current_native_ast_not_just_historical_source(candidate):
    path = candidate / 'dgemma/model.py'
    path.write_text(path.read_text().replace('local_files_only: bool = False,\n    check_interrupted:',
                                           'local_files_only: bool = True,\n    check_interrupted:'))
    edit_rows(candidate, lambda rows: [r.update(disposition='modified') for r in rows
              if r['scope'] == 'target-baseline' and r['source']['path'] == 'dgemma/model.py'])
    with pytest.raises(Invalid, match='candidate API-load_model: stale AST'):
        verify(candidate)


@pytest.mark.parametrize('observation', ['Planned only', '0 executed; collection failed, exit 2'])
def test_pass_not_based_on_plan_or_collection_failure(candidate, observation):
    edit_json(candidate, 'evidence.json', lambda d: d['records'][0].update(observed=observation))
    with pytest.raises(Invalid, match='PASS (missing observed|contradicted)'):
        verify(candidate)


def test_pass_without_actual_record(candidate):
    edit_json(candidate, 'evidence.json', lambda d: d['records'][0].update(records=[]))
    with pytest.raises(Invalid, match='PASS missing observed evidence'):
        verify(candidate)


def test_baseline_json_cannot_self_authorize_new_hashes(candidate):
    edit_json(candidate, 'baseline-v01-cpu-f0.json', lambda d: d.update(original_baseline_sha256={}))
    with pytest.raises(Invalid, match='original baseline evidence changed'):
        verify(candidate)


@pytest.mark.parametrize('path', ['LICENSE', 'docs/FOUNDING.md', 'docs/provenance/SOURCE.md'])
def test_frozen_provenance_cannot_be_waived_by_disposition(candidate, path):
    file = candidate / path
    file.write_text(file.read_text() + '\nchanged\n')
    edit_rows(candidate, lambda rows: [r.update(disposition='modified') for r in rows
              if r['scope'] == 'target-baseline' and r['source']['path'] == path])
    with pytest.raises(Invalid, match='frozen ADR/provenance/LICENSE'):
        verify(candidate)
