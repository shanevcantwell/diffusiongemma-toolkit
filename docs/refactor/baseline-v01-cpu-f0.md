# V01 CPU F0 — distinct successful rerun

**EV-V01-RERUN: PASS for the retained no-GPU baseline**, with two skips and one known strict xfail. Executed **2026-09-16T01:47:28Z–01:47:53Z** in `cpu-f0-20260916T014405Z-ij_5aoig`. This is not a replacement for the [original BLOCKED result](baseline-v01.md); both original artifacts remain byte-for-byte unchanged.

[Compact evidence, versions and SHA-256 digests](baseline-v01-cpu-f0.json) · [success comment](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3#issuecomment-5690879296) · [provisioning grant](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3#issuecomment-5690837393) · [original blocked comment](https://github.com/shanevcantwell/diffusiongemma-toolkit/issues/3#issuecomment-5690521128).

## Observed results

- All **17 retained files**, **295 collected; 292 passed; 2 skipped; 1 strict xfail; zero failures, errors or collection errors**. Full pytest, independent collection and coverage-backed rerun each exited 0. Selection: `tests --import-mode=importlib -m 'not live and not e2e' -p no:cacheprovider`; plugin autoload disabled, no continue-on-collection-errors. Existing CPU toy-model fixtures ran; no dependency stubs were introduced.
- Skipped: `tests/test_chat_template_thinking.py::test_injected_think_message_differs_from_native_by_exactly_one_newline` and `tests/test_chat_template_thinking.py::test_trailing_newline_in_injected_content_is_trimmed_so_parity_is_unreachable`. Tokenizer/processor absent from the fresh offline cache; no download attempted.
- Strict xfail: `tests/test_ingress.py::TestExactTemperatureRunLevelIngress::test_t_min_equals_t_max_is_accepted`, preserving [source issue #110](https://github.com/shanevcantwell/ComfyUI-DiffusionGemma/issues/110), not repairing it.
- Statement coverage: **903/1315 = 68.6692%**, 412 missing, 19 excluded, 23 `dgemma`/`surfaces` files. **No branch coverage or configured/global floor**. This does not certify source-only scoped coverage obligations.
- Separate provenance stdlib regression: **3 passed**, exit 0; not product behavior or a fresh history scan.

## Environment and preservation

Python **3.12.3**, pytest **9.1.1**. CPython `venv --system-site-packages` reused existing user-site after venv-local packages; no `.pth`, `PYTHONPATH`, `sitecustomize` or checkout injection. Existing torch **2.11.0+cu128**, torchvision **0.26.0+cu128**, numpy **1.26.4** and CUDA stack were untouched. Shared transformers **5.14.1** remains unchanged; the venv uses the committed **5.13.0** pin, diffusers **0.40.0**, auto-round **0.15.1**, nvidia-ml-py **13.610.43** and coverage **7.16.1**.

Resolver inspection preceded installation of **12 exact SHA-256-locked wheels (20,536,318 bytes)**, then offline installation from the owned wheelhouse without dependency re-resolution. The JSON lists every installed wheel version/hash, relevant effective versions and external lock/evidence digests. It was distilled from `baseline/sanitized-summary.md`, `baseline/summary.json` and `evidence/summary-readback.log`, cross-checked against retained run artifacts; raw logs/hostnames/local absolute paths are not published.

**Shared-base, non-hermetic environment: dependency health is not PASS.** `pip check` exited **1**: unrelated shared `gtts` conflicts with venv-local click, shared `flite` with venv-local requests; shared `httpx2`/idna conflict predates provisioning. These recorded conflicts were not repaired. The lock replays the venv delta against the recorded shared inventory, not a standalone hermetic environment.

Before/after preservation evidence matches **40 product/test files, 23 original-baseline files, 6 source configuration files and 164 shared distribution records**. Distribution comparison covers versions/locations/metadata hashes, not every binary byte. Concurrent documentation is outside runtime digest comparison. No pre-existing artifacts were overwritten/deleted; no checkout bytecode/test caches were generated.

CUDA visibility was empty and Hugging Face/model access offline with a fresh owned cache. No GPU, real weights, server/model-management calls or model downloads; no OS socket sandbox claimed.

## Gate scope

V01 has usable F0 evidence. **A04 independent review remains PENDING; B is not implemented and remains gated on A04.** The original infrastructure failure remains BLOCKED for its own environment. This retained-suite result does not certify new boundary enforcement, source-only tests, installed artifacts, Python/MCP isolation, downstream Comfy, strict protocol, live/GPU or release readiness. C–F remain separately deferred.
