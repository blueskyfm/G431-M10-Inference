# G431-MM0 + Tesla M10: PCI BAR5 firmware experiment

> **Experimental result, not an official GIGABYTE BIOS.** Four physical M10 cards have booted after this change and Ubuntu enumerated 16 GPU devices. Five to ten cards have not yet been retested with the modified firmware.

![GIGABYTE G431-MM0 populated with ten Tesla M10 cards](G431_MM0_Tesla_M10_build.jpeg)

This project documents a low-cost inference host built from a GIGABYTE G431-MM0-OT and Tesla M10 cards. The photo shows ten cards physically installed; the verified post-change boot test is four cards only.

## Background

The system originally ran two or three physical M10 cards. With five cards, POST stopped at “Please wait for chips” and the BMC KVM showed code 70, before Linux started. No defective card was identified.

The hardware is a GIGABYTE G431-MM0-OT with MJ11-EC1-OT baseboard. The original BIOS was F09 (2021-09-14); the experimental image reports F10 in Ubuntu, while the BMC firmware page continued to show F09. BMC firmware is 12.61.39.

## Experiment

The experiment changes an AMI PciBus PCI resource exception for NVIDIA Tesla M10 PCI ID 10de:13bd, targeting BAR5 (configuration offset 0x24). The goal is to avoid legacy I/O-port resource pressure during firmware PCI enumeration. BAR0/BAR1/BAR3 and the NVIDIA driver are not changed.

After flashing, the server booted with four physical M10 cards; nvidia-smi -L | wc -l returned 16, corresponding to four GM107 devices per card. This confirms enumeration at four cards only. Five to ten cards, CUDA inference, sustained load, thermal/power behavior, and long-term stability remain untested.

## Review bundle and acknowledgements

- [Download the English review bundle](G431_M10_GitHub_Review_Package_EN.zip) — patch-builder, synthetic checks, verification results, and supporting notes; it does not contain a ready-to-flash RBU.
- [Read the community review draft](DISCUSSION_POST.md).
- The work was inspired by [crgregersen's m10dis project](https://github.com/crgregersen/m10dis). Thank you for documenting the Tesla M10 and BAR5 so clearly. This GIGABYTE firmware experiment is independent and is not endorsed by that project.
- The cards were found through [this eBay France listing](https://www.ebay.fr/itm/880037037060?chn=ps&norover=1&mkevt=1&mkrid=709-134431-41854-0&mkcid=2&mkscid=101&itemid=880037037060&targetid=2501626380638&device=m&mktype=pla&googleloc=9219961&poi=&campaignid=24236806942&mkgroupid=200469000416&rlsatarget=pla-2501626380638&abcId=10823391&merchantid=6995724&gad_source=1&gad_campaignid=24236806942&gbraid=0AAAAACadmUl68qTjSAJJBUjnD2wQGHmCx&gclid=EAIaIQobChMIgqXd_ZyCmAMVjrVoCR0UXhl0EAQYAiABEgL0-_D_BwE), at about €85 per card when checked; the listing and price may change.

The inference goal is to run several independent, quantized specialist agents around 6B parameters, not to combine all M10 memory into one giant GPU. Model fit and inference speed have not yet been benchmarked.

## Safety and scope

This is an unofficial experiment on one server. A full RBU made from a system dump is intentionally excluded because it may contain machine-specific data and redistribution rights for GIGABYTE firmware are unclear. Do not flash this experiment on another board or use someone else's system dump. Keep a known-good recovery path.

The public bundle includes the patch-builder and synthetic tests, not a certified firmware image. It is not proof that ten cards will boot or that inference workloads will be stable. Feedback and careful review are welcome before further tests.
