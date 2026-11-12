# Reported results and remaining validation

These are the author's reported observations and archived synthetic results, not new hardware tests performed when writing this document.

| Configuration or check | Evidence | Limit |
|---|---|---|
| Original F09, 2–3 M10 cards | Boots; basic GPU detection | No sustained inference benchmark supplied |
| Original F09, 5 cards | POST stops with “Please wait for chips”, KVM code 70 | Resource exhaustion is a hypothesis |
| Experimental image, 4 cards | Ubuntu command nvidia-smi -L | wc -l returned 16 | Enumeration only; four GPU devices per M10 |
| Exception emulation | Archived emulation_results.json, 23 cases | Synthetic inputs and selected routines |
| I/O BAR caller emulation | Archived caller_results.json, 8 cases | Mocked PCI writes and list insertion |
| 5–10 cards after modification | No completed test reported | Ten-card photo proves physical installation only |
| CUDA inference and sustained load | No completed test reported | No performance or stability claim |

F10 is the experimental SMBIOS version label, not an official GIGABYTE F10 release. The retained 2021 build date and BMC F09 display do not establish patch presence by themselves.

## Useful contributions

Report the exact board model, original BIOS package and module hash, experimental build hash, kernel and driver versions, physical card count and slot layout. Include the diagnostics folder from collect_diagnostics.sh after reviewing its contents. For a POST failure, include the exact message/code and whether Linux was reached.

Record cold-boot and reboot outcomes separately. Enumeration, a successful small CUDA workload, actual model inference, and sustained temperature/power behavior are separate milestones. Do not mark all of them successful based on nvidia-smi alone.
