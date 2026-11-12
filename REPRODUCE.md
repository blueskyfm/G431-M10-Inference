# Reproduce the module-level experiment

This guide covers building and emulating one modified PciBus module. It does not build a flashable RBU. Only four physical M10 cards have been reported booting after the experimental firmware change.

## Inputs and tools

Download G431_M10_GitHub_Review_Package_EN.zip from this repository and extract it. Work inside its github_g431_m10_review directory. You need Python 3, a virtual environment, Unicorn, and UEFITool with support for extracting a PE32 section body. Record the versions you use. The original tool versions used to produce the archived results were not recorded in this bundle; requirements.txt is a dependency range, not a historical lockfile.

Obtain BIOS F09 for the exact G431-MM0-OT / MJ11-EC1-OT board from GIGABYTE support. Open the firmware image in UEFITool (extract the vendor archive first). Locate the firmware file with UI name PciBus, expand its sections, and use Extract body on its PE32 image section. Do not extract the entire FFS file or the section header. Save the result as patch/PciBus_original.pe.

The expected source SHA-256 is:

    f252384354d29c590f6e846b2b36326970057f440575e0ae49e639dbcf852fc0

Matching the F09 label alone is insufficient. Compatibility of every downloadable F09 package has not been established. If the extracted module does not have this hash, stop and report the package name, tool version and hash. Do not remove the builder's checks.

## Build and run

Copy requirements.txt from the repository next to the extracted patch and verification directories. From that directory:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
sha256sum patch/PciBus_original.pe
python patch/build_module.py
cp patch/PciBus_original.pe verification/
cp patch/PciBus_M10_BAR5_EXPERIMENTAL.pe verification/
python verification/verify_emulation.py
python verification/verify_bar_caller.py
python -m pip freeze > local-python-versions.txt
```

Use ordinary Python execution: do not use -O or PYTHONOPTIMIZE, because the existing scripts use assertions for their checks. The two PE inputs are deliberately absent from the public ZIP. The scripts load them from their own verification directory, not the current working directory.

A successful run reports 23 exception scenarios and 8 caller scenarios. It rewrites emulation_results.json and caller_results.json; save a copy of the archived results first if you want a comparison. The existing structure_checks.json is a historical report: these two scripts do not regenerate or validate a complete firmware image.

## What remains outside this guide

Reintegration, firmware-volume capacity and checksums, capsule/trailer construction, board-specific flash acceptance and recovery need a separately verified procedure. A .pe output cannot be flashed through the BMC. Do not rename it to .RBU.

Use collect_diagnostics.sh on each successfully booted configuration to capture evidence. For POST failures, retain the exact physical card count, slot positions, POST code and KVM message. Linux cannot collect logs from a boot that never reaches Linux.
