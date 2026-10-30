# EL-NF1 frozen preregistration v1.0 — 2026-10-30 JST

**RESEARCH_ONLY / NOT_ADOPTED.** Commit before numerical implementation and before unseen real-data evaluation. This record is immutable; subsequent amendments must append, not rewrite its empirical result.

## Measurand and metrology G0
Predict the **left/right relative artificial-head HRIR/HRTF response** as a function of source distance at a fixed measured direction; not physical Pa per source, human eardrum, ear canal, contact acoustics or perceptual ASMR.
Fixture: Marschall et al. 2023 Zenodo 7316545, original without low-frequency extension, file `NF_LIB_HRTF_measured.sofa`, published MD5 `4ba9cc348801a6805265c7168b5b3227`, 0.2/0.3/0.4/0.5m × 49 nominal directions, CC BY 4.0. Do not vendor source dataset. Verify SOFA convention, source coordinate type/units, common direction pairing, R=2 and left/right channel, Data.SamplingRate, additional Data.Delay in samples, non-finite/zero signals, fixture SHA-256 and open/blocked or unresolved receiver plane. If direction pairing <10 or relative channel comparability fails: stop / INDETERMINATE; never silently use ±9cm probes or assert absolute Pa.

## G1 intervention and blinded holdouts
F30: hide ALL 0.30m measurements, predict using 0.20/0.40m. F40: hide ALL 0.40m, predict using 0.30/0.50m. Test-distance acoustic data may never enter preprocessing fit, normalization, peak search of training IR, or parameter selection. Pair measured directions via **source coordinate metadata alone** (≤2deg angular, ≤0.015m radial bin, unique nearest), never via acoustic similarity.
- B: same-direction measured 0.50m response, common 0.5/r gain and travel-time adjustment (not true far-field HRTF).
- C0: same-direction unaligned effective HRIR linear distance interpolation.
- C1: estimate each ear's arrival from **training HRIR only**, time-align, linear-interpolate, then restore interpolated arrival.
- A free-field point source is *separate analytic oracle*, not an empirical Pa-to-HRTF comparison.

## Primary metrics and G3 decision
ILD = 20 log10(L/R Fourier L2 energy amplitude) in **[500,1000), [1000,2000), [2000,4000), [4000,8000) Hz**. Primary = pooled across folds/directions/bands median absolute ILD prediction error in dB, B vs C1. ITD = [500,1500]Hz filtered interaural cross-correlation peak with parabola fractional refinement, in microseconds.
Cluster bootstrap: resample *entire measured direction* with replacement, fixed seed 20261030, 2000 draws, paired median(error_B)-median(error_C1), 2.5/97.5% percentile CI; direction and frequency bands are correlated.
**GO_LIMITED_NUMERICAL_CANDIDATE** iff G0+synthetic tests pass, C1 pooled median error ≤0.8× B, bootstrap 95% lower bound >0 dB, F30 and F40 each have smaller median error, and C1 median |ITD error| ≤ B median +25µs. If C1 doesn't outperform simpler C0 meaningfully, prefer C0 as engineering selection. These are project *engineering* thresholds, not known human perceptual thresholds. Reject/REVISE/INDETERMINATE on failure rather than changing threshold post hoc. Zero band energies yield explicit failure, not an infinite or NaN pass.

## Claim ceilings and separation
No 1cm extrapolation, wet/dry contact, cartilage conduction, actual eardrum pressure, spatial motion, individualized hearing, loudness calibration, head tracking, human ASMR outcome, source/load feedback, Core schema change or Studio release. G4 blind listening and G5 independent physical/code review are separate from software/CI and numeric G3. Keep Draft/unmerged until explicitly approved.

Sources: https://zenodo.org/records/7316545 ; https://doi.org/10.1016/j.apacoust.2022.109173 ; https://www.sofaconventions.org/mediawiki/index.php/SimpleFreeFieldHRIR ; core #53 #156 #199 and PR #83 #129.
