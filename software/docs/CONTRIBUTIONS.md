# Contributions, prior art and limits

This project documents an experimental integration on one GIGABYTE G431-MM0-OT / MJ11-EC1-OT. It does not claim to invent LLM inference on Maxwell GPUs, multi-GPU model splitting, expert routing, ensemble review, or OpenAI-compatible APIs.

## Contributions supported by retained evidence

1. A board-specific AMI PciBus resource-exception experiment targeting Tesla M10 PCI ID 10de:13bd and I/O BAR5. The public hardware repository includes its builder and synthetic checks. The supplied experimental F10 image contains that record. Undoing the builder's edits reproduces the exact published original-module SHA-256. The extracted module passes 23 exception-emulation and 8 caller-emulation scenarios.
2. A six-card boot on that board, with 24 GM107 devices enumerated by Linux and NVIDIA. All 24 passed a 1 MiB host-to-device/device-to-host CUDA memory copy and comparison. Subsequent serving tests confirmed 24 resident runtimes on distinct GPUs and a full-pool review with 24 usable responses. This is not a sustained compute, training or accuracy benchmark.
3. An integration of Unsloth Studio as the control plane, llama.cpp as the GGUF inference backend, one runtime per GPU, and a single API in front of named expert roles. Role specialization is a system instruction, not a claim of specialist fine-tuning.
4. Operational fixes and a reproducible configuration: explicit 8192-token contexts, GPU placement, startup restoration, NVIDIA device initialization before the persistence daemon drops privileges, model/role labels, and an OpenCode profile isolated from another existing server.
5. Measured latency and failures rather than universal performance claims. A repeated, very short arithmetic request took 11.343 s on the first measured call and 0.361/0.333 s on the next calls. Prompt reuse/cache and warm state matter. A longer three-review-plus-synthesis request took 178.05 s while model loading was still in progress; it is not evidence of consistently fast technical answers.

## What may be distinctive

The reproducible combination of this specific board, a firmware-level BAR5 exception, a six-card/24-device validation and an Unsloth Studio expert-serving deployment is a useful case study. No identical implementation was identified in this limited search. That is not proof of novelty or a worldwide first. A controlled original-versus-modified firmware test on an identical card/slot/power configuration is still needed to attribute the boot behavior conclusively to the patch.

## Prior art and acknowledgements

- [crgregersen/m10dis](https://github.com/crgregersen/m10dis): M10 BAR5/I/O-space analysis and a different late-power-on boot approach; inspiration for the firmware experiment.
- [h3rb3rn/llama.cpp-legacy-gpu](https://github.com/h3rb3rn/llama.cpp-legacy-gpu): existing legacy M10/M60 inference and multi-GPU work.
- [timoruohomaki/theworkstation](https://github.com/timoruohomaki/theworkstation): an existing M10 workstation/inference setup.
- [llama.cpp multi-GPU documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/multi-gpu.md): model splitting already exists; 8 GiB per chip does not by itself prohibit a larger distributed model.
- [Unsloth fine-tuning requirements](https://unsloth.ai/docs/fr/commencer/fine-tuning-for-beginners/unsloth-requirements): distinguish native training requirements from Studio's llama.cpp-backed GGUF inference. Native Unsloth training on M10 was not demonstrated here.

## Claims not supported

- Ten-card stable boot, safe maximum power, long-term thermal stability, native Unsloth training on Maxwell, or a 163 GB model running successfully.
- Accuracy comparable to a frontier model merely because many small models are consulted.
- A proven firmware/MMIO cause of the ten-card failure. Insufficient or faulty power cabling remains a hypothesis too.
- MiniMax M2/M3 running as an 8 GiB expert. The MiniMax model deployed here is SynLogic-7B, a Qwen2.5-derived reasoning model, not M2/M3.

## Final serving validation

Nine GGUF variants were loaded across 24 GPU-pinned runtimes. A full 24-review `8/4` request returned `2` in 36.38 s, with no abstentions. A separate short three-variant SQL review took 28.82 s. Fifteen mocked regression tests verify routing and API behavior; they do not measure model accuracy. Source provenance and SHA-256 hashes for four new weight downloads are retained. Cold-boot restoration has been installed but has not been reboot-tested.
