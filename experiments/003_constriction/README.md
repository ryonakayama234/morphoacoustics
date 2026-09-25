# 003 — Constriction realization

## Hypothesis

A morphology-independent `CONSTRICT` task should be realized as a body-specific change in tract geometry before acoustics are evaluated.

## Intervention

Apply one active gesture at normalized oral-tract location 0.65 with target area `2e-5 m²` to a 0.17 m, 10-section rest tract.

## Controlled variables

- rest section area: `3e-4 m²`
- gesture interval: 0.0–0.3 s
- evaluation time: 0.1 s
- reachable tongue interval: 0.30–0.80
- acoustic backend: fidelity-0 segmented lossless tube

## Expected result

Exactly the section containing normalized location 0.65 is narrowed to the requested target area. The resulting input impedance differs from the rest tract.

A second intervention moves the same task to location 0.95. Because no articulator reaches that location, realization must return `INFEASIBLE` and acoustics must not run.

## Acceptance criterion

- reachable gesture: `FEASIBLE`, geometry exists, acoustic result exists
- unreachable gesture: `INFEASIBLE`, geometry is absent, acoustic result is absent

Stable forms of these claims are encoded in `tests/test_realization.py` and `tests/scientific/test_vertical_slice.py`.
