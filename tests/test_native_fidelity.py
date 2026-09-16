"""Observed native behavior, including surprising callback/aliasing semantics.

Uses the retained loader/frame toy seams; no dependency modules are stubbed,
no model weights downloaded, and no native behavior repaired.
"""
import contextlib
from types import SimpleNamespace as NS

import pytest
import torch

import dgemma as api
import dgemma.model as native_model
from dgemma.capture import _FrameCollector
from dgemma.ingress import validate_capture


@pytest.fixture
def toy_loader(monkeypatch):
    # Same from_pretrained, quant preflight, and CUDA-query seams as the
    # retained test_autoround_load / test_quant_mismatch_guard toy loaders.
    model = torch.nn.Linear(2, 2)
    processor = object()
    calls = []
    monkeypatch.setattr(native_model, '_check_quant_checkpoint_match', lambda *a: calls.append(('preflight', a)))
    monkeypatch.setattr(native_model, '_assert_autoround_vram_precondition', lambda: None)
    monkeypatch.setattr(native_model, '_apply_autoround_patches', contextlib.nullcontext)
    def load(repo, **kwargs):
        calls.append(('model', repo, kwargs))
        return model
    def process(repo, **kwargs):
        calls.append(('processor', repo, kwargs))
        return processor
    monkeypatch.setattr(native_model.DiffusionGemmaForBlockDiffusion, 'from_pretrained', load)
    monkeypatch.setattr(native_model.AutoProcessor, 'from_pretrained', process)
    monkeypatch.setattr(torch.cuda, 'is_available', lambda: True)
    return model, processor, calls


@pytest.mark.parametrize('quant', ['none', 'autoround'])
@pytest.mark.parametrize('phase', range(4), ids=['preflight', 'model', 'processor', 'device'])
@pytest.mark.parametrize('failure', [True, OSError, ImportError, LookupError], ids=['interrupt', 'oserror', 'importerror', 'other'])
def test_load_callback_phase_identity_and_translation(toy_loader, quant, phase, failure):
    _, _, calls = toy_loader
    polls = []
    error = None if failure is True else failure('callback sentinel')
    def callback():
        polls.append(len(polls))
        if polls[-1] == phase:
            if error is not None:
                raise error
            return True
        return False
    translated = phase == 2 and (failure is OSError or (failure is ImportError and quant == 'autoround'))
    expected = api.LoadInterrupted if failure is True else RuntimeError if translated else failure
    with pytest.raises(expected) as caught:
        api.load_model(repo_id='toy', quant=quant, local_files_only=True, check_interrupted=callback)
    assert type(caught.value) is expected
    assert len(polls) == phase + 1
    assert [c[0] for c in calls] == ['preflight', 'model', 'processor'][:phase]
    if failure is True:
        assert isinstance(caught.value, Exception)
        assert api.LoadInterrupted is native_model.LoadInterrupted
        assert caught.value.__cause__ is None
        assert 'interrupted before phase' in str(caught.value)
    elif translated:
        assert caught.value.__cause__ is error
        assert ('Could not load' if failure is OSError else 'requires the auto-round library') in str(caught.value)
    else:
        assert caught.value is error
        assert caught.value.__cause__ is None


@pytest.mark.parametrize('quant', ['none', 'autoround'])
def test_load_forwarding_native_payload(toy_loader, quant):
    model, processor, calls = toy_loader
    polls = []
    result = api.load_model(quant=quant, local_files_only=True, check_interrupted=lambda: polls.append(1) or False)
    repo = api.AUTOROUND_REPO_ID if quant == 'autoround' else api.DEFAULT_REPO_ID
    assert type(result) is api.DGemmaModel
    assert result.model is model and result.processor is processor
    assert result.repo_id == repo and result.quant == quant and result.device == 'cpu'
    assert calls == [('preflight', (repo, quant, True)),
                     ('model', repo, {'device_map': 'auto', 'dtype': 'auto' if quant == 'autoround' else torch.bfloat16, 'local_files_only': True}),
                     ('processor', repo, {'local_files_only': True})]
    assert len(polls) == 4


@pytest.mark.parametrize('keep', ['all', 'last'])
@pytest.mark.parametrize('budget', [1, None])
def test_capture_same_frame_and_budget_gates_full_softmax(monkeypatch, keep, budget):
    seen, computations = [], []
    softmax = torch.softmax
    def spy(values, *args, **kwargs):
        computations.append(values)
        return softmax(values, *args, **kwargs)
    monkeypatch.setattr(torch, 'softmax', spy)
    collector = _FrameCollector(NS(num_inference_steps=4), .1, .9, keep_frames=keep,
                                capture_full_distribution=True, max_full_distribution_steps=budget)
    def on_frame(frame):
        assert collector.frames[-1] is frame  # assertion at callback time
        seen.append(frame)
        assert frame.distribution is collector.frames[-1].distribution
    collector.on_frame = on_frame
    logits = torch.tensor([[[0., 1., 2.], [2., 0., 1.]]])
    for step in range(3):
        before = len(computations)
        assert collector.on_step_end(None, step, step, {
            'canvas': torch.tensor([[1, 2]]), 'logits': logits,
            'scheduler_output': NS(accepted_index=torch.tensor([[True, False]]))}) == {}
        expected = budget is None or step < budget
        assert len(computations) - before == int(expected)
        assert (seen[-1].distribution is not None) is expected
        assert collector.frames[-1] is seen[-1]
        assert seen[-1].entropy is not None
    assert len(seen) == 3
    assert len(collector.frames) == (3 if keep == 'all' else 1)
    if keep == 'all':
        assert all(a is b for a, b in zip(seen, collector.frames))


