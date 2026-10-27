# VF-1B2b EXPERIMENT — before-code hypothesis, gates and stop conditions

**Study planned 2026-10-27, code not yet written at preregistration commit.** Follow #215 and frozen VF-1B2a #216 exact head `d962364f7c4e1a9eb470e9bad14cd805fa632fed`. All reference numbers and measurement accuracy are public *before this design*; this is a **transparent exploratory external-data comparison**, not an independently blinded confirmatory experiment. We cannot claim model tuning isolation from knowledge of Table 2. No new voice rendering.

## Hypothesis / falsifier
- H_ref: published M6 real-life flow values can be transcribed precisely, converted to SI, and used for independent measurement-bounded quantitative *flow* comparisons. Fail if any of 12 table cells, source reference, physical unit conversions, or accuracy semantics are corrupted.
- H_transfer: #216's toy law `Q=Cd*Asep*sqrt(2 ΔP / ρ)`, with inherited `Cd=0.7`, `Asep=Amin` for parallel/convergent and `Asep=1.2*Amin` for the chosen divergent `Aexit=2Amin`, yields **shape ratios** 1.0 (conv/uniform) and 1.2 (div/uniform). Ask whether they lie within published M6 measured-accuracy ratio intervals at each ΔP. Outside at >=2/4 pressures triggers `M6_SHAPE_TRANSFER_DISCREPANCY`, independent of absolute flow normalization. This is NOT a physics-validity FAIL for a geometry-mismatched toy.
- H_geometry: M6 3D nonrectangular sinusoidal shape and reported taps are NOT representable by the toy linear-area 1D ramp, even with same area. Set `geometry_match=false` as a fixed precondition. Never promote G2 (quantitative intraglottal pressure validity) based on Q alone, or claim validated 1D Cd from apparent `Q/(Amin sqrt(2ΔP/ρ))` values.

## Fixed numeric conditions
- Four Δp=294, 491, 981, 1472 Pa; 3 glottis families (convergent, uniform, divergent). Published Q table in DATA; expected accuracy bound ±6 cm³/s. Same density assumption 1.21 kg/m³ as #216; no invented experimental air density, fluid pressure tap values, or flow uncertainty distribution.
- Unit transfer exact to published precision: |Δp-converted| <=1e-10 Pa, |Q-converted|<=1e-12 m³/s; bounds use published ±6 absolute accuracy without probabilistic interpretation.
- For each pressure: measured ratios `conv/uniform`, `div/uniform`, positive interval endpoint propagation, toy shape ratios 1.0,1.2; report each `outside_measured_interval`. Two or more divergences are a **diagnostic mismatch flag only**, without a matched-geometry physical error gate.
- Also report per-shape proxy absolute error in flow m³/s, but `absolute_comparison_qualified=false` because geometry and entrance/dissipation differ. Do not tune parameters or call this an estimated calibrated Cd.
- Independent toy analytic oracle: continuous sqrt pressure law for Δp>0, zero at Δp=0, paired sampling n=41/161 invariant, positive flow, fixed-wall work=0, stable geometric separation for the three toy shapes.
- Adversarial tests: replace one table value, invert pressure sign, confuse cm³/s with m³/s, swap one reference shape, fraudulently mark geometric equivalence, missing metadata, and poison the verdict. No silent data repair.
- Histograms/plots are optional; output CSV/JSON sufficient. stdlib-only Python experiment and unittest. Dedicated GitHub Actions runs tests before driver, archives evidence even when RED. SOURCE must remain research-only. Main tests can run automatically on the PR.

## Disjoint gate criteria
- G0: `PASS_REFERENCED_12_MEASUREMENTS` only after complete table, source/provenance/units/negatives and actual tests pass.
- G1: `PASS_TOY_MATH_AUDIT` only after independent ratio / sqrt-pressure / no-work controls. Do not interpret this as physically right.
- G2: `INDETERMINATE_NO_MATCHED_PRESSURE_TAP_PROFILE_OR_GEOMETRY` regardless of shape ratio outcome. Published pressure curves exist in figures, but the present table is ONLY flow data and the toy is NOT M6.
- G3: `NOT_APPLICABLE_NO_MOVING_WALL` (no tissue, no fluid-to-solid energy closure).
- G4: `VOICE_NO_GO` (no physical sound or Studio audition).
- Review: seek independent exact-head PR review. A green workflow without independent critical review is not a reviewed accepted scientific model. Only prospective pilot receipt may be merged after qualified review; retain Draft if unavailable.

## Stop / next decision
**Stop before VF-1B2c** if model geometry mismatches, pressure tap data lack defensible numerical calibration, energy-transfer derivation is absent, or independent reviewer is unavailable. Preserve actual state, CSV, unit/shape sensitivity, model-source limitations, negative-test failures and CI logs. Follow-up choices are (a) measured wall-tap digitization with quantified uncertainty and matched 3D geometry/model, or (b) separate moving-wall port-Hamiltonian / control-volume law derivation that remains research-only while G2 is unresolved. No negative damping, no waveform after-the-fact correction, no production graphs or panels.
