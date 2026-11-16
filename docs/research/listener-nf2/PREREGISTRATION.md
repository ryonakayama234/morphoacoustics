# EL-NF2 v1.0 — PRE-IMPLEMENTATION PREREGISTRATION

**FROZEN BEFORE measured-data scoring.** Amendments must be new commits and explain whether they supersede a test. Scientific claim is relative bilateral measured artificial-head transfer in 0.2–0.5 m only; no eardrum Pa, 1cm, perception or motion.

## Measurement G0
Dataset: Zenodo 7316545 original `NF_LIB_HRTF_measured.sofa`, CC BY 4.0, published MD5 `4ba9cc348801a6805265c7168b5b3227`, expected source 49 directions × 4 radii at 0.2,0.3,0.4,0.5 m; 48 kHz two-channel, SOFA SimpleFreeFieldHRIR and FIR. SHA-256 observed at retrieval and pinned in evidence. Check coordinate orientation +X front, +Y left, +Z up; SourcePosition spherical degree, degree, metre or validated cartesian metre; Data.Delay explicit sample convention; verify unique direction pairing (max 2 degrees). Reject out-of-range, nonfinite, inconsistent or unverified parsing. `ReceiverPosition` / ear open-vs-blocked and acoustic pressure normalization remain UNVERIFIED.

## Fixed coordinates-only split (S1/S2)
After matching unique directions, sort by normalized azimuth [-180,180), then elevation, then norm of original source unit xyz; tie break stable source coordinate index. **Do not inspect HRIR values in split construction.** Direction groups assigned by sorted index modulo 5:
- final test directions: index % 5 == 0 (approximately 10/49); hide **all four distances** at these directions from model fitting, calibration, algorithm choice and model selection.
- validation directions: index % 5 == 1 (approximately 10/49), all four distances withheld from training. Validation can guide model selection but must never tune final test results.
- training directions: other indices (approximately 29/49).

S1 direction holdout: target at 0.2 and 0.5 m final directions; only same-radius training directions allowed.
S2 joint holdout: targets at 0.3 and 0.4 m final directions; **ALL 0.3 / 0.4 m HRIR across training directions are excluded for S2 model construction**; use training directions only, with radii 0.2 and 0.5. This isolates direction-and-distance interpolation simultaneously. S1/S2 target positions are same final direction clusters. Evaluation truth is opened only after model choices are frozen. S2 tests at interior distances, not radial extrapolation. Validation uses equivalent direction split with both measured interior bins withheld from candidate fitting. No acoustic values from final test directions enter normalization, delay estimation, fitting, nearest-point selection or calibration.

## Model comparison (frozen)
B0 = nearest trained direction at same target radius S1; for S2 nearest direction × nearest radial endpoint, deterministic radius tie-break 0.2 m, no oracle.
B1 = 3-nearest unit-sphere directions inverse angular-distance weighted, same radius in S1; for S2 bilinear weighting across endpoints 0.2 and 0.5 in radius. Unaligned HRIR samples. Normalize weights on train metadata only.
C1 = B1 geometry, per-ear *training-only* peak-arrival separation and reconstruction: interpolate peak arrival times with same weights, align training HRIR to a fixed anchor before mixing, restore predicted arrival. Both HRIR content and time shifts solely from training data. For S2, use four spatial/radial vertices (3 directions × 2 radii). No learned model tunables; C1 tests the delay-separation hypothesis H1.
C2 / spherical harmonic candidate is NOT included in v1.0 main final gate; adding it requires new prereg and must not cherry-pick favorable test results. Analytic free-field is a separate synthetic sanity oracle only, not a measured-head control.

## Metrics
Primary: four-band [500,1000), [1000,2000), [2000,4000), [4000,8000) Hz ILD: 20log10(left/right Fourier L2 amplitude); pooled median absolute error across four bands and all final S1/S2 direction groups. Secondary: ITD error in microseconds via [500,1500]Hz filtered interaural xcorr with parabolic sample refinement; individual left/right log spectral shape error after removing per-ear log-magnitude mean over 500–8000 Hz (diagnostic, NOT absolute Pa); 95th-percentile four-band ILD error and regional max. Avoid computing absolute amplitude transfer accuracy without calibrating source/receiver planes.
Inferential unit: **held-out direction**, with S1/S2 and bands preserved as correlated records. Paired direction-cluster bootstrap (2,000 resamples seed 20261030), distribution of median(error_B1)-median(error_C1). Summarize S1 and S2 separately, and target radial bins 0.2/0.3/0.4/0.5. Report B0/B1/C1 all.

## Engineering gate G3 (provisional threshold frozen now for this study)
`GO_LIMITED_NUMERICAL_CANDIDATE` iff G0 + synthetic gates pass, C1 pooled primary median ≤0.8 × B1 median, 95% paired-bootstrap lower bound >0 dB, S1 AND S2 median C1 < B1, C1 median absolute ITD ≤ B1 median absolute ITD + 25 microseconds, and no silent invalid/unsupported accepted inputs. Negative result is `REVISE_OR_REJECT`, not a broken CI; missing/incompatible data `INDETERMINATE`. Engineering threshold is NOT a perceptual threshold. If C1 is similar to simpler B1, select B1 as engineering reference even if numeric gate marginally passes; this selection must be separately justified without altering G3.

## Precommitted validity
Input query r must satisfy 0.2≤norm(r)≤0.5 m and directional support within the convex local angular cap spanned by training directions; no out-of-domain extrapolation. Validation/test positions outside support are recorded UNSUPPORTED, not counted as successful predictions; report coverage and explicit noncoverage. A three-nearest-neighbor angular cap can be computed from coordinates only; refusal threshold of max angular distance 45° to nearest training direction (engineering guard) is fixed before testing. If <8 final directions supported, outcome INDETERMINATE.

## Gates
G0 measurement/audit; G1 frozen prereg; G2 synthetic and mutation/refusal tests; G3 real measured final holdout and arithmetic-audited evidence; G4 separate blind headphone audition if pursued; G5 reviewer distinct from author before any adoption. Never merge automatically. CI success does not mean human validation.
