# Experiment 017 — Embodied infeasibility boundary (E1-B)

Issue: #40

Depends on Experiment 016 / PR #42.

## Research question

Can the simulator preserve one unchanged, valid, supported task request while a
single morphology capability axis crosses its reachability boundary, producing:

- a normal physical/acoustic realization when the task is reachable, and
- explicit `INFEASIBLE` with no physical state and no acoustic evaluation
  when the task is unreachable?

This experiment treats **reachable task set** as an Embodiment observable.

## Canonical task

Exactly one immutable task-level score is reused in every condition:

```text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=2e-4 m²,
    onset=0.0 s,
    offset=0.3 s,
)
```

The score contains no body-specific reach endpoint, axial coordinate, section
index, acoustic target, or fallback target.

## Fixed body / backend properties

All conditions use:

- tract length: 0.170 m
- 10 equal sections
- rest area: 3e-4 m²
- same cavity
- same tongue articulator identity/kind/cavity
- reachable_start = 0.30
- same prepared 1D geometry
- same Fidelity-0 realizer
- same segmented-tube acoustic backend
- same acoustic probe request

Only `ArticulatorSpec.reachable_end` changes.

## Preregistered reach conditions

| label | reachable_end | normalized margin `reachable_end - 0.65` | metric margin at L=0.17 m | expected |
|---|---:|---:|---:|---|
| M_plus | 0.70 | +0.05 | +8.5 mm | FEASIBLE |
| M_boundary | 0.65 | 0.00 | 0.0 mm | FEASIBLE |
| M_minus | 0.60 | -0.05 | -8.5 mm | INFEASIBLE |

The boundary is deliberately included because the current domain rule is
inclusive:

```text
reachable_start <= location <= reachable_end
```

Therefore exact contact with the reach endpoint must remain FEASIBLE.

## Independent Wolfram oracle

`wolfram/reach_boundary_oracle.json` records the independently calculated
normalized and metric reach margins and the expected status sign rule:

```text
margin >= 0  -> FEASIBLE
margin < 0   -> INFEASIBLE
```

The oracle does not call the Python realizer.

## What is primary in E1-B

The primary observable is not resonance shift. It is the causal feasibility
classification:

```text
same valid task
    +
same supported backend
    +
only reachable_end changes
        ↓
M_plus      -> FEASIBLE
M_boundary  -> FEASIBLE
M_minus     -> INFEASIBLE
```

The impossible condition must not be silently coerced into a nearby reachable
task.

## Acoustic negative control

M_plus and M_boundary differ in latent reach capacity, but both can realize the
same task at location 0.65. Their prepared acoustic geometry and realized
constriction are therefore expected to be exactly equal.

The experiment requires:

- realized physical states equal;
- acoustic backend called exactly once for each feasible condition;
- acoustic probe arrays exactly equal.

This demonstrates that a morphology capability change need not change sound
while the requested task remains inside both reachable sets.

## No-fallback gate

M_minus must satisfy all of:

- status = `INFEASIBLE`;
- issue code = `LOCATION_UNREACHABLE`;
- issue gesture index = 0;
- physical state is `None`;
- acoustic result is `None`;
- wrapped acoustic backend call count = 0.

The call-count check ensures the system did not compute acoustics and merely
discard the result afterward.

## Representation and intervention isolation

The canonical score SHA-256 must be identical before and after all three
conditions.

The three body specs must be identical except for
`articulator.reachable_end`. Prepared tract geometry must be exactly equal.

Any body-specific rewrite of `location=0.65` or `target_area=2e-4 m²` is
`REPRESENTATION_LEAK`, not Embodiment evidence.

## Decision

### SUPPORT_EMBODIED_INFEASIBILITY

Requires all of:

1. canonical score hash is unchanged across the complete experiment;
2. the body intervention is isolated to `reachable_end`;
3. prepared tract geometry is identical across all conditions;
4. Wolfram reach margins match the Python fixture values within `1e-15`;
5. M_plus is `FEASIBLE`;
6. M_boundary is `FEASIBLE`;
7. M_minus is `INFEASIBLE`;
8. neither valid fixture condition is `INVALID` or `UNSUPPORTED`;
9. M_minus reports only `LOCATION_UNREACHABLE` for gesture index 0;
10. M_minus has no physical state;
11. M_minus has no acoustic result;
12. M_minus acoustic backend call count is zero;
13. M_plus and M_boundary realized states are exactly equal;
14. M_plus and M_boundary acoustic probe arrays are exactly equal;
15. feasible conditions retain the exact requested target area and selected
    section implied by location 0.65.

## Failure classifications

Ordered diagnostic classes:

- `REPRESENTATION_LEAK`
- `CAUSAL_TRACE_INCONSISTENT`
- `INVALID_REQUEST_REGRESSION`
- `BACKEND_UNSUPPORTED`
- `TASK_REALIZATION_FAILED`
- `FEASIBILITY_BOUNDARY_FAILED`
- `FAILURE_ATTRIBUTION_INCONSISTENT`
- `ACOUSTIC_FALLBACK_LEAK`
- `CAPABILITY_NULL_CONTROL_FAILED`

A negative-body `INFEASIBLE` result is **not** a failure. It is the expected
positive Embodiment result.

## Claim boundary

A pass supports only:

> For the Fidelity-0 CONSTRICT fixture, changing one articulator reach endpoint
> while keeping the valid task and acoustic geometry fixed changes the reachable
> task set at the preregistered boundary; an unreachable task is represented as
> explicit physical infeasibility and does not proceed into acoustic synthesis.

It does not establish:

- biological reachability realism;
- arbitrary morphology constraints;
- force/strength limitations;
- deformable tissue collision constraints;
- perception or naturalness;
- source/filter coupling;
- arbitrary creature capability modeling.

## Run

```bash
python experiments/017_embodied_infeasibility_boundary/run.py \
  --output-dir experiment-017-output
```
