# Experiment 005 — Morphology-dependent infeasible gesture

## Hypothesis

The same valid task-level gesture can be physically realizable for one morphology and infeasible for another. `INFEASIBLE` should therefore encode evidence about the body, not an acoustic-backend failure or an invalid request.

## Intervention

Apply one `CONSTRICT(location=0.70, target_area=2e-5 m2)` gesture to two 0.17 m prepared morphologies that differ only in articulator reachability:

- `capable-body`: tongue reach `0.30–0.80`,
- `limited-body`: tongue reach `0.30–0.55`.

## Controlled variables

Prepared tract geometry, gesture score, target area, acoustic backend, frequency request, and all non-reachability morphology fields are held fixed.

## Expected result

`capable-body` returns `FEASIBLE` and proceeds to acoustics. `limited-body` returns `INFEASIBLE` with `LOCATION_UNREACHABLE`, contains no realized state, and stops before acoustic evaluation.

## Backend and parameter provenance

Fidelity 0 serial rigid lossless 1D tract. The same manually prepared geometry is independently bound to each `CreatureSpec`.

## Acceptance criterion

The experiment passes if changing only articulator reachability changes the outcome from `FEASIBLE` to `INFEASIBLE`, and acoustics are absent for the infeasible body.
