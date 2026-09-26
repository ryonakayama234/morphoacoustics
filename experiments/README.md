# Experiments

This directory is for executable research experiments rather than ad-hoc demos.

Current sequence:

1. `001_uniform_tube` — validate simple tube resonances against analytic expectations.
2. `002_vary_tract_length` — hold source fixed and vary tract length.
3. `003_constriction` — map a `CONSTRICT` gesture to a prepared 1D tract state.
4. `004_same_gesture_two_morphologies` — execute one unchanged gesture score on two explicitly prepared bodies and compare physical/acoustic outcomes.
5. `005_infeasible_gesture` — demonstrate that the same valid gesture can be feasible for one body and physically infeasible for another.

Each experiment should state:

- hypothesis,
- intervention,
- controlled variables,
- expected qualitative/quantitative result,
- backend and parameter provenance,
- acceptance criterion.

An experiment that becomes a stable invariant should be promoted into `tests/scientific/`.
