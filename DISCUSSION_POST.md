# Request for review: experimental GIGABYTE G431-MM0 BIOS change for Tesla M10 cards

I am building a low-cost inference server from a GIGABYTE G431-MM0-OT / MJ11-EC1-OT and Tesla M10 cards. The longer-term goal is to run several independent, quantized specialist models around 6B parameters as agents. I am not trying to combine all M10 memory into one large-model pool, and I have not benchmarked 6B inference yet.

I was inspired by the [m10dis repository](https://github.com/crgregersen/m10dis), particularly its useful documentation of Tesla M10 BAR5 and multi-GPU inference. Thank you, **crgregersen**, for publishing that project. My server and firmware experiment are independent from m10dis.

The G431-MM0 was a low-cost server choice. I found Tesla M10 cards through [this eBay France listing](https://www.ebay.fr/itm/880037037060?chn=ps&norover=1&mkevt=1&mkrid=709-134431-41854-0&mkcid=2&mkscid=101&itemid=880037037060&targetid=2501626380638&device=m&mktype=pla&googleloc=9219961&poi=&campaignid=24236806942&mkgroupid=200469000416&rlsatarget=pla-2501626380638&abcId=10823391&merchantid=6995724&gad_source=1&gad_campaignid=24236806942&gbraid=0AAAAACadmUl68qTjSAJJBUjnD2wQGHmCx&gclid=EAIaIQobChMIgqXd_ZyCmAMVjrVoCR0UXhl0EAQYAiABEgL0-_D_BwE), at about €85 each when I checked.

Here is the [photo of the ten-card physical build](G431_MM0_Tesla_M10_build.jpeg). It shows the cards installed; it does not mean all ten have been boot-tested. The post-change result currently confirmed is four physical cards / 16 enumerated GPU devices.

## Symptom

- Original BIOS F09 (2021-09-14); BMC 12.61.39.
- Two and three physical M10 cards booted.
- A five-card attempt stopped before Linux with “Please wait for chips” and KVM POST code 70. No bad card was identified.

## Experiment and current result

I modified the AMI PciBus PCI resource exception table to suppress I/O BAR5 (config offset 0x24) for NVIDIA PCI ID 10de:13bd. The aim is to reduce legacy I/O-port window pressure; BAR0/BAR1/BAR3 are not targeted.

After applying the experimental image, the server booted with **four physical M10 cards**, and Ubuntu reports nvidia-smi -L | wc -l = **16** (four GM107 devices per card). This is encouraging, but I have **not yet retested five cards**, and six to ten cards, CUDA inference, and long-duration stability are unverified.

I compared a BMC BIOS dump with the experimental payload: the region from offset 0x290000 onward, including the firmware volume containing PciBus at 0x294000, matches exactly. Ubuntu dmidecode reports F10, while the BMC page still says F09; the displayed labels are not identical sources of evidence.

The [public review bundle](G431_M10_GitHub_Review_Package_EN.zip) contains the patch-builder and synthetic test results, but not the full RBU. The RBU was made from my server's dump and may contain machine-specific data; Gigabyte firmware redistribution rights are also unclear. I do not recommend reusing a dump from another machine.

## Questions

1. Does this PciBus exception look like a reasonable way to avoid M10 BAR5 I/O-resource exhaustion on this board?
2. What additional UEFI or Linux resource checks should I run before moving from four to five cards?
3. Which POST/PCI resource logs would help separate BIOS resource exhaustion from power, bridge, or device-initialization issues?

This is an experimental, single-system result—not a supported BIOS or a claim that ten cards work. I welcome careful review before further tests.
