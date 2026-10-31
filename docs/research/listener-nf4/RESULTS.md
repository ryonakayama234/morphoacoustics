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


## 2026-10-31 D1-D4: 10 original measured SCUT subjects, frozen blind G3 NEGATIVE

**Official exact-head measured run:** [GitHub Actions 41186553120](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41186553120), SUCCESS, with [non-reconstructive numeric evidence artifact 13037051526](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41186553120/artifacts/13037051526) (30-day retention). Commit evaluated `e12c98c79fd9ff652bb3f61549abcbbdd801a231`. Versioned G0 allocation v1.1 frozen at `bf8a5119` BEFORE original measured HRIR values were read. Exact 10 original publisher SOFA files retrieved on disposable runner; all input SHA256 recorded in [MEASURED_SUMMARY_2026_10_31.json](MEASURED_SUMMARY_2026_10_31.json), along with 20 pre-truth prediction-seal SHA256 hashes. No original FIR data or models' HRIR coefficients committed/uploaded.

**Program chronology:** The first original-data CI [41186449407](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41186449407) stopped BEFORE Data.IR access because 3D Cartesian -> spherical floating precision put boundary directions into wrong angular bins, differing from G0 direct spherical. It was a software problem (not an acoustic score or negative scientific verdict). The fix rounds az/el to 6 decimal degrees BEFORE the unchanged frozen floor/bin formula. A synthetic 864-direction grid regression and Python 3.11/3.12 checks pass. The successful real-data run then scored the unchanged frozen geometry/model/gates, without altering thresholds against final data.

### Frozen development model choice
- **Baseline B3-o4-l0.03:** development selection pooled median ILD **1.4532 dB**.
- **Best eligible proposed candidate C4-o2-l0.1:** development selection pooled median ILD **2.6045 dB**, already weaker than B3. This is a legitimate negative development observation; no final-result-driven model replacement.
- C3 on development performed worse still; all development model diagnostics included in real evidence. These figures are development-only, not final proof.

### Final original measured confirmation (subjects 0009 and 0010)

| Preregistered metric, exactly matched accepted target positions | B3-o4-l0.03 | C4-o2-l0.1 | Gate |
| --- | ---: | ---: | --- |
| Pooled median four-band absolute ILD error | **2.06708 dB** | **2.34171 dB** | **FAIL**: proposed candidate **13.3% worse**, not >=15% better |
| Paired block 95% CI, baseline minus candidate | \- | **[-0.83938, +0.10474] dB** | **FAIL**: includes zero |
| Broadband cross-correlation ITD error median | 93.75 μs | **20.83 μs** | PASS relative noninferiority; not a localization study |
| Centered monaural spectral RMSE median | 4.92171 dB | **4.46120 dB** | PASS relative noninferiority |
| Absolute ILD error p95 across bands | **10.70323 dB** | 11.62872 dB | PASS tolerance: deterioration +0.92549 dB <=1dB |
| Geometric computability | 344/344 | 344/344 | Global field resolves NF3-style zero-geometry coverage, **not accuracy** |
| Support Atlas accepted query coverage | - | **242/344=70.35%** | **FAIL**: <80% |
| Distinct accepted (subject, angular block) groups per fold | - | S1=86; S2=86 | PASS computational count; 43 angular block IDs repeated on two subjects |
| Both S1 and S2 improve | - | No | **FAIL** |

**G3 = `REVISE_OR_REJECT` / `NOT_ADOPTED`**. Evidence arithmetic audit **PASS_ARITHMETIC_ONLY** recomputed from committed-source code independent of the predictor; no distinct scientist reviewed the physical assumptions. All raw prediction buffers are sealed on the runner BEFORE loading the withheld IR; 20 seal manifests and hashes are in downloadable numerical artifact.

#### Spatial/radial breakdown — same accepted rows in each condition

