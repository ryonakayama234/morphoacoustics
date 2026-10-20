---
id: EL-G0A-PREREG
status: PREREGISTERED_BEFORE_REAL_DATA_EXECUTION
adoption: NOT_ADOPTED
scope: experiment_only
---
# EL-G0a pre-registered test

## Hypothesis / null

H: In the same scene, the artificial head + pinna transfer response (B) changes the left/right spectral and phase signature compared with an ideal free-field pair of pressure points (A). With headphones, subjective **externalization**, laterality, proximity and naturalness may differ, but B is **not assumed superior**.

Null: the listener hears no reliable difference or prefers A, or dataset metadata/calibration prevents a valid comparison. Interpret differences as stimulus-specific; do not infer population-level ASMR outcomes.

## Frozen fixture

- Parent experiment 040 analytic fixture/oracle remains unchanged; 9 tests must pass.
- Separate G0a fixture: same deterministic bandlimited volumetric flow trace `Q(t)` at 48 kHz, center ±30° near 30 cm and horizontal within ±10° as recorded in the *source data* (no invented sample directions).
- A: free-field `rho/(4πr)*Qdot(t-r/c)`, default rho=1.2kg/m³, c=343m/s.
- B: SOFA measured `NF_LIB_HRTF_measured.sofa` with SHA-256 recorded and Zenodo MD5 checked `4ba9cc348801a6805265c7168b5b3227`, sampled transfer response to Qdot. No 1/r double-addition.
- WAV 48 kHz, 24bit PCM; six A/B recordings, browser A/B UI with blind mode and note export.
- Explicit shared playback gain and B-wide RMS matching (not physical calibration). Listener position metadata and SOFA convention must be available or failure raised.

## Pre-registered numeric/completion gates

1. Existing 9 Experiment 040 automated tests pass unchanged.
2. New unit tests cover SOFA coordinate conversion, source position selection without extrapolation, invalid units/NaN, FIR and TF handling, independent convolution, delay sign and mirror null, 6-WAV synthetic fixture pipeline, overwrite refusal.
3. At the *real dataset* gate: Zenodo MD5 matches, three distinct measured source positions selected, both channels finite, no failed samplerate transformation; six 48kHz PCM clips written; hashes, metadata and gain written; source identity fixed between A/B.
4. A's point probe analytic time/level sign matches Experiment 040 mirror case (ITD offset -0.255867393 ms, R/L +3.130726878 dB under its exact original fixture). New source directions need not match those original positions.
5. B conversion preserves SOFA complex phase (frequency-domain HRTF) and declared `Data.Delay` without arbitrary minimum-phase replacement. No ear-canal/propagation double application.
6. Playback amplitudes are finite, clipped peaks < 0.71FS, channel ordering audited, separate ears not individually normalized.
7. UI provides position selection, A/B listening, hidden identity, reveal, note export and local-only playback. Browser/listening human gate remains explicitly **PENDING** until manually confirmed.
8. Independent physics/phase/units/data-provenance review must occur before research gate promotion. An implementer-only review is not independent.

## Failure/interpretation

- Dataset unsuitable/unknown coordinate/frequency convention -> UNSUPPORTED, no ersatz anatomical rendering.
- Malformed data / nonfinite values -> INVALID with error, no silent completion.
- Successful CI is `IMPLEMENTATION_NUMERICALLY_CHECKED`, **not** subjective externalization validation, not a promotion of PR #83 G1/G2 or production adoption.
- Without actual listener report, the creator experience is a *testable affordance*, not a verified user outcome.

Sources: [EL-H01](../embodied-listener/10-listener-morphology.md), [EL-H02](../embodied-listener/20-near-field-propagation.md), [research gates](../embodied-listener/70-research-gates.md), [Marschall dataset](https://zenodo.org/records/7316545).
