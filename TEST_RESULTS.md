# Validation: firmware, GPUs and inference

This is the current results index for the whole G431-M10-Inference project. Earlier firmware-only notes remain in the review ZIP; use this page for the latest retained deployment evidence. Observations below were collected at different times, not as one controlled comparison.

## 1. Firmware and boot

| Configuration or check | Retained result | What it establishes |
|---|---|---|
| Original F09, 2–3 M10 cards | Reported successful boot and detection | Historical baseline; no sustained inference benchmark |
| Original F09, 5 cards | POST stops before Linux, code 70 | Failure observed; cause unproven |
| Experimental image, 4 cards | `nvidia-smi -L` reported 16 devices | Original post-change enumeration report |
| Experimental image, 6 cards, 2026-11-13 | Linux and NVIDIA enumerate 24 GPU devices | Latest verified running card count |
| Experimental image, 10 cards | Repeated boot events, KVM “Please wait for chipset”, POST 70 | No Linux reached; no ten-card success claim |
| 5 and 7–9 cards after modification | No separately controlled result retained | Do not infer outcomes from six/ten cards |
| PciBus exception emulation | 23 scenarios pass | Selected routines with synthetic inputs |
| I/O BAR caller emulation | Eight scenarios pass | Mocked PCI writes and resource-list insertion |

F10 is an experimental SMBIOS label, not an official GIGABYTE release. The supplied module was extracted and checked, but the latest attempt to dump the installed BIOS did not complete. Displayed version labels alone do not prove binary identity. The original four-card report and current six-card evidence do not replace a controlled original-versus-modified firmware comparison.

See [patch details](PATCH_DETAILS.md), [reproduction](REPRODUCE.md), and [hardware details and hashes](software/docs/HARDWARE_VALIDATION.md).

## 2. CUDA and GPU placement

All 24 devices in the six-card configuration passed context creation, allocation, a 1 MiB host-to-device/device-to-host copy, byte comparison and cleanup. This checks the CUDA memory path; it is not a GPU arithmetic or sustained-load benchmark.

The serving deployment subsequently had 24 resident runtimes pinned to 24 distinct GPU IDs. The four new model downloads have recorded source repositories and SHA-256 hashes.

- [Live nvidia-smi image](software/evidence/nvidia-smi-2026-11-13.png) and [unmodified text](software/evidence/nvidia-smi-2026-11-13.txt), captured 2026-11-13 at 16:17:46 UTC
- [Hardware summary](software/evidence/hardware-2026-11-13.json)
- [Serving state, runtime versions and placement](software/evidence/serving-2026-11-13.json)
- [Model download provenance](software/evidence/model-downloads.json)
- [CUDA memory-check script](software/scripts/cuda-memory-check.py)

## 3. Model serving and client integration

| Check | Result | Limit |
|---|---|---|
| Loaded expert pool | 24 runtimes, nine model variants | Some variants share model ancestry |
| Individual arithmetic smoke tests at small output budgets | 17 exact answers, two correct with extra formatting, five reasoning-only outputs | Budget and thinking-mode sensitivity; not a quality benchmark |
| Full 24-review `8/4` request | Answer `2`; 24 usable reviews; 36.38 s | Functional end-to-end check, not proof each reviewer is accurate |
| Short SQL explanation with three reviewers and synthesis | 28.82 s | One technical example |
| Repeated `2/2` request | 11.343 s, then 0.361/0.333 s | Prompt reuse and warm/cache effects; not a cold-boot benchmark |
| Earlier, longer technical review during loading | 178.05 s | Different prompt and conditions; not directly comparable |
| OpenCode dialogue | Correct `2/2` reply through the dedicated profile | Tools and autonomous code editing not validated |
| API regression suite | 15 tests pass with simulated backends | Tests routing/API behavior, not real model accuracy |

Evidence: [individual outputs](software/evidence/inference-smoke-final.json), [full-pool response](software/evidence/deep-smoke-release-parsed.json), [initial arithmetic timings](software/evidence/arithmetic-initial.jsonl), and [OpenCode check](software/evidence/opencode-dialogue.json). Setup and test commands are in the [software guide](software/README.md).

## Open questions

- **Ten-card POST failure:** power cabling and PCI resource allocation remain hypotheses. The six-card low-MMIO window is 480 MiB; 40 GPU BAR0 allocations would require 640 MiB before other devices. Dynamic firmware allocation and its relation to POST 70 remain unverified.
- **Restart behavior:** model-restoration and NVIDIA initialization services are installed; full cold-boot restoration has not been tested.
- **Sustained operation:** no completed long-duration compute, thermal or maximum-power validation.
- **Model capability:** no comparative quality benchmark, native Unsloth training demonstration, or successful 163 GB model test.

When contributing results, report exact board and firmware/module hashes, kernel/driver/runtime versions, physical card count and slot layout. Record cold boot and reboot separately. Review diagnostics for private information before sharing. Enumeration, CUDA copies, text generation and sustained stability are separate milestones.
