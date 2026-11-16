# EL-NF3 v1.0 — frozen prospective protocol

**2026-10-30 JST | Issue #256 | RESEARCH_ONLY / NOT_ADOPTED / DO NOT MERGE AUTOMATICALLY.**

## Purpose and measurand
Predict relative left/right complex FIR responses of a **stationary artificial head** to a stationary *point-like test source* at a previously unmeasured position q=(r,az,el), under the dataset's own calibration/reference convention. Output is an estimated HRIR pair, **not calibrated eardrum Pa**, individualized hearing, ASMR pleasure, 1-cm contact, finite source patch, moving-source crossfades or Core's full coupled acoustic field. Positional interpolation only: a forward source signal is external and may be convolved for an *optional* separately gated audition, not counted as a measured vocal-performance result.

The prior EL-NF2 PR #255's final pooled C1-vs-B1 ILD point improvement 30.18% is **NOT proven**: direction-block bootstrap 95% CI [-0.0878, 1.4184] dB includes zero; nearest B0 better in S1 and validation. Final NF2 directions MUST NOT be used for NF3 tuning.

## G0 source integrity and metadata
Primary new fixture: Yuqing Li et al, KEMAR near-field measured original `KEMAR_NFHRIRmea_1cm.sofa`, https://zenodo.org/records/7626148 ; reported 83,448 measured spatial locations, 0.20–1.10 m, elevation -25..35 deg; nominal 1-cm distance step. Publisher MD5 `8e286f7f2ffa67973bb0eb2e37c158e2`. **NOT the simulated companion.** Observed SHA-256 MUST be recorded on retrieval; never invent one. Public page does not establish a specific license: **legal reuse/republication license PENDING**; no source-data vendoring or product distribution until verified. Validate SOFA convention/version, SourcePosition Type/Units and frame axes, ListenerView/Up and ReceiverPosition, actual channel assignment, sample rate, Data.Delay in samples, time origin, finite signals, unique coordinate bins, scope of microphone/canal open/blocked plane and amplitude calibration. Incompatibility -> INVALID/INDETERMINATE, never implicit guessed defaults. Inspect published adaptive-moving-source measurement correlation; 83k spatial points are not 83k independent heads. Numerical validity can be studied on lawfully accessed original files without redistributing them; authorization remains a separate gate.

Primary evaluation domain: 0.20 <= r <= 0.50m and **measured angular support**. Separate stress-test 0.50..1.10m, NOT in primary G3. Limit claims to same artificial head; Aalto Marschall 2023 Zenodo 7316545 is a differently measured head, previously analyzed, hence external *stress* not a new hidden confirmatory test. No extrapolation beyond measurement domain.

## H hypotheses
H1: local geometry-supported interpolation improves unseen angular block ILD against best baseline.
H2: time-origin/arrival-separated HRIR interpolation improves ILD *without* ITD/spectral regression; a maximum IR peak is NOT necessarily the first arrival.
H3: geometry/validation-calibrated risk yields lower **selective** error at matched coverage than baselines.
H4: improvement persists under held-out joint angle-radius cells and lower measurement density. Failure of any -> corresponding claim not adopted.

## Models
B0: nearest training spatial sample (Euclidean metric in source Cartesian metres, fixed training geometry).
B1: local inverse-distance weighted raw FIR response (train-only neighbors/weights).
B2: 3D Cartesian Delaunay simplex barycentric interpolation, constrained by available geometry; no out-of-hull extrapolation. If computationally infeasible at 83k nodes, prespecify deterministic decimated triangulation using coordinate-only anchors (record count and seed) *before test measurements*; no cherry-picked error-driven pruning.
C1: nearest-geometry raw FIR vs peak-arrival-separated interpolation replication of EL-NF2; disclose peak proxy rather than direct-path proof.
C2: local 2D angular triangulation of each available radial shell, interpolate within angular simplices and between bracketing radial shells; a bounded, training-only arrival estimator / fractional-delay FIR alignment; bilateral consistency; separately calibrated selective refusal. Angular chart seam duplication at +/-360deg, check radius and simplex geometry. If shell completeness prevents robust triangulation, **INDETERMINATE / revise in a NEW prereg**; no hidden nearest fallback in C2 primary metric.
Ablations C2a=geometry only, C2b=arrival only, C2c=geometry+arrival without calibrated guard. Baselines and C2 are evaluated on **identical accepted target positions** for paired primary tests; report full-domain coverage for each. If C2 improvement is attributable solely to rejection, the research claim fails.

