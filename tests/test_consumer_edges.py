"""AST-only consumer boundary fixtures, including both loader contexts."""
from pathlib import Path

import pytest

from tools.consumer_edges import check_edges, package_contexts, resolve
from tools.refactor_support import load

REPO = Path(__file__).resolve().parents[1]
EXPORTS = load(REPO / 'docs/refactor/contracts.json')['exports']


@pytest.mark.parametrize('text', [
    'from dgemma import load_model as load; load()',
    'import dgemma as dg; dg.load_model()',
    'import dgemma; dgemma.KVCache',
    'from .state_manager import StateManager',
    'from .. import state_manager',
    'import surfaces.mcp.state_manager as state',
    'import dgemma as dg\nother = dg\nother.decode_frames(p, [])',
    'try:\n from ...dgemma import load_model\nexcept ImportError:\n from dgemma import load_model',
])
def test_allowed_explicit_root_and_adapter_siblings(text):
    assert check_edges(text, EXPORTS, packages=('surfaces.mcp', 'bundle.surfaces.mcp')) == []


@pytest.mark.parametrize('text', [
    'from dgemma.model import load_model',
    'import dgemma.model as engine; engine.load_model()',
    'from dgemma import model',
    'from dgemma import *',
    'import dgemma as dg; dg.model.load_model()',
    'import dgemma; dgemma._private',
    'import dgemma as dg; other = dg; other.model.load_model()',
    'from dgemma import load_model as load; load.__globals__',
    'from ...dgemma.model import load_model',
    'from ... import dgemma as dg; dg.model.load_model()',
    'try:\n from ...dgemma.model import load_model\nexcept ImportError:\n from dgemma import load_model',
    'try:\n from ...dgemma import load_model\nexcept ImportError:\n from dgemma.model import load_model',
    'import dgemma as dg; getattr(dg, name)',
])
def test_reject_private_wildcard_relative_and_both_branches(text):
    errors = check_edges(text, EXPORTS, packages=('surfaces.mcp', 'bundle.surfaces.mcp'))
    assert errors
    assert any('[surfaces.mcp]' in e for e in errors)
    assert any('[bundle.surfaces.mcp]' in e for e in errors)


@pytest.mark.parametrize('text', [
    'import importlib; importlib.import_module("dgemma")',
    'from importlib import import_module as imp; imp(name)',
    'import importlib as il; f = il.import_module; f(name)',
    '__import__(name)',
    'from builtins import __import__ as imp; imp("json")',
])
def test_dynamic_import_never_silently_succeeds(text):
    assert any('requires explicit disposition' in e for e in check_edges(text, EXPORTS))


def test_reviewed_dynamic_disposition_does_not_waive_private_edge():
    for name, private in [('json', False), ('dgemma.model', True)]:
        text = f'import importlib; importlib.import_module({name!r})'
        disposition = dict(package='', expression=f'importlib.import_module({name!r})', reason='Fixture-only explicit review')
        errors = check_edges(text, EXPORTS, dispositions=[disposition])
        assert bool(errors) is private
    assert check_edges(text, EXPORTS, dispositions=[{**disposition, 'reason': ''}])


def test_level_minus_one_resolution_from_actual_package(tmp_path):
    (tmp_path / '__init__.py').write_text('')
    path = 'surfaces/mcp/commands/model.py'
    assert package_contexts(tmp_path, path) == ['surfaces.mcp.commands', f'{tmp_path.name}.surfaces.mcp.commands']
    assert resolve('state', 1, 'surfaces.mcp.commands') == 'surfaces.mcp.commands.state'
    assert resolve('state', 2, 'surfaces.mcp.commands') == 'surfaces.mcp.state'
    assert resolve('dgemma', 3, 'bundle.surfaces.mcp') == 'bundle.dgemma'
    assert resolve('dgemma', 3, 'surfaces.mcp') is None
    assert resolve(None, 2, 'bundle.surfaces.mcp') == 'bundle.surfaces'


def test_transitive_engine_imports_are_not_consumer_edges():
    # The scanner parses this direct caller; it never imports dgemma or walks
    # sys.modules to misclassify engine-to-engine edges triggered by root.
    assert not check_edges('import dgemma\ndgemma.run_diffusion(m, p)', EXPORTS)


def test_real_mcp_edges_pass_without_whitelisting():
    paths = sorted((REPO / 'surfaces/mcp').rglob('*.py'))
    errors = [e for p in paths for e in check_edges(p.read_text(), EXPORTS,
              path=p.relative_to(REPO).as_posix(), packages=package_contexts(REPO, p.relative_to(REPO))) ]
    assert len(paths) == 8
    assert errors == []


@pytest.mark.parametrize('text', [
    'import importlib; getattr(importlib, "import_module")(name)',
    'exec(code)',
    'eval(code)',
    'import runpy; runpy.run_module(name)',
])
def test_computed_dynamic_execution_requires_review(text):
    assert any('requires explicit disposition' in e for e in check_edges(text, EXPORTS))


