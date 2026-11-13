# M10 expert serving with Unsloth Studio

This is stage 3 of [G431-M10-Inference](../README.md#from-boot-to-inference): using the GPUs made available by the hardware deployment. The firmware experiment and CUDA checks are documented separately; [TEST_RESULTS.md](../TEST_RESULTS.md) indexes evidence across all three stages. This serving layer does not itself fix PCI enumeration or establish the cause of a boot failure.

An experimental deployment on a GIGABYTE G431-MM0-OT: six Tesla M10 cards, 24 independent 8 GiB GPUs, named local GGUF experts and one OpenAI-compatible API. Unsloth Studio manages the llama.cpp inference runtimes; this is **not native Unsloth training on Maxwell**.

Hardware enumeration and CUDA-memory-copy validation are recorded in [hardware validation](docs/HARDWARE_VALIDATION.md). Read [contributions and prior art](docs/CONTRIBUTIONS.md) before making novelty or performance claims. The related firmware experiment is documented in [G431-M10-Inference](https://github.com/blueskyfm/G431-M10-Inference).

## Request paths

| API model | Behavior | Latency tradeoff |
|---|---|---|
| `quorum` | Local keyword routing: one expert for simple requests; up to three model families plus a synthesis for recognized technical topics | Simple requests avoid the ensemble; technical reviews can be slow |
| `quorum-fast` | One selected expert, no review/synthesis | Real backend SSE streaming; preferred for interactive chat |
| `quorum-deep` | All loaded experts, then a synthesis | Explicit expensive review, not a low-latency mode |
| `expert-N` | One configured expert with its role instruction | Direct access through the same API |

Routing is heuristic, not an independently trained router. Roles are review instructions, not specialist fine-tunes. More models are not evidence of higher accuracy. DeepSeek-R1 and SynLogic share Qwen ancestry and are not fully independent architectures.

`x_quorum` records selected experts, actual response counts, roles and elapsed time. Review failures are reported; a synthesis fallback is labeled. Tool/structured-output requests use one expert rather than allowing several models to execute tools independently. A separate evaluation is needed before claiming reliable autonomous coding/tool use.

## Models and GPU placement

`aggregator/experts.json` is the deployment manifest. It specifies one model per GPU, a role and a readable Studio model ID such as `expert-1-phi-python`. Physical cards contain four GPU chips; the `card_group` field is an enumeration group, not a verified physical chassis-slot label.

The validated deployment contains 24 loaded runtimes on 24 distinct GPUs and nine model variants: Qwen3-4B, Llama-3.1-8B, Mistral-7B, Gemma-3-4B, DeepSeek-R1-Distill-Qwen-7B, Phi-4-mini, Granite-4.0-H-Tiny, Nemotron-3-Nano-4B and MiniMax SynLogic-7B, all quantized GGUFs. The four new downloads have verified SHA-256 hashes in `evidence/model-downloads.json`. Check the retained per-model results in `evidence/` and the live `/health`/`/experts` endpoints. Models that fail the actual M10 runtime must not be reported as validated merely because their weights fit in memory.

## Dialogue

Point an OpenAI-compatible client at `http://SERVER_IP:9000/v1`, choose `quorum-fast` or `quorum`, and use the existing Studio API key. Keep the key outside this repository.

```sh
export M10_API_KEY='your-private-key'
curl http://SERVER_IP:9000/v1/chat/completions \
  -H "Authorization: Bearer $M10_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"quorum-fast","messages":[{"role":"user","content":"Combien fait 2/2 ?"}],"max_tokens":32}'
```

`GET /v1/models` and authenticated `GET /experts` expose roles and placement. `GET /health` reports **actually loaded**, not merely configured, experts. Studio itself is normally on port 8888; select the saved external provider `M10 Quorum - experts locaux` to speak to the ensemble. Selecting an individual local GGUF directly in Studio bypasses the aggregator's role instructions.

## Deployment

This source reflects a particular machine; review and adjust user names, model directories and credential paths before reuse. It neither installs proprietary firmware nor downloads model weights automatically.

1. Install and validate an M10-compatible NVIDIA driver and llama.cpp CUDA runtime before using Studio. Record the actual runtime build and CUDA versions. GPU detection alone is insufficient.
2. Install Unsloth Studio, run it on port 8888 and create an API key. Put the key in a private readable file. Keep the runtime's private libraries out of global `LD_LIBRARY_PATH`.
3. Place the GGUF files named in `aggregator/experts.json` in the configured model directory. Each model must be tested with the deployed runtime, not just assumed compatible.
4. Copy `aggregator.py`, `experts.json` and `load_experts.py` to a dedicated application directory; create a venv and install `requirements.txt`.
5. Install the adapted systemd units. The model loader uses explicit GPU IDs, `alongside: true` and 8192-token contexts. It skips resident experts and restores the configured set after Studio starts. Cold-boot restoration must still be tested on the real machine.
6. Enable the loader and aggregator, check their journals, then verify per-expert inference and both API modes. Do not mark all configured experts ready until `/health` and the inference checks agree.

The NVIDIA persistence drop-in initializes device nodes as root before the daemon drops privileges. It addresses the observed missing-device startup failure; it is not a new GPU driver.

## OpenCode

See [the client guide](docs/OPENCODE.md). Add a distinct provider ID so an existing Unsloth server is preserved. Match the context budget to the real 8192-token runtimes, and use a short chat-agent prompt for interactive latency. The dialogue profile disables tool use rather than advertising untested agentic coding capabilities.

## Verification and performance

```sh
python -m pip install -r requirements.txt
python tests/test_aggregator.py
```

The 15 regression checks cover single-call simple routing, three-review synthesis, 24-candidate consolidation, backend SSE error status, tool-request single routing, unavailable-model handling, authentication and role/placement metadata. They do not test real GPU model compatibility.

The initial repeated `2/2` prompt measured 11.343 s, 0.361 s and 0.333 s. These are short complete-response wall times with reused prompts, not general throughput or time-to-first-token benchmarks. A longer three-review technical request measured 178.05 s while other models were loading. No claim of consistent subsecond technical answers follows from the arithmetic result.

A final full-pool arithmetic review returned `2` for `8/4`, with 24 usable reviews and synthesis in 36.38 s. A short technical review with three variants took 28.82 s. These are functional smoke tests, not quality benchmarks. Individual tests with very small output budgets produced 17 exact answers, two correct answers with extra formatting, and five reasoning-only outputs; larger review budgets and disabled default Nemotron thinking avoided empty reviews in the full-pool test. See [serving evidence](evidence/serving-2026-11-13.json).

The deployed llama-server reports version `0.9.0-dev`, commit `5f490d7`, with isolated CUDA 12.6 libraries. The exact source-to-binary build recipe was not retained, so this repository is a deployment case study rather than a fully reproducible backend build.

The 163 GB Qwen3.8-Flash-Next configuration and ten-card deployment have not been validated. Multi-GPU model splitting is a separate configuration that competes with resident experts for VRAM.
