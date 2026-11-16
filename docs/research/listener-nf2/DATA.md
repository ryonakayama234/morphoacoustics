# EL-NF2 — data and measurement contract

Original https://zenodo.org/records/7316545 / `NF_LIB_HRTF_measured.sofa` / CC BY 4.0. Published MD5 `4ba9cc348801a6805265c7168b5b3227`; independent SHA-256 recorded on execution. Do not check in source dataset.

Expected SimpleFreeFieldHRIR, FIR, Data.IR [196,2,N], Data.SamplingRate 48000 Hz, optional Data.Delay 1×2 or M×2 samples; SourcePosition spherical azimuth/elevation/radius [degree,degree,metre] or vetted cartesian [metre]. Basis +X front, +Y left, +Z up. Radii 0.20/0.30/0.40/0.50 m each 49 measurements; uniquely matched unit-direction tuple across radii within 2 degrees. Filename alone is not integrity verification.

`ReceiverPosition` / exact acoustic port, canal entrance, free vs blocked ear, calibration and source reference pressure are NOT VERIFIED, so only relative left/right artificial-head transfer can be claimed. A sample-index delay is not seconds. All model/time origin and normalization provenance must be explicit.

Evidence records dataset SHA-256, published MD5 validation, code SHA-256, git prereg commit, split indices, all final prediction errors, medians, CI, supported query count, reasons for refusals and reviewer state. Never overwrite an existing evidence path. Reject NaN JSON. Missing data or inconsistent metadata leads to INDETERMINATE/INVALID, not fabricated measurements.
