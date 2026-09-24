# Experiments

This directory is for executable research experiments rather than ad-hoc demos.

Planned sequence:

1. `001_uniform_tube` — validate simple tube resonances against analytic expectations.
2. `002_vary_tract_length` — hold source fixed and vary tract length.
3. `003_constriction` — map a `CONSTRICT` gesture to a time-varying area function.
4. `004_same_gesture_two_morphologies` — execute one gesture score on two bodies.
5. `005_infeasible_gesture` — demonstrate an explicit physical failure.

Each experiment should state:

- hypothesis,
- intervention,
- controlled variables,
- expected qualitative/quantitative result,
- backend and parameter provenance,
- acceptance criterion.

An experiment that becomes a stable invariant should be promoted into `tests/scientific/`.