@pytest.mark.parametrize('duck', [False, True])
def test_public_ingress_rejects_uncapped_full_distribution(duck):
    payload = NS(capture_full_distribution=True) if duck else api.CaptureSpec(capture_full_distribution=True)
    with pytest.raises(ValueError, match='max_full_distribution_steps'):
        validate_capture(payload)
    # Root introduces no wrapper; native ingress runs before pipeline setup.
    with pytest.raises(ValueError, match='max_full_distribution_steps'):
        api.run_diffusion(NS(processor=NS(vocab_size=3)), 'prompt', capture=payload)


def test_callback_error_preserves_retained_frame():
    error = LookupError('observer')
    collector = _FrameCollector(NS(num_inference_steps=4), .1, .9)
    def fail(frame):
        assert frame is collector.frames[-1]
        raise error
    collector.on_frame = fail
    with pytest.raises(LookupError) as caught:
        collector.on_step_end(None, 0, 0, {'canvas': [1], 'scheduler_output': NS(accepted_index=torch.tensor([[True]]))})
    assert caught.value is error and collector.steps_used == 1


def test_decode_raw_order_example_zero_and_empty():
    calls = []
    def decode(ids, **kwargs):
        calls.append((ids, kwargs))
        return '<think>raw<eos>' + str(ids)
    processor = NS(tokenizer=NS(decode=decode))
    frames = [NS(canvas=torch.tensor([[3, 4], [99, 99]])), NS(canvas=(5, 6))]
    assert api.decode_frames(processor, []) == [] and not calls
    assert api.decode_frames(processor, frames) == ['<think>raw<eos>[3, 4]', '<think>raw<eos>[5, 6]']
    assert calls == [([3, 4], {'skip_special_tokens': True}), ([5, 6], {'skip_special_tokens': True})]


class ToyCache:
    def __init__(self):
        self.length = 0
    def get_seq_length(self, layer_idx):
        return self.length


class ToyEncoder(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.zeros(1))
        self.calls = []
        self.error = None
    def forward(self, **kwargs):
        self.calls.append((kwargs, torch.is_grad_enabled()))
        if self.error:
            raise self.error
        cache = kwargs['past_key_values']
        if cache is None:
            cache = ToyCache()
        cache.length += kwargs['input_ids'].shape[-1]
        return NS(past_key_values=cache)


@pytest.fixture
def encoder_model():
    encoder = ToyEncoder()
    config = NS(num_hidden_layers=2, layer_types=['full_attention'] * 2, sliding_window=4, rope_parameters={})
    model = NS(model=NS(model=NS(encoder=encoder), config=NS(get_text_config=lambda: config)),
               processor=NS(vocab_size=17), repo_id='toy', device='not-the-encoder-device')
    return model, encoder


def test_encode_new_wrapper_shared_cache_raw_forwarding(encoder_model):
    model, encoder = encoder_model
    with pytest.raises(ValueError, match='empty'):
        api.encode_sequence(model, [])
    assert not encoder.calls
    first = api.encode_sequence(model, (3, 7))
    second = api.encode_sequence(model, [8], into=first)
    assert type(first) is type(second) is api.KVCache
    assert second is not first and second.cache is first.cache
    assert second.geometry == first.geometry and second.geometry is not first.geometry
    assert second.provenance is not first.provenance
    assert first.cumulative_length == (2, 2) and second.cumulative_length == (3, 3)
    assert first.cache.length == 3  # known aliasing; no clone repair
    assert first.provenance.minting_sequence == (3, 7)
    assert second.provenance.minting_sequence == (3, 7, 8)
    assert second.provenance.tokenizer_fingerprint == api.tokenizer_fingerprint(model) == 'toy:17'
    for i, (kwargs, grad) in enumerate(encoder.calls):
        assert not grad and set(kwargs) == {'input_ids', 'past_key_values', 'position_ids'}
        assert kwargs['input_ids'].device == encoder.weight.device
        assert kwargs['input_ids'].tolist() == ([[3, 7]] if i == 0 else [[8]])
        assert kwargs['position_ids'].tolist() == ([[0, 1]] if i == 0 else [[2]])
        assert kwargs['past_key_values'] is (None if i == 0 else first.cache)
    # Native encode does not revalidate into: preserve duck typing and stale geometry.
    duck = NS(cache=first.cache, cumulative_length=(42,), provenance=first.provenance, geometry={})
    third = api.encode_sequence(model, [9], into=duck)
    assert third.cache is first.cache and encoder.calls[-1][0]['position_ids'].tolist() == [[42]]


def test_encode_oom_native_type_and_chaining(encoder_model, monkeypatch):
    model, encoder = encoder_model
    encoder.error = torch.OutOfMemoryError('toy capacity')
    monkeypatch.setattr(torch.cuda, 'is_available', lambda: False)
    with pytest.raises(torch.OutOfMemoryError, match='bare transformers lane') as caught:
        api.encode_sequence(model, [1])
    assert type(caught.value) is torch.OutOfMemoryError
    assert caught.value.__cause__ is encoder.error
