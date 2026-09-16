"""B01 checkout boundary: canonical objects, not wrappers or a new loader.

Native modules are imported here to establish identity, not as consumer API.
The independent subprocess blocks framework/adapter imports before root import.
"""
from __future__ import annotations

import ast
from dataclasses import MISSING, fields, is_dataclass
import importlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
from typing import get_type_hints

import pytest

import dgemma


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "docs" / "refactor"
CONTRACT = json.loads((CONTRACT_DIR / "contracts.json").read_text())
RECORDS = [
    record
    for shard in CONTRACT["public_shards"]
    for record in json.loads((CONTRACT_DIR / shard).read_text())["records"]
]
CALLABLES = [r for r in RECORDS if r["kind"] == "callable"]
DATACLASSES = [
    r for r in RECORDS
    if r["kind"] == "type" and any(d.startswith("dataclass") for d in r["decorators"])
]
CONSTANTS = [r for r in RECORDS if r["kind"] == "constant"]
EXISTING_EXPORTS = {
    "CanvasState", "CanvasTrace", "DGemmaModel", "DiffusionFrame",
    "DEFAULT_CONFIDENCE", "DEFAULT_ENTROPY_BOUND", "DEFAULT_GEN_LENGTH",
    "DEFAULT_NUM_INFERENCE_STEPS", "DEFAULT_QUANT", "DEFAULT_T_MAX",
    "DEFAULT_T_MIN", "DEFAULT_REPO_ID", "AUTOROUND_REPO_ID", "THINK_TOKEN",
    "load_model", "run_diffusion",
}


def native(record):
    module, name = record["native"].rsplit(".", 1)
    return getattr(importlib.import_module(module), name)


def default_value(expression, obj):
    # Contract defaults are literals or module-level native constants.
    tree = ast.parse(expression, mode="eval").body
    if isinstance(tree, ast.Name):
        return getattr(importlib.import_module(obj.__module__), tree.id)
    return ast.literal_eval(tree)


def test_exact_root_allowlist_and_preserved_exports():
    assert len(CONTRACT["exports"]) == len(set(CONTRACT["exports"])) == 30
    assert dgemma.__all__ == CONTRACT["exports"]
    assert EXISTING_EXPORTS <= set(dgemma.__all__)
    assert {r["export"] for r in RECORDS} == set(dgemma.__all__)
    assert not set(CONTRACT["non_exports"]) & set(dgemma.__all__)
    namespace = {}
    exec("from dgemma import *", namespace)
    assert set(namespace) - {"__builtins__"} == set(dgemma.__all__)
    assert all(namespace[name] is getattr(dgemma, name) for name in dgemma.__all__)


@pytest.mark.parametrize("record", RECORDS, ids=lambda r: r["export"])
def test_native_object_identity(record):
    root = getattr(dgemma, record["export"])
    original = native(record)
    assert root is original
    if record["kind"] != "constant":
        assert root.__module__ == record["native"].rsplit(".", 1)[0]
        assert root.__module__ == original.__module__


@pytest.mark.parametrize("record", CALLABLES, ids=lambda r: r["export"])
def test_signatures_defaults_and_resolved_annotations(record):
    root = getattr(dgemma, record["export"])
    original = native(record)
    signature = inspect.signature(root)
    native_signature = inspect.signature(original)
    assert signature == native_signature
    assert root.__defaults__ is original.__defaults__
    assert root.__kwdefaults__ is original.__kwdefaults__
    assert root.__annotations__ is original.__annotations__
    assert get_type_hints(root) == get_type_hints(original)
    assert list(signature.parameters) == [p["name"] for p in record["parameters"]]
    for expected in record["parameters"]:
        parameter = signature.parameters[expected["name"]]
        assert parameter.kind.name == expected["kind"]
        assert parameter.annotation == expected["annotation"]
        assert parameter.default is native_signature.parameters[parameter.name].default
        if expected["required"]:
            assert parameter.default is inspect.Parameter.empty
        else:
            assert parameter.default == default_value(expected["default"], original)
    assert signature.return_annotation == record["returns"]


