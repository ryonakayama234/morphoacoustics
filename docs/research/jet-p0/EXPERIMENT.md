# JET-P0 — EXPERIMENT (frozen before implementation)

**Gate A**: experiment-only model proposal on Core `main` 6869cfec04041393eae44485ce2fc91f002114f5. Linked [#30](https://github.com/ryonakayama234/morphoacoustics/issues/30). No claims of naturalness or self-oscillating vocal folds.

## Falsifiable hypotheses
H1 (jet): at identical aperture and 800→1600 Pa, **unperturbed Bernoulli flow** scales by sqrt(2); with ΔP=0, both flow and noise vanish. Closure cannot produce airflow after physical source shutoff.
H2 (gap): keeping pressure, oscillating aperture and noise process fixed, a nonzero residual leak produces finite flow during nominal closed phases while zero-gap null does not.
H3 (closure): a seeded, pressure/flow-conditioned *source-local* noise candidate does not reproduce Exp013's >2 kHz near-total domination downstream. If it does, **REJECT**, do not call it added realism.
H4 (perceptual): distinguishable physical pressures do not establish naturalness or persistent character identity; separate blinded creator audition and artifact notes may reject all conditions.

## Controls/interventions
One actual prepared Core body M0@1 and its exact fixed rest /a/-like geometry, same 100 Hz, same 0.50s schedule and 48000 Hz sampling; existing Core pressure renderer unchanged. Compare modal, breathy_gap (only leak changes), pressure_x2 (only subglottal ΔP changes), noise_off (only stochastic closure α changes). Pressure/geometry/noise are NEVER edited after hearing the result to retroactively rescue thresholds.

## Numeric Gate B (planned execution, fail closed)
1. Source-only tests: zero pressure->zero source; gap closure; sqrt(2) pressure law within 2e-15 rtol; deterministic seed; source-local gated perturbation; reject invalid negative/nonfinite controls. Source-only high-band fraction (< 0.10 above 2 kHz) for every case; check unmodified flow/source RMS separately.
2. Reuse Exp042's exact `_validated_context()` and `_render()`: each proposed condition must yield finite nonzero 24000-sample *new Core physical pressure*. A single gain for all WAVs must preserve pressure ordering; archive NPY raw physical pressure. No unexplained branch fallback.
3. Output pressure band fraction >=2 kHz must remain below 0.20 for each case; this is a **screening threshold**, not calibrated psychophysics, chosen conservatively against Exp013's 0.979 problematic case. Failure is a useful negative research result. Check physical control and noise_on/noise_off produce genuinely different raw pressure when prescribed source differs.
4. Check manifest artifact identities and reproducibility at exact source head and CI; do not claim completion if unexecuted or mismatch.

## Listening Gate C (future, independent)
Use masked order, free voice description before any forced choice, perceptual voice-likeness, roughness/hiss/click and usability as separate fields; one-creator pilot N=1 is not population evidence. A/A exact-WAV negative control via existing Studio #28 / Draft #29 only **after** real Core source candidates and handoff verification. No claims of "character variation" until effects remain coherent across at least two bodies *and* one change of gesture/duration.

## Evidence log
- Before implementation: independent Wolfram calculation for rho=1.2 kg/m³, Cd=0.6, A=20 mm², ΔP=800 Pa and 1 mm width gives Q=0.000438178046 m³/s, pressure doubling ratio=1.41421356237, speed=21.9089 m/s, Re≈1460.59. This checks the equation, **not** the later candidate aperture parameters, turbulence validity, or human voice quality.
- **At freeze:** Gate B Core rendering/CI=NOT_RUN; Gate C listening=NOT_RUN; adoption=HOLD. Record all failed gates and changes here with immutable commit/run links, not revised history.
