# Experiment 004 — Same gesture, two morphologies

## Hypothesis

A morphology-independent task-level gesture should retain the same normalized task description when transferred between bodies, while its physical realization and acoustic consequence may differ.

## Intervention

Apply one `CONSTRICT(location=0.65, target_area=2e-5 m2)` gesture to two explicitly prepared serial 1D morphologies:

- `long-human`: 0.17 m tract,
- `short-human`: 0.12 m tract.

Both bodies expose the same tongue reachability interval and use the same 10-section uniform rest area.

## Controlled variables

Gesture score, target area, articulator reachability, section count, acoustic backend, frequency grid, and sound speed are held fixed. Only prepared tract length and creature identity differ.

## Expected result

The normalized gesture remains `0.65` for both bodies, but the corresponding axial positions differ (`0.1105 m` versus `0.078 m`). Both realizations are feasible and constrict the homologous normalized section, while their acoustic impedance responses differ.

## Backend and parameter provenance

Fidelity 0 serial rigid lossless 1D tract. Geometries are manually constructed uniform tubes and explicitly bound to their `CreatureSpec` objects with preparation provenance.

## Acceptance criterion

The experiment passes if both bodies realize the unchanged gesture, physical axial positions differ as predicted, and the sampled acoustic responses are not numerically identical.
