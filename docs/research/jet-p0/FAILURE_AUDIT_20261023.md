# JET-P0 post-run failure audit — 2026-10-23

**Retrospective, written AFTER execution; NOT a changed preregistration.** Exact source HEAD `9a79fa616e280de24daab5bfbe3cce57fda92256`, PR [#167](https://github.com/ryonakayama234/morphoacoustics/pull/167), actual source-HEAD CI [39951204385](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39951204385): **FAIL**. Seven source-unit tests PASS and genuine Core static M0 pressure generation PASS, then frozen high-band acoustic gate FAIL. Listening NOT RUN, adoption HOLD.

## Immutable evidence
- CI uploaded [research artifact 12499763960](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39951204385/artifacts/12499763960). Downloaded ZIP SHA256: `e407612b7706d761e4161633156fa69f3f1c7fe92c18738cd979e91cdbdc259b`; all 4 × 3 manifest checksums (source NPY, raw pressure NPY, WAV) independently verified.
- Source code's `manifest.source_head` is still literal `MUST_FILL_FROM_GITHUB_CI_OR_LOCAL_GIT_HEAD`: **do not** treat this as source provenance. Real trust comes from the GitHub run's recorded HEAD and ZIP digest.
- Raw pressure is from genuine inherited SV-1 static Core renderer, **not** an arbitrary postprocessor. Shared playback-gain `6.360063516949838` is downstream-only and does not affect raw-Pa diagnostics.

| Case | Source fraction ≥2kHz | Core raw-Pa fraction ≥2kHz | Pa RMS | Gate < 0.20 |
|---|---:|---:|---:|---|
| noise_off | 3.88252287258e-8 | 0.000524032305 | 0.00337243908 | PASS |
| modal | 1.28008406343e-5 | 0.807575557500 | 0.00784178440 | **FAIL** |
| breathy_gap | 1.12117358757e-5 | 0.861492063183 | 0.00934310573 | **FAIL** |
| pressure_x2 | 4.22735496641e-5 | 0.936400104215 | 0.01977825416 | **FAIL** |

Fraction is squared FFT magnitude above 2kHz / all bins, under existing experiment definition. No perceptual interpretation of fractions is assumed.

## Post-hoc differential investigation — diagnostic, NOT a new prospective gate
Using original downloaded floating point NPYs only, for the identical body/pressure/aperture/seed modal minus noise_off pair:
- stochastic added `source RMS = 6.39509484022e-8 m³/s`; total modal source RMS `1.02561353521e-5 m³/s`; added source RMS ≈ **0.624%** of the total.
- `(raw pressure modal - raw pressure noise_off)` RMS = `0.00708141020190 Pa`. The `noise_off` raw pressure RMS was `0.00337243908237 Pa`; output residual RMS **2.10×** baseline. Residual pressure highband fraction **0.990118**.
- These differences do not independently establish a separately rendered noise-only physical signal if any stage is nonlinear. They motivate an explicit fixed-geometry superposition check. They are not proof that the numerical solver is incorrect or that all turbulence closures are unphysical.
- Candidate cause: source-port noise + frequency-dependent tract/outlet radiation response (as suspected in [Core #30](https://github.com/ryonakayama234/morphoacoustics/issues/30)). Exact causal attribution of port, termination, radiation derivative, source spectral placement, and frame windowing **UNRESOLVED**.

## Explicit decision
- JET-P0's declared Gate B: **REJECTED** for 3/4 conditions. Never change original 0.20 bound or hide artifact to claim PASS.
- Formula tests and physical-solver execution: technical progress only.
- **Selected next investigation:** [SA-1 Core #168](https://github.com/ryonakayama234/morphoacoustics/issues/168), separating physical source ↔ acoustic-port transfer and receptor radiation, with independent oracle and rerun.
- **Stage C Voice Atlas:** no creator listening has been conducted. Existing [Studio Draft #29](https://github.com/ryonakayama234/morphoacoustics-studio/pull/29) is limited to adopted CC-A2 bodies and must not silently ingest research-only WAVs.