| Case | Accepted / Eligible | B3 ILD median | C4 ILD median |
| --- | ---: | ---: | ---: |
| Subject 0009 / S1 | 57/86 | 1.7827 dB | 2.5367 dB |
| Subject 0009 / S2 | 64/86 | 1.7881 dB | 2.1208 dB |
| Subject 0010 / S1 | 57/86 | 1.9750 dB | 2.3511 dB |
| Subject 0010 / S2 | 64/86 | 2.2456 dB | 2.4946 dB |
| Pooled S1 | **114/172=66.28%** | **1.9320 dB** | **2.4881 dB** |
| Pooled S2 | **128/172=74.42%** | **2.1225 dB** | **2.3053 dB** |

C4 is worse than B3 in all four per-subject/fold groups by the preregistered median ILD measure; there is no subject or fold success concealed by a pooled failure.

#### Frequency-resolved posthoc diagnostics — NOT new gate / no retuning
Four original frequency bands on 242 same accepted positions:

| Band | B3 median absolute ILD | C4 median absolute ILD | Observation |
| --- | ---: | ---: | --- |
| 500–1000 Hz | **0.5316 dB** | 4.4241 dB | C4 markedly worse |
| 1000–2000 Hz | **0.8752 dB** | 2.4406 dB | C4 worse |
| 2000–4000 Hz | 2.9646 dB | **1.7794 dB** | C4 better |
| 4000–8000 Hz | 6.0277 dB | **2.2370 dB** | C4 better |

This **frequency-dependent tradeoff** is observed, not explained causally. Candidate mechanisms to investigate in a NEW pre-registered study: arrival-based alignment and amplitude bias at low frequencies, basis order/ridge regularization, FIR truncation and C4 local correction. A <2kHz B3 / >2kHz C4 hybrid on THESE already-opened final targets would be posthoc model selection, **not a valid NF4 improvement**.

#### Operational support atlas analysis
- G0 geometric/global model predicted at all 344 final positions; **none of these were refused for unsupported 25° triangles**.
- Separately calibrated nearest-train-distance thresholds: **S1 0.087156m**, **S2 0.126795m** (chosen from subjects 0007/0008 only).
- Applied to final 0009/0010, these accepted 242/344, not the target 80%: evidence of an operational distribution shift between calibration and final spatial blocks. Rejecting 102 cases must NOT be counted as perfectly predicted.
- Posthoc conditional candidate median ILD is **2.342 dB accepted** versus **3.088 dB rejected** (candidate predictions were available numerically even for risk-rejected positions), so the geometric risk rank excludes some harder C4 positions, **but not enough** to satisfy coverage or beat B3. B3 median on accepted 2.067 dB versus rejected 2.078 dB.
- Supplemental *posthoc* sensitivity bootstrap resampling angular BLOCK IDs (43 unique across two subjects rather than each subject×block as separate cluster) gives pooled paired 95% interval **[-0.9274, +0.2510] dB**, also spanning zero. It is NOT a replacement for the registered CI and makes no new significance claim.

#### Interpretation and evidence limits
1. The global field is computationally defined across these angular holdouts, an applicability improvement over NF3 C2's 0/155, but NF4 **fails empirical predictive accuracy**, so global coverage is not physical correctness.
2. The arrival-separated/local-residual C4 improves cross-correlation ITD and centered spectral-shape RMSE, plus 2–8kHz band ILD, but loses markedly at 500–2000 Hz and overall. No claim of better perceptual position, physical ear transfer, voice or ASMR perception.
3. Geometry-calibrated selective prediction has partial error ranking utility but measured 70.35% acceptance fails the declared 80% gate. Calibration-set percentile does not guarantee spatially blocked test coverage.
4. Experimental SCUT source files state `CC 3.0 BY-SA-NC`; **commercial rights absent**. Exact microphone plane, source reference and absolute normalization remain unverified. Source SHA256 hashes pinned in frozen summary, but only 0001/0009 had independent G0 prior hash pins; hashes of other eight were observed first at G3 from publisher-hosted downloads, NOT a publisher signature.
5. **No G4 human blind listening; no G5 distinct science reviewer. Do not merge/release into `asmr/`, Core, SMC or Studio.**

The main research hypothesis is **REJECTED for this frozen numerical protocol**. Preserve the entire negative result, and pursue a new model/split/dataset only under a new D0 and fresh independent acoustic validation.
