# V01 original environment evidence — BLOCKED

Observed **2026-09-16 01:08:20Z–01:08:23Z**, target baseline `df5ebace19b5300fc0ada7ea14730dd5d960dcf5`. [Sanitized machine-readable evidence](baseline-v01.json) includes all 16 collection-error IDs, both collected-but-unexecuted IDs and all inventoried dependency versions. [Live ledger](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3) · [original result publication](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3#issuecomment-5690521128).

## Results by axis

- Retained product suite: **BLOCKED at collection**, exit 2; 17 test files, 16 collection errors, 2 items collected, **ZERO executed / passed / assertion failures / skipped**. Collect-only replay also exited 2. JUnit `tests=16` represents collection-error pseudo-tests. No behavioral F0 failure set was established.
- Root exception: `ModuleNotFoundError: No module named 'diffusers'`, via root → loop → compat, originating `dgemma/compat.py:94`.
- Missing dependencies also include auto-round, pynvml, coverage and pytest-cov. Python 3.12.3 / GCC 13.3.0; pytest 9.1.1, torch 2.11.0+cu128, torchvision 0.26.0+cu128, transformers 5.14.1, accelerate 1.14.0, numpy 1.26.4, Pillow 12.2.0, MCP 1.29.0. Source pin is transformers 5.13.0; drift compatibility was **not tested** because diffusers failed first.
- Coverage **NOT MEASURED**, absolute floor enforced **NONE**. No target coverage config or floor exists; do not borrow another repo's 93% or misapply source's scoped KV 100% obligation.
- Separate stdlib provenance regression: **PASS, 3 passed**, exit 0. Only AST/literal scanner regression; no product import, Git history scan or product behavior certified.
- Installed artifact, Comfy, protocol, GPU/real-weight axes: **NOT RUN**. No release claim.
- Checkout file-hash snapshots: 79 before/after, unchanged. Git-lane verification is separate from this test worker's file-hash evidence.

## Normalized reproduction (not an installation instruction)

Run from a disposable checkout at the target baseline. Set `PYTHON` to the interpreter being measured and `EVIDENCE` to a new run-owned directory outside the checkout. The original interpreter was system Python, not a virtualenv. Shell utility `timeout` and pytest are prerequisites. Record the selected interpreter/distribution inventory separately.

```sh
mkdir -p "$EVIDENCE/tmp"
export PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTEST_ADDOPTS='' PYTEST_PLUGINS=''
export CUDA_VISIBLE_DEVICES='' NVIDIA_VISIBLE_DEVICES=none
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1
export HF_HUB_DISABLE_TELEMETRY=1 DO_NOT_TRACK=1
export TMPDIR="$EVIDENCE/tmp" COVERAGE_FILE="$EVIDENCE/.coverage"
unset PYTHONPATH
# Capture exit codes honestly; normal collection failure aborts execution.
timeout --signal=TERM --kill-after=10s 180s "$PYTHON" -B -m pytest tests \
  --import-mode=importlib -m 'not live and not e2e' -p no:cacheprovider \
  --basetemp="$EVIDENCE/tmp/pytest-full" \
  --junitxml="$EVIDENCE/pytest-full.junit.xml" -ra
# Independently record collection shape, not a successful partial suite.
timeout --signal=TERM --kill-after=10s 120s "$PYTHON" -B -m pytest tests \
  --collect-only --import-mode=importlib -m 'not live and not e2e' \
  -p no:cacheprovider --basetemp="$EVIDENCE/tmp/pytest-collect" \
  --junitxml="$EVIDENCE/pytest-collect.junit.xml" -q
# Separate provenance axis:
timeout --signal=TERM --kill-after=5s 30s "$PYTHON" -B \
  docs/provenance/test_audit_inventory.py -v
```

No target/ancestor pytest configuration or target conftest existed. Source import-mode/marker conventions were explicit CLI options; no source config was transplanted and no retained test had live/e2e markers. Plugin autoload, cacheprovider and bytecode writes were disabled. No dependencies were installed, stubbed or skipped to manufacture success. Offline flags are not an OS socket sandbox. Missing diffusers prevented model/network/GPU work; retained tie tests contain CPU toy-model fixtures and need safety review before replay.

## Resumption authority and evidence retention

The operator subsequently authorized a dedicated **external CPU test virtualenv**, reusing the existing torch/CUDA installation without altering it, with resolution inspection first and a stop if it requires replacing torch/torchvision. GPU visibility stays disabled and model downloads off; small CPU toy-model fixtures are within scope. A separate provisioning worker owns that activity. The running model server, live weights and global packages remain untouched. Cleanup may delete only positively identified run-created artifacts, never pre-existing files or broad directory globs.

**Environment authorization is satisfied. V01 remains BLOCKED pending the actual rerun.** Preserve this original environment result unchanged; attach any rerun as a distinct evidence record with its own interpreter, dependency inventory and result axes. Phase A documentation can be reviewed, but runtime writes still require reviewed A plus actual V01 evidence. Raw machine paths, environment dumps and logs remain external; this committed record and linked public ledger carry resumable evidence without requiring temporary files.