@pytest.mark.parametrize('text', [
    'import dgemma as dg\ndg.{member}()\nimport json as dg',
    'from bundle import dgemma as dg\ndg.{member}()\nfrom bundle import json as dg',
    'def engine():\n import dgemma as dg\n dg.{member}()\n'
    'def sibling():\n import json as dg\n return dg',
    'if condition:\n import dgemma as dg\nelse:\n import json as dg\ndg.{member}()',
    'if condition:\n import json as dg\nelse:\n import dgemma as dg\ndg.{member}()',
    'import dgemma as dg\nother = dg\nimport json as dg\nother.{member}()',
    'import dgemma as dg\nimport json as other\nother = dg\nother.{member}()',
])
@pytest.mark.parametrize('member,private', [('model.load_model', True), ('load_model', False)])
def test_possible_bindings_survive_rebinding_scopes_and_branches(text, member, private):
    errors = check_edges(text.format(member=member), EXPORTS,
                         packages=('surfaces.mcp', 'bundle.surfaces.mcp'))
    assert bool(errors) is private
    if private:
        assert all('private engine edge' in e for e in errors)
        assert any('[surfaces.mcp]' in e for e in errors)
        assert any('[bundle.surfaces.mcp]' in e for e in errors)


# Independently enumerate the supported spellings, not the checker's allowlist.
DYNAMIC_CASES = [
    ('', '__import__'),
    ('', 'eval'),
    ('', 'exec'),
    ('import builtins as module', 'module.__import__'),
    ('import builtins as module', 'module.eval'),
    ('import builtins as module', 'module.exec'),
    ('import importlib as module', 'module.import_module'),
    ('import runpy as module', 'module.run_module'),
    ('import runpy as module', 'module.run_path'),
    ('from runpy import run_module as primitive', 'primitive'),
    ('from runpy import run_path as primitive', 'primitive'),
    ('from builtins import eval as primitive', 'primitive'),
    ('from builtins import exec as primitive', 'primitive'),
    ('from builtins import __import__ as primitive', 'primitive'),
    ('from importlib import import_module as primitive', 'primitive'),
]


@pytest.mark.parametrize('setup,primitive', DYNAMIC_CASES)
@pytest.mark.parametrize('argument', ['name', "'json'", "'dgemma.model'"])
def test_all_dynamic_assignment_aliases_require_review(setup, primitive, argument):
    text = f'{setup}\nfirst = {primitive}\nsecond: object = first\nrunner = twin = second\nrunner({argument})'
    errors = check_edges(text, EXPORTS)
    assert any('dynamic import requires explicit disposition: runner(' in e for e in errors)
    if argument == "'dgemma.model'":
        assert any('private engine edge dgemma.model' in e for e in errors)


@pytest.mark.parametrize('setup,primitive', DYNAMIC_CASES)
@pytest.mark.parametrize('private', [False, True])
def test_dynamic_alias_disposition_cannot_waive_internal_literal(setup, primitive, private):
    expression = f"runner({'dgemma.model' if private else 'json'!r})"
    text = f'{setup}\nrunner = {primitive}\n{expression}'
    disposition = dict(package='surfaces.mcp', expression=expression,
                       reason='Fixture-only review of this expression and package')
    errors = check_edges(text, EXPORTS, packages=('surfaces.mcp',), dispositions=[disposition])
    assert bool(errors) is private
    if private:
        assert all('private engine edge dgemma.model' in e for e in errors)


@pytest.mark.parametrize('override', [
    {'package': 'other'}, {'expression': "runner('other')"},
    {'expression': '*'}, {'reason': ''}, {'reason': '  '}, {'reason': None},
])
def test_disposition_must_match_expression_package_and_have_rationale(override):
    text = "import runpy\nrunner = runpy.run_module\nrunner('json')"
    disposition = dict(package='surfaces.mcp', expression="runner('json')", reason='Reviewed fixture')
    assert check_edges(text, EXPORTS, packages=('surfaces.mcp',),
                       dispositions=[{**disposition, **override}])


@pytest.mark.parametrize('text', [
    "import runpy as module\nother = module\nmodule = other\nrunner = other.run_path\nrunner(name)",
    "import builtins as module\nother = module\nrunner = other.eval\nrunner(name)",
    "import importlib as module\nother = module\nrunner = other.import_module\nrunner(name)",
    "import runpy as module\nrunner = module.run_module\nimport json as module\nrunner(name)",
    "def engine():\n import runpy as module\n runner = module.run_module\n runner(name)\n"
    "def sibling():\n import json as module\n runner = module.dumps",
    "if condition:\n import runpy as module\nelse:\n import json as module\n"
    "runner = module.run_module\nrunner(name)",
])
def test_dynamic_module_bindings_and_collisions(text):
    assert any('requires explicit disposition' in e for e in check_edges(text, EXPORTS))


@pytest.mark.parametrize('text,private', [
    ('import dgemma as dg\na = dg\nb = a\na = b\na.load_model()', False),
    ('import dgemma as dg\na = dg.load_model\na = a.public\na = a.other\na()', False),
    ('import dgemma as dg\na = dg\nb = a.load_model\na = b.public\na._private', True),
    ('import dgemma as dg\ndg = dg._private\ndg = dg.public\ndg.model.load_model()', True),
])
def test_alias_cycles_are_bounded(text, private):
    # A subprocess timeout makes a nonterminating fixed point an ordinary test
    # failure. Branching attribute cycles also guard against path-string growth.
    import json
    import subprocess
    import sys

    script = ('import json\nfrom tools.consumer_edges import check_edges\n'
              f'print(json.dumps(check_edges({text!r}, {EXPORTS!r})))')
    result = subprocess.run([sys.executable, '-B', '-c', script], cwd=REPO,
                            capture_output=True, text=True, timeout=10, check=True)
    errors = json.loads(result.stdout)
    assert bool(errors) is private
    if private:
        assert all('private engine edge' in e for e in errors)
