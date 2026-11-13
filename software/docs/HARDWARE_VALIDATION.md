# Six-card validation, 2026-11-13

Six physical Tesla M10 cards expose 24 independent GM107 GPUs, each with 8192 MiB VRAM. They are not six unified 32 GiB devices. This boot used Ubuntu kernel 7.0.0-43-generic and NVIDIA 580.178.04, with the experimental F10 SMBIOS label.

All 24 devices passed context creation, a 1 MiB device allocation, a host-to-device copy, a device-to-host copy, full byte comparison and resource cleanup. The portable ctypes test is in `scripts/cuda-memory-check.py`. This checks a working CUDA memory path, not GPU arithmetic, workload quality or sustained stability.

Ten cards previously looped before Linux, with the KVM showing `Please wait for chipset` and POST code 70. The owner subsequently raised a possible Y-power-cable issue. That hypothesis has not been verified. No conclusion about a specific cable's safe power rating follows from this project.

The six-card boot advertises a low MMIO window from 0xD2000000 to 0xEFFFFFFF: 480 MiB. Each GPU's BAR0 is 32-bit, non-prefetchable and 16 MiB: 384 MiB for 24 GPUs and 640 MiB for 40 GPUs. The current window would be too small for ten cards' BAR0 allocations alone. Whether firmware enlarges it dynamically, and whether exhaustion causes POST 70, remains unproven. Above-4G allocation already accommodates the 64-bit BAR1 and BAR3 windows; it cannot make a hardware 32-bit BAR0 into a 64-bit BAR.

Linux still reports unassigned legacy I/O resources/BAR5 on this boot. Those warnings did not prevent the observed NVIDIA enumeration and CUDA-copy passes. Do not translate them directly into a claim that inference is impossible.

For the supplied RBU:

- SHA-256: `749fff29e1b30f281018ee90e232ec63fb97bcbf00a1342a834c46faae074ddb`
- Extracted modified PciBus SHA-256: `fb7961dc3a342ce1580ec1a892d4986a542ab60819ac83c88cd1e406ee5450cc`
- Reconstructed original PciBus SHA-256: `f252384354d29c590f6e846b2b36326970057f440575e0ae49e639dbcf852fc0`

The installed BIOS was not dumped successfully. The F10 label alone is not binary proof that the installed module matches the supplied file. Full machine-specific firmware dumps and credentials are excluded from the public software package.
