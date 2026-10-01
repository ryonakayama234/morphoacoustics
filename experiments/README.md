# Experiments

This directory is for executable research experiments rather than ad-hoc demos.

Current sequence:

1. `001_uniform_tube` — validate simple tube resonances against analytic expectations.
2. `002_vary_tract_length` — hold source fixed and vary tract length.
3. `003_constriction` — map a `CONSTRICT` gesture to a prepared 1D tract state.
4. `004_same_gesture_two_morphologies` — execute one unchanged gesture score on two explicitly prepared bodies and compare physical/acoustic outcomes.
5. `005_infeasible_gesture` — demonstrate that the same valid gesture can be feasible for one body and physically infeasible for another.
6. `006_gesture_timecourse` — compare binary and smooth temporal activation above the existing snapshot primitive before promoting any temporal API into the core package.
7. `007_gesture_sampling_convergence` — test convergence and expose the need for explicit event semantics at discontinuities.
8. `008_event_trajectory` — compare sampled-only timing with explicit events plus sampled continuous trajectories and record the adoption decision.
9. `009_fixed_tract_waveform` — excite fixed prepared tracts with an explicit source and generate the first raw/listening waveforms with independent resonance checks.
10. `010_dynamic_gesture_waveform` — propagate one validated Gesture timecourse through quasi-stationary physical/acoustic rendering and separate motion effects from morphology effects.
11. `011_gesture_coordination_overlap` — compare sequential and overlapping execution of two spatially distinct Gestures before promoting any general coordination or coarticulation API.

Each experiment should state:

- hypothesis,
- intervention,
- controlled variables,
- expected qualitative/quantitative result,
- backend and parameter provenance,
- acceptance criterion.

An experiment that becomes a stable invariant should be promoted into `tests/scientific/`.
