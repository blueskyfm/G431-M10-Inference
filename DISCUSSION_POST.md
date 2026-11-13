# Community review: G431-MM0 with Tesla M10 — from firmware to 24-GPU inference

I am building a local inference server from a GIGABYTE G431-MM0-OT / MJ11-EC1-OT and Tesla M10 cards. The project now covers the path from a firmware boot investigation to a six-card deployment serving 24 local GGUF model instances through one API.

The [build photo](G431_MM0_Tesla_M10_build.jpeg) shows ten cards installed, but the latest verified running configuration is **six cards / 24 independent 8 GiB GPUs**. Ten cards failed before Linux at POST code 70.

## Firmware investigation

With original BIOS F09, two or three physical cards booted, while a five-card attempt stopped before Linux at POST 70. Inspired by the BAR5 analysis in [crgregersen/m10dis](https://github.com/crgregersen/m10dis), I investigated an AMI PciBus resource exception targeting Tesla M10 PCI ID `10de:13bd`, I/O BAR5 at offset `0x24`.

The experimental image is labeled F10; it is not an official GIGABYTE release. The initial post-change report was four cards and 16 devices. Later, six cards booted and all 24 GPUs passed a CUDA memory-copy check. These are encouraging observations, but there is no controlled comparison proving the patch alone explains the increase in usable cards.

The supplied module passes 23 exception-emulation and eight caller-emulation scenarios. The [review bundle](G431_M10_GitHub_Review_Package_EN.zip) contains the builder and historical synthetic results, without a full RBU. The latest installed BIOS could not be dumped successfully, so its version label alone is not proof of binary identity. See [patch details](PATCH_DETAILS.md) and [current results](TEST_RESULTS.md).

## Putting the GPUs to work

Unsloth Studio manages llama.cpp GGUF runtimes, one per GPU. There are 24 instances using nine model variants, with named technical review roles and an OpenAI-compatible API:

- `quorum-fast`: a single selected expert.
- `quorum`: adaptive single-expert or small-panel review.
- `quorum-deep`: all loaded experts, followed by synthesis.

The complete 24-review path returned the correct result for `8/4` in 36.38 s with 24 usable reviews. This is a functional check, not a claim of frontier-model quality. A dedicated OpenCode dialogue profile was also tested. The [software directory](software/README.md) includes the API, model/role manifest, loader, service units, client instructions, tests and evidence.

This is llama.cpp-backed inference orchestrated by Studio, not demonstrated native Unsloth training on Maxwell. Expert roles are prompts, not specialist fine-tunes. M10 inference and ensemble techniques already exist; the contribution is this board-specific experiment and documented deployment.

## Feedback sought

1. Review of the AMI BAR5 exception and the limits of its synthetic tests.
2. Logs or controlled tests to distinguish PCI resource allocation from power-cabling and initialization issues in the ten-card POST failure.
3. Comparable measurements for single-model versus ensemble latency and answer quality on Maxwell GPUs.
4. Cold-boot restoration and sustained-load reports from similar configurations.

Thanks to crgregersen for publishing the original BAR5 investigation and to existing legacy-GPU inference projects. This project is independent; their work is acknowledged in [contributions and prior art](software/docs/CONTRIBUTIONS.md). Current evidence and outstanding validation are indexed in [TEST_RESULTS.md](TEST_RESULTS.md).
