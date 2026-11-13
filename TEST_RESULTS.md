# Reported results and remaining validation

These are the author's reported observations and archived synthetic results, not new hardware tests performed when writing this document.

| Configuration or check | Evidence | Limit |
|---|---|---|
| Original F09, 2–3 M10 cards | Boots; basic GPU detection | No sustained inference benchmark supplied |
| Original F09, 5 cards | POST stops with “Please wait for chips”, KVM code 70 | Resource exhaustion is a hypothesis |
| Experimental image, 4 cards | Ubuntu command nvidia-smi -L | wc -l returned 16 | Enumeration only; four GPU devices per M10 |
| Exception emulation | Archived emulation_results.json, 23 cases | Synthetic inputs and selected routines |
| I/O BAR caller emulation | Archived caller_results.json, 8 cases | Mocked PCI writes and list insertion |
| Experimental image, 6 cards (2026-11-13) | 24 PCI/NVIDIA GPU devices; 24 successful 1 MiB CUDA memory-copy round trips | No sustained compute/load test |
| Experimental image, 10 cards | KVM: “Please wait for chipset”, POST 70; repeated boot events | Root cause unproven; no Linux reached |
| 5, 7–9 cards after modification | No separately controlled test retained here | Do not infer these outcomes from six/ten cards |
| Selected GGUF text-generation requests | Actual Studio/llama.cpp replies, including MiniMax SynLogic and Microsoft Phi smoke checks | Not an all-device inference or quality benchmark |
| Sustained load, ten-card power/thermal behavior | No completed validation | No stability/safe-power claim |

F10 is the experimental SMBIOS version label, not an official GIGABYTE F10 release. The retained 2021 build date and BMC F09 display do not establish patch presence by themselves.

## Useful contributions

Report the exact board model, original BIOS package and module hash, experimental build hash, kernel and driver versions, physical card count and slot layout. Include the diagnostics folder from collect_diagnostics.sh after reviewing its contents. For a POST failure, include the exact message/code and whether Linux was reached.

Record cold-boot and reboot outcomes separately. Enumeration, a successful small CUDA workload, actual model inference, and sustained temperature/power behavior are separate milestones. Do not mark all of them successful based on nvidia-smi alone.

## Retained six-card evidence and software

See [hardware validation](software/docs/HARDWARE_VALIDATION.md), [machine-readable evidence](software/evidence/hardware-2026-11-13.json), and [software contributions and prior art](software/docs/CONTRIBUTIONS.md). The low-MMIO window observed with six cards is 480 MiB; 40 GPU BAR0 allocations at 16 MiB would require 640 MiB before other devices. This is a hypothesis to investigate, not a demonstrated cause of POST 70. The owner also raised possible Y-power-cable issues; these have not been verified.
