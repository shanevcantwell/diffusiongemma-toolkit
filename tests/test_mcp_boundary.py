"""B03 checkout-only adapter regressions; no weights, SDK stubs or source rehoming."""
import ast
import asyncio
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

import dgemma
from surfaces.mcp import state_manager as state
from surfaces.mcp.commands import generate as command
from tools.refactor_support import git, load

REPO = Path(__file__).resolve().parents[1]
PATHS = ('surfaces/mcp/state_manager.py', 'surfaces/mcp/commands/generate.py')


@pytest.mark.parametrize('prefix', ['', 'boundary_bundle.'])
def test_real_import_branches_resolve_canonical_root_identities(prefix):
    # A namespace parent reproduces the retained loader package arithmetic, not
    # an installed/Comfy proof. Each context gets a fresh interpreter and real SDK.
    script = r'''
import ast, builtins, importlib, pathlib, sys, types
repo, prefix = pathlib.Path(sys.argv[1]), sys.argv[2]
if prefix:
    package = types.ModuleType(prefix[:-1])
    package.__path__ = [str(repo)]
    sys.modules[prefix[:-1]] = package
observed = []
original = builtins.__import__
def record(name, globals=None, locals=None, fromlist=(), level=0):
    caller = (globals or {}).get('__name__', '')
    if caller in {prefix + 'surfaces.mcp.state_manager', prefix + 'surfaces.mcp.commands.generate'} and 'dgemma' in name:
        observed.append((caller, name, tuple(fromlist), level))
    return original(name, globals, locals, fromlist, level)
builtins.__import__ = record
try:
    root = importlib.import_module(prefix + 'dgemma')
    modules = [importlib.import_module(prefix + name) for name in
               ('surfaces.mcp.state_manager', 'surfaces.mcp.commands.generate')]
finally:
    builtins.__import__ = original
assert len(observed) == 6, observed
for caller, name, names, level in observed:
    assert name == 'dgemma', observed
    assert level == (3 if caller.endswith('state_manager') else 4) if prefix else level == 0
    module = sys.modules[caller]
    for symbol in names:
        assert symbol in root.__all__, symbol
        assert getattr(module, symbol) is getattr(root, symbol), (caller, symbol)
for module in modules:
    # Both textual branches, not just the branch executed in this subprocess.
    edges = [n for n in ast.walk(ast.parse(pathlib.Path(module.__file__).read_text()))
             if isinstance(n, ast.ImportFrom) and 'dgemma' in (n.module or '')]
    assert len(edges) == 6
    assert {n.module for n in edges} == {'dgemma'}
print('canonical root identities; relative/fallback levels; no direct hidden imports: PASS')
'''
    result = subprocess.run([sys.executable, '-B', '-c', script, str(REPO), prefix],
                            cwd=REPO, capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'PASS' in result.stdout


@pytest.mark.parametrize('path', PATHS)
def test_production_diff_is_exactly_import_module_redirection(path):
    manifest = load(REPO / 'docs/refactor/manifest.json')
    source = Path(os.environ.get('DGEMMA_SOURCE_REPO', REPO))
    original = git(source, 'show', manifest['baselines']['source']['revision'] + ':' + path)
    expected = original
    for module in ('kv_cache', 'model', 'types', 'config', 'loop', 'payloads'):
        expected = expected.replace('dgemma.' + module + ' import ', 'dgemma import ')
    assert (REPO / path).read_text() == expected


def model():
    return SimpleNamespace(repo_id='test/model', device='cpu',
                           processor=SimpleNamespace(tokenizer=SimpleNamespace(vocab_size=8)))


def cache(m):
    return SimpleNamespace(provenance=SimpleNamespace(
        model_repo_id=m.repo_id, tokenizer_fingerprint=dgemma.tokenizer_fingerprint(m)))


@pytest.mark.parametrize('fails', [False, True])
def test_load_attempt_clears_lru_and_preserves_residency_on_failure(monkeypatch, fails):
    old, new = model(), model()
    manager = state.StateManager(_model=old, _repo_id='old', _quant='none')
    handle = manager._store_kv_cache(cache(old))
    error = RuntimeError('load failed')
    def load_model(**kwargs):
        assert kwargs == dict(repo_id='new', quant='autoround', local_files_only=True)
        assert not manager._kv_cache_registry
        if fails:
            raise error
        return new
    monkeypatch.setattr(state, 'load_model', load_model)
    if fails:
        with pytest.raises(RuntimeError) as caught:
            manager.load(repo_id='new', quant='autoround', local_files_only=True)
        assert caught.value is error
        assert manager.require_model() is old
        assert manager.status() == dict(is_loaded=True, repo_id='old', quant='none', device='cpu')
    else:
        assert manager.load(repo_id='new', quant='autoround', local_files_only=True) is new
        assert manager.status() == dict(is_loaded=True, repo_id='new', quant='autoround', device='cpu')
    with pytest.raises(ValueError, match='Unknown or expired'):
        manager.resolve_kv_cache(handle)


def test_registry_default_bound_lru_touch_and_model_identity():
    m = model()
    manager = state.StateManager(_model=m)
    assert manager._kv_cache_registry_capacity == 8
    caches = [cache(m) for _ in range(9)]
    handles = [manager._store_kv_cache(c) for c in caches[:8]]
    assert manager.resolve_kv_cache(handles[0]) is caches[0]
    ninth = manager._store_kv_cache(caches[8])
    assert list(manager._kv_cache_registry) == handles[2:] + [handles[0], ninth]
    with pytest.raises(ValueError, match='Unknown or expired'):
        manager.resolve_kv_cache(handles[1])
    m.repo_id = 'different'
    with pytest.raises(ValueError, match='different model'):
        manager.resolve_kv_cache(ninth)


def test_encode_raw_tokens_new_wrapper_same_handle(monkeypatch):
    m = model()
    tokens, prompts, calls = [1, 2], [], []
    m.processor.tokenizer.encode = lambda prompt: prompts.append(prompt) or tokens
    manager = state.StateManager(_model=m)
    first, second = cache(m), cache(m)
    def encode(actual_model, token_ids, *, into):
        assert actual_model is m and token_ids is tokens
        calls.append(into)
        return first if into is None else second
    monkeypatch.setattr(state, 'encode_sequence', encode)
    handle = manager.encode_into_registry('raw')
    assert manager.encode_into_registry('', handle) == handle
    assert manager.resolve_kv_cache(handle) is second
    assert prompts == ['raw', ''] and calls == [None, first]
    with pytest.raises(ValueError, match='Unknown or expired'):
        manager.encode_into_registry('raw', '')  # unlike generate, '' is not absent


def result_tuple():
    return ('answer', SimpleNamespace(converged=True, committed_fraction=0.5, steps_used=1,
        thought=None, stray_thought_delimiter=False, turn_closed=True, answer_tokens=2,
        finished_honestly=True), SimpleNamespace(scheduler_name='native', scheduler_config={'a': 1},
        frames=[SimpleNamespace(canvas_idx=0, step_idx=1, t=0.5, temperature=1.0,
                                committed_fraction_per_example=(0.5,))]))


@pytest.mark.parametrize('with_run', [False, True])
def test_generate_forwarding_payloads_serialization_and_cancel_cleanup(monkeypatch, with_run):
    m = model()
    manager = state.StateManager(_model=m)
    kv = cache(m)
    handle = manager._store_kv_cache(kv)
    calls = []
    def run(actual_model, prompt, **kwargs):
        assert actual_model is m and prompt == 'prompt'
        calls.append(kwargs)
        assert kwargs['kv_cache'] is kv
        assert kwargs['constraints'] == dgemma.Constraints(pins=(dgemma.Pin(position=1, token_id=2),))
        assert kwargs['control_signals'] == dgemma.ControlSignals(bindings=(
            dgemma.Binding(target='temperature', signal=(0.1,), low=0.0, high=1.0),))
        assert kwargs['capture'] == dgemma.CaptureSpec(top_k=2, keep_frames='last')
        if with_run:
            assert not kwargs['should_cancel']()
            assert asyncio.run(command.cancel_run(manager, {'run_id': 'b03'}))['found']
            assert kwargs['should_cancel']()
        else:
            assert kwargs['should_cancel'] is None
        return result_tuple()
    monkeypatch.setattr(command, 'run_diffusion', run)
    args = dict(prompt='prompt', kv_cache_id=handle, seed=7, thinking=True, include_frames=True,
        constraints={'pins': [{'position': 1, 'token_id': 2}]},
        control_signals={'bindings': [{'target': 'temperature', 'signal': [0.1], 'low': 0.0, 'high': 1.0}]},
        capture={'top_k': 2, 'keep_frames': 'last', 'full_distribution': True})
    if with_run:
        args['run_id'] = 'b03'
    result = asyncio.run(command.generate(manager, args))
    assert len(calls) == 1 and not command._active_runs
    remaining = {k: v for k, v in calls[0].items() if k not in
                 {'constraints', 'control_signals', 'capture', 'kv_cache', 'should_cancel'}}
    assert remaining == dict(seed=7, thinking=True, gen_length=dgemma.DEFAULT_GEN_LENGTH,
        num_inference_steps=dgemma.DEFAULT_NUM_INFERENCE_STEPS, entropy_bound=dgemma.DEFAULT_ENTROPY_BOUND,
        t_min=dgemma.DEFAULT_T_MIN, t_max=dgemma.DEFAULT_T_MAX, confidence=dgemma.DEFAULT_CONFIDENCE)
    assert result == dict(text='answer', canvas_state=vars(result_tuple()[1]), trace_summary=dict(
        scheduler_name='native', scheduler_config={'a': 1}, num_frames=1, frames=[dict(
            canvas_idx=0, step_idx=1, t=0.5, temperature=1.0, committed_fraction_per_example=[0.5])]))
    assert not asyncio.run(command.cancel_run(manager, {'run_id': 'b03'}))['found']


def test_generate_preserves_empty_prompt_and_empty_cache_handle_differences(monkeypatch):
    assert asyncio.run(command.generate(state.StateManager(), {'prompt': '', 'kv_cache_id': 'unknown'})) == {
        'error': 'prompt is required'}
    manager = state.StateManager(_model=model())
    def run(m, prompt, **kwargs):
        assert kwargs['kv_cache'] is None and kwargs['should_cancel'] is None
        assert all(kwargs[name] is None for name in ('constraints', 'control_signals', 'capture'))
        return result_tuple()
    monkeypatch.setattr(command, 'run_diffusion', run)
    result = asyncio.run(command.generate(manager, {'prompt': 'ok', 'kv_cache_id': ''}))
    assert 'frames' not in result['trace_summary']
    with pytest.raises(ValueError, match='Unknown or expired'):
        asyncio.run(command.generate(manager, {'prompt': 'ok', 'kv_cache_id': 'unknown', 'run_id': 'b03'}))
    assert not command._active_runs


def test_generate_native_error_identity_and_cleanup(monkeypatch):
    error = ValueError('native failure')
    def run(*args, **kwargs):
        assert 'b03' in command._active_runs
        raise error
    monkeypatch.setattr(command, 'run_diffusion', run)
    with pytest.raises(ValueError) as caught:
        asyncio.run(command.generate(state.StateManager(_model=model()), {'prompt': 'ok', 'run_id': 'b03'}))
    assert caught.value is error and not command._active_runs


def test_constructor_error_registration_leak_is_preserved_not_repaired():
    # Known pre-try defect, deliberately not a new cleanup implementation.
    try:
        with pytest.raises(TypeError):
            asyncio.run(command.generate(state.StateManager(_model=model()), dict(
                prompt='ok', run_id='b03', constraints={'pins': [{'unexpected': 1}]})))
        assert 'b03' in command._active_runs
    finally:
        command._unregister_run('b03')
