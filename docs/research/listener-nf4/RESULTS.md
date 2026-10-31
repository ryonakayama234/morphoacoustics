# EL-NF4 — RESULTS / append-only log

## 2026-10-31 D0
- Owner authorized independent research implementation and scientific judgment; did NOT authorize production promotion or merging.
- Research hypotheses, source candidates, support/coverage and primary thresholds prospective, before D1 code or any new SCUT measured IR scoring.
- Prior NF3 actual measured final C2 coverage 0/155 is a historical negative result, never fresh NF4 confirmation.
- **No EL-NF4 real measured evidence yet.** No numerical pass, failure or scientific efficacy asserted at D0.
- Data rights, exact receiver plane and future external assessment remain open.


## 2026-10-31 G0: original SCUT geometry/metrology-only evaluation
- Valid original host https://sofacoustics.org/data/database/scut/, inspected **measured** subject0001 and subject0009 with G0 workflow [41185941339](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41185941339), then [41186118906](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41186118906).
- 0001 SHA256 `267819899fc548a95eed6c1fd687fc6e38aa492e55a38834431c23f7cf041b9f`; 0009 SHA256 `ac109e37c9bf2a8c278ee74ccf486ebe4b1e1d59d00a61ac1a2f6355384179f7`.
- Geometry each: 6048 positions = **864 directions × seven distances** [0.20,0.25,0.30,0.40,0.50,0.75,1.00] m; 96kHz, FIR 512, SOFA SimpleFreeFieldHRIR, zero Data.Delay, az 0..355°, elevation -30..80°. Published 2018 paper's 685 directions and public file's actual 864 must not be conflated.
- 20° az × 10° elevation geometry yields 216 occupied groups, hash assigns 87 train / 43 selection / 43 calibration / 43 final groups before a conservative 5° acoustic buffer. Original source-position block digest `482d0da15e8efe0a17ab744fcc362ed67c9c06976eb5af9043ab1a8fb3c4c146`.
- File GLOBAL:License says **`CC 3.0 BY-SA-NC`**: research use only, no commercial Studio model/artifact or source redistribution, exact terms/derivatives rights require independent audit.
- Physical acoustic receiver/microphone reference plane and stimulus normalization remain **UNVERIFIED**. Numeric claims restricted to relative measured HRIR, not absolute physical ear response.
- Pre-acoustic geometry-only precise allocation/radial folds frozen in [PREREGISTRATION_V1_1](PREREGISTRATION_V1_1.md) at commit `bf8a5119032d9330afa2409669450e853e282987`. No real Data.IR values accessed during this audit.
- Audit workflow initially had a **false-green pipeline exit** during added JSON geometry summaries: NumPy int64 serialization crashed but tee hid the error. Corrected explicit JSON integer conversions and `set -o pipefail` before final successful G0 [41186118906](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41186118906). This was an infrastructure issue, NOT a scientific result.
