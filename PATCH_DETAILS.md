# Scope of the PciBus change

The builder accepts only a PE module with SHA-256 f252384354d29c590f6e846b2b36326970057f440575e0ae49e639dbcf852fc0 and the embedded layout checks. All offsets below refer to that module, not the complete BIOS image.

It copies the 16 existing 40-byte resource-exception records from offset 0x12a10 into an extended final .reloc section and appends one record. The appended record uses action 3, vendor 0x10de, device 0x13bd, mask 0xffff, kind 11 and BAR register 0x24. These field interpretations are specific to the investigated AMI implementation.

The registration instruction at 0x73ca is redirected to the appended table, and its count changes from 16 to 17. The script updates the final section and PE size fields and clears that section's discardable flag so the appended table remains available. It checks that the existing base-relocation directory is unchanged. It does not add a new absolute pointer.

## Expected effect and evidence

The hypothesis is that suppressing the M10 I/O BAR5 resource reduces legacy I/O window pressure during PCI enumeration. Direct exception emulation compares original and modified code for M10 BAR5, BAR0/BAR1/BAR3, ASPEED, I210, a neighboring NVIDIA device ID and samples derived from the 16 original records.

Caller emulation covers two device IDs, two BAR masks and two previous BAR values. PCI writes and resource-list insertion are mocked. For the target M10, it expects no list insertion, resource type zero and a final mocked BAR write of zero. The caller can assign size=1 after deletion; the test checks that type=0 still prevents insertion. This distinction matters when reviewing the result.

The tests execute selected x86-64 routines in Unicorn with synthetic data and stubbed helpers. They do not emulate complete firmware startup, PCI switches, actual bus transactions or GPU workloads. They do not establish the original hang's root cause conclusively.

The builder prints the output module's size and SHA-256. Retain that output with the source hash and tool versions when reporting a reproduction. A complete BIOS checksum report is not equivalent to hardware validation.
