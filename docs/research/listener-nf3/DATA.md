# EL-NF3 — DATA / metrology, rights and split contract

## Primary source
Zenodo https://zenodo.org/records/7626148 (Li et al, v1 2023): measured `KEMAR_NFHRIRmea_1cm.sofa` (reported 346.5MB, 83,448 locations, 20–110cm, -25..35° elevation, 0..355° azimuth); **published MD5 8e286f7f2ffa67973bb0eb2e37c158e2**. Companion `KEMAR_NFHRIRsim_1.5cm.sofa` is **not** the primary truth. A publication describes continuously moving sound source and adaptive filtering; do not treat adjacent 1cm measurements as independent. Exact measured topology must be audited; 1cm nominal radial spacing does not imply a complete rectangular angular grid.

**Right/status:** Zenodo web view exposes a "License" label but did not present a usable license identifier on examination on 2026-10-30. Record **LICENSE_UNVERIFIED**, do not assume CC-BY/CC0, no data copy in repository, no audio derivative distribution, no runtime/product adoption while unverified. Later verification must record license text, URL, retrieval timestamp and licensee limitations.

## Original-file audit checklist
- Original MD5 match and SHA-256 computed and pinned; verify measured filename and source Zenodo DOI.
- HDF5 SOFA: `SOFAConventions`, `DataType`, `Data.IR` axes and shape M×2×N, sampling rate, delay samples. Explicitly handle/deny nonzero `Data.Delay`; never silently ignore it.
- `SourcePosition` type/unit spherical [degree,degree,metre] or Cartesian [metre]. `ListenerView`/`ListenerUp` and coordinate transform. Confirm exact left/right channel assignment and receiver reference.
- `ReceiverPosition` presence is **not itself proof** of open-canal/blocked-canal or eardrum microphone. Source amplitude equalization, absolute pressure and time zero remain unresolved until independent evidence.
- Reject duplicated position bins, zero/NaN/Inf HRIR, inconsistencies, data corruption; log measured geometry coverage and sample-rate bin widths.
- Read source data locally or on controlled CI runner from original publisher, never vendor dataset.

## Allocation and leakage
Fixed in [PREREGISTRATION](PREREGISTRATION.md). Use spherical angular grouping by floor(azimuth/20 degrees), floor((elevation+25 degrees)/10 degrees); stable hash seed 20261030. Every radius of each angular group belongs to exactly one role. Direction blocks around final blocks require 5-degree excluded buffer: those samples may not be included in training or calibrator. **The training geometry and source coordinates may be known but target HRIR withheld.** Calibration set distinct from model selection, which is distinct from final.

S1: unknown angle blocks, measured same-radius training. S2: unknown angle + 0.30/0.40m radial values, train/calibration acoustic data restricted to 0.20/0.50m. No test/validation HRIR may enter peak/onset detection, global normalization, interpolation weights, solver selection or rejection calibration.

## Source claim boundaries
External Marschall/Aalto Zenodo https://zenodo.org/records/7316545 is a different artificial-head measurement and known to previous research. Evaluate as stress / implementation comparison only. Source data type, distance-reference origin and delay/normalization differences prohibit naive cross-dataset HRTF-pixel comparison.

Synthetic fixtures are freely authored numerical oracles, *not evidence about KEMAR anatomy*. All scientific verdicts require real measured heldout files and separate human/reviewer gates.