## Splits (coordinate-only, before observing held-out IR values)
Unit of allocation = contiguous *20-deg azimuth x 10-deg elevation block*, with 5-deg coordinate buffer around final block edges; all radii at each angular block assigned together. Fix seed `20261030`. Stable SHA256(seed + integer angular block ID) rank to allocate: final 20%, calibration 20%, model-selection 20%, training remainder; exclusion buffers do not flow from final into any training/preprocessing/evaluation. Do not inspect acoustic values for split construction. Block distribution and exact indices/hashes stored prior to final scoring. Distinct radial experiments:
- S1: held-out direction blocks, *available same-radius training data*, evaluate 0.20..0.50m shell targets.
- S2: held-out angular blocks AND target distances [0.30,0.40]m; **exclude all 0.30/0.40m acoustic values from S2 predictor construction/calibration**, even for other angular blocks, using only *training radial shells 0.20 and 0.50m*. If dataset topology does not include required shells within tolerance 0.005m, mark S2 INDETERMINATE rather than alter the protocol.
- S3: train-only geometry decimation with prespecified coordinate seed, evaluate original final angular blocks, no use of final IR for anchor choice.
Bootstrap resampling unit = entire angular block, preserving all radii, ears and bands. Block dependence can remain due to spatial smoothing; report effective block counts, spatial correlations and sensitivity to coarser blocks, do not report pointwise p-values as independent.

## Numeric comparisons and gate G3
Four ILD bands [500,1000),[1000,2000),[2000,4000),[4000,8000)Hz: 20log10(L/R band Fourier L2 amplitude). Main loss median absolute ILD error pooled over held-out block x radius x band for same accepted points. ITD low band 500..1500Hz cross-correlation parabolic refine, per-ear centered log-spectral shape error, upper-tail ILD. Predeclare selection of the strongest baseline B0/B1/B2/C1 **on model-selection blocks only**, never final test. Compare C2 to that frozen selected baseline on identical accepted final points.

GO_LIMITED_NUMERICAL_CANDIDATE if G0/G1/G2 valid, paired pooled median C2 <= 0.85 x chosen baseline, block-cluster bootstrap 2000 resamples fixed seed 20261030 lower 95% bound of median-baseline minus median-C2 >0 dB, both S1/S2 medians improve, C2 ITD median <= selected-baseline ITD +25 microseconds, no marked spectral shape/tail regression under separately frozen numeric bounds after G0 data-quality audit and BEFORE opening final IR, and geometric support coverage >=80% of eligible final-domain queries. All G3 counts, refusal rates and same-coverage risk curves disclosed. Numerical thresholds are **engineering criteria**, not perceptual thresholds.
Calibration: model-selection stage fixes candidate; calibration blocks choose one guard threshold before final scores to target 80% eligible geometric coverage. Report selective-risk/coverage curve across 60/80/100% and empirical error-interval calibration. Never interpret conformal coverage as distribution-free under spatial dependence.
Fewer than 8 independently supported final angular blocks per S1/S2 => INDETERMINATE. Boundary, sample rate mismatch, missing/invalid IR, degenerate simplex, bad weights, invalid metadata => explicit refusal / INVALID. For G3 negative scientific result use REVISE_OR_REJECT, not CI failure.

## G4/G5 / production boundary
G4 headphone blind audition optional and separate; quantitative model fit does not establish human directional hearing or ASMR. G5 independent **different reviewer** of raw-data plane, provenance, gate math, leakage and code. Same author's audit script is not independent scientific review. Only separate owner-approved scope-limited adoption PR may add an optional version-pinned runtime to `asmr/`; no `src/`, Performance Contract, SMC, speaker behavior, Studio, sound product, or plugin API change in this research PR.

**Chronology:** This file must be committed alone **BEFORE** any EL-NF3 numeric code or measured holdout scoring. Changes to thresholds/protocol require prospective successor preregistration and explicit indication that results under this version cannot be retroactively reclassified.