@pytest.mark.parametrize("record", DATACLASSES, ids=lambda r: r["export"])
def test_dataclass_fields_defaults_and_frozen_flags(record):
    root = getattr(dgemma, record["export"])
    original = native(record)
    assert is_dataclass(root)
    assert root.__dataclass_params__ is original.__dataclass_params__
    assert root.__dataclass_params__.frozen == ("dataclass(frozen=True)" in record["decorators"])
    assert inspect.signature(root) == inspect.signature(original)
    assert get_type_hints(root) == get_type_hints(original)
    actual = fields(root)
    assert [f.name for f in actual] == [f["name"] for f in record["fields"]]
    for field, original_field, expected in zip(actual, fields(original), record["fields"]):
        assert field is original_field
        assert field.type == expected["annotation"]
        assert field.default is original_field.default
        assert field.default_factory is original_field.default_factory
        if expected["required"]:
            assert field.default is MISSING and field.default_factory is MISSING
        else:
            assert field.default == default_value(expected["default"], original)


@pytest.mark.parametrize("record", CONSTANTS, ids=lambda r: r["export"])
def test_constant_values_and_identity(record):
    assert getattr(dgemma, record["export"]) is native(record)
    assert getattr(dgemma, record["export"]) == ast.literal_eval(record["expression"])


def test_knob_docs_is_the_mutable_native_dictionary(monkeypatch):
    from dgemma.config import KNOB_DOCS

    assert isinstance(dgemma.KNOB_DOCS, dict)
    marker = object()
    monkeypatch.setitem(dgemma.KNOB_DOCS, "__root_boundary_probe__", marker)
    assert KNOB_DOCS["__root_boundary_probe__"] is marker


def test_load_interrupted_is_canonical_exception_with_inherited_constructor():
    from dgemma.model import LoadInterrupted

    assert dgemma.LoadInterrupted is LoadInterrupted
    assert LoadInterrupted.__bases__ == (Exception,)
    assert LoadInterrupted.__init__ is Exception.__init__
    assert not issubclass(LoadInterrupted, RuntimeError)
    marker = object()
    error = dgemma.LoadInterrupted("interrupted", marker)
    assert error.args == ("interrupted", marker)
    with pytest.raises(LoadInterrupted) as caught:
        raise error
    assert caught.value is error


def test_root_import_and_cpu_calls_with_frameworks_unavailable():
    script = textwrap.dedent('''
        import importlib
        import importlib.abc
        import sys

        blocked = {"mcp", "comfy", "comfyui", "comfy_api", "folder_paths",
                   "nodes", "server", "surfaces", "consumers"}
        attempted = []
        class Unavailable(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split(".")[0] in blocked:
                    attempted.append(fullname)
                    raise ModuleNotFoundError("blocked framework: " + fullname, name=fullname)
        assert not any(name.split(".")[0] in blocked for name in sys.modules)
        sys.meta_path.insert(0, Unavailable())
        # Prove unavailability, not merely absence from sys.modules.
        for name in sorted(blocked):
            try:
                importlib.import_module(name)
            except ModuleNotFoundError as error:
                assert error.name == name and "blocked framework:" in str(error)
            else:
                raise AssertionError("framework import unexpectedly succeeded: " + name)
        assert set(attempted) == blocked
        attempted.clear()

        import dgemma
        import torch
        assert not torch.cuda.is_initialized()
        assert not torch.cuda.is_available()
        # Native decode seam, as in test_frames: a CPU canvas and duck tokenizer.
        class Tokenizer:
            vocab_size = 128
            def decode(self, ids, skip_special_tokens):
                assert skip_special_tokens is True
                assert ids == [7, 8]
                return "raw thought and EOS left intact"
        tokenizer = Tokenizer()
        frame = dgemma.DiffusionFrame(0, 0, 1.0, 0.8, [0.5], torch.tensor([[7, 8], [9, 10]]))
        assert dgemma.decode_frames(tokenizer, [frame]) == ["raw thought and EOS left intact"]
        assert dgemma.decode_frames(tokenizer, []) == []
        model = dgemma.DGemmaModel(object(), tokenizer, "cpu", "bfloat16", "toy/repo", "none")
        assert dgemma.tokenizer_fingerprint(model) == "toy/repo:128"
        assert not attempted, attempted
        assert not any(name.split(".")[0] in blocked for name in sys.modules)
        assert not torch.cuda.is_initialized()
        print("root-isolation: PASS (active import blocker; native CPU calls)")
    ''')
    environment = os.environ.copy()
    environment.update(
        CUDA_VISIBLE_DEVICES="", NVIDIA_VISIBLE_DEVICES="none",
        PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1",
    )
    result = subprocess.run(
        [sys.executable, "-B", "-c", script], cwd=ROOT, env=environment,
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "root-isolation: PASS" in result.stdout
