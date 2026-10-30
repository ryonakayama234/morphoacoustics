# EL-NF1 — research data contract

Original dataset Marschall et al. 2023 [Zenodo 7316545](https://zenodo.org/records/7316545), unextended `NF_LIB_HRTF_measured.sofa`, published MD5 `4ba9cc348801a6805265c7168b5b3227` and dynamically recorded SHA-256. CC BY 4.0, no source data vendoring.

**Input required:** `SOFAConventions=SimpleFreeFieldHRIR`, `DataType=FIR`, `Data.IR[M,2,N]`, fixed 48000 Hz, `Data.Delay[1,2]` or `[M,2]` in **samples** (or absent), spherical sources in degrees/degrees/metre or vetted cartesian metre. Source positions must match four radius bins, each exactly 49 measurements, each reference direction within 2 degrees uniquely paired. +X front, +Y left, +Z up. The two channels use the dataset's L/R measurement order, not fabricated ideal ear probe points.

**Output evidence:** input/runner SHA-256, original MD5, convention/reference-plane uncertainty, number of paired directions, heldout and training indices, all model errors, medians, paired bootstrap CI, numeric candidate verdict, G4/G5 held separately. The evidence file is never overwritten; JSON forbids NaN.

**Refusals:** INVALID for inconsistent dimensions, nonfinite, negative delay or bad file hash; UNSUPPORTED for unrecognized SOFA convention/units, ambiguous geometry/direction, unsupported sample rate, unmeasured conditions; INDETERMINATE for zero energy or inability to make reliable inference. None silently creates calibrated physical pressure, drum pressure, contact or perceptual claims.

Known limitation from G0a #129: `ReceiverPosition` can be ambiguous, including spherical with only metre units, so receiver geometry/open-canal/blocked-canal state is **UNVERIFIED**. Relative L/R result is not calibrated absolute Pa, nor validated source-to-ear physical pressure.
