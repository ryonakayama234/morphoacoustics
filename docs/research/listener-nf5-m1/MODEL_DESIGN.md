# MODEL_DESIGN — causal hypotheses and computational degrees of freedom
**Design, not measured algorithm validation.** Core source body, biomechanical ear and impedance coupling out of scope.
## Baselines and candidates
- B0: closest training original 3D Cartesian source location; original-index tie; measured bilateral relative HRIR with an explicitly declared radial validity/refusal. Mandatory, even if B3 was historically stronger on development.
- B1: inverse-distance-weighted local training bilateral original IR; fix distance epsilon and neighbor cardinality in prospective operational amendment. No unbounded extrapolation.
- B2: valid geometry-only in-hull barycentric/local field, declared coverage. An invalid simplex is a refusal, not perfect prediction.
- B3: direction/radius-regularized spherical harmonic baseline, order/ridge/cross-shell policy selection-only.
- F1: time-separated aligned HRIR estimation: estimate per-ear arrival by frozen estimator, remove arrival, spatially predict residual waveforms including phase, restore arrival. No truth-cue leakage.
- F2: F1 + common log spectral magnitude m and interaural difference ell with **distinct** preregularized spatial models. Use frozen train-only residual-phase reconstruction; not ILD-only audio.
- F3: F2 with additional ear spectral-detail/residual-phase spatial predictor and coherence/causality checks. More complexity only if it improves independent selection.
## Falsifiable structural observation
If T is the **same linear interpolation operator** on all spectral variables, then `T(m)+T(ell)/2=T(log|H_L|)` and similarly R. Thus merely using m/ell coordinates cannot by itself improve linear independent-ear interpolation. F2 hypothesis requires *different constraints / loss / spatial scales or frequency-aware penalties* on m vs ell; validate with equivalence-negative control. Do NOT claim an algebraic change is a scientific improvement.
## Complex bilateral reconstruction
`m=0.5(log|HL|+log|HR|)`; `ell=log|HL|-log|HR|`;
`tau_c=0.5(tau_L+tau_R)`; `delta=tau_R-tau_L` (right later positive).
`Hhat_e(f)=exp(mhat+s_e*ellhat/2) * exp(-j*2*pi*f*tauhat_e) * exp(+j*phi_res_e(f))`, `s_L=+1`, `s_R=-1`, `tauhat_L=tauhat_c-delta/2`, `tauhat_R=tauhat_c+delta/2`.
Train-only magnitude-floor mask; Hermitian conjugacy / DC and Nyquist real; finite real inverse FFT and declared origin. Do not force minimum phase or discard residual phase; no arbitrary earwise normalization. FFT zero padding may estimate spectra more smoothly but adds no measurement bandwidth. Guard pre-window leakage relative to fixed measured FIR origin; do NOT claim physical causality from finite-window numerical tests.
## Geometry selection
Frozen prior to final: direct SOFA listener-local az+el and distance in metres; use unit vectors and log-radius. Local methods must reject out-of-hull/excess gaps rather than silently give constant-output extrapolation. B3 regularization and any frequency crossover selected only on selection data, not on NF4 opened final. No assumed universal 2kHz crossover.
## Support and calibration
Risk/abstention is an independent module tied to **exact predictor hash and head/geometry/processing regime**, trained on disjoint calibration only. Report both conditional accuracy and coverage (all eligible final denominator); zero coverage -> INDETERMINATE. Refusal reasons include bad units/plane, unseen head, shell outside domain, insufficient local directions, uncertain risk, invalid phase/time, numeric failure.
## Neural decision
No neural training in M1 or initial NF5 candidate grid. Fixed interpretable DSP and regularized local/SH methods are the first diagnostic, because NF4 model complexity degraded final accuracy and nearest-neighbor B0 posthoc was strongest. Neural branch would require a new preregistered counter-hypothesis and new independent blind evidence.
