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


def test_real_mcp_edges_remain_pending_not_whitelisted():
    paths = sorted((REPO / 'surfaces/mcp').rglob('*.py'))
    errors = [e for p in paths for e in check_edges(p.read_text(), EXPORTS,
              path=p.relative_to(REPO).as_posix(), packages=package_contexts(REPO, p.relative_to(REPO))) ]
    assert errors, 'B03 must replace this pending-edge observation after redirection'
    assert any('private engine edge dgemma.model' in e for e in errors)


@pytest.mark.parametrize('text', [
    'import importlib; getattr(importlib, "import_module")(name)',
    'exec(code)',
    'eval(code)',
    'import runpy; runpy.run_module(name)',
])
def test_computed_dynamic_execution_requires_review(text):
    assert any('requires explicit disposition' in e for e in check_edges(text, EXPORTS))
