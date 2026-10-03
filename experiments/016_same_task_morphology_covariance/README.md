# Experiment 016 — Same-task morphology covariance (E1-A)

Issue: #40

Depends on Experiment 015 / PR #41.

## Research question

Can one unchanged, non-empty task-level `GestureScore` be realized on two
feasible prepared morphologies so that:

1. the task representation remains identical,
2. the physical realization moves into body-specific coordinates,
3. morphology and Gesture both create acoustic effects above the calibrated
   observer floor, and
4. the resulting acoustics obey the scale covariance predicted by this
   deliberately self-similar fixture?

This is the first E1-A test of task-preserving morphology transfer. It is still
restricted to the Fidelity-0 prepared-geometry axis; it is not yet a claim about
arbitrary `CreatureSpec` anatomy.

## Preregistered fixture

The same `CreatureSpec`, articulator reachability, serial topology, section
count, rest area, backend, boundary condition, and observer are used in both
prepared morphologies.

Only total prepared tract length changes:

| morphology | total length |
|---|---:|
| M0 | 0.170 m |
| M1 | 0.187 m |

Thus

```text
M1 / M0 length scale = 1.1
expected frequency scale = 1 / 1.1 = 0.909090909...
```

Each tract has 10 equal sections with rest area `3e-4 m²`.

## Canonical non-empty task

Exactly one immutable score is constructed and reused for both bodies:

```text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=2e-4 m²,
    onset=0.0 s,
    offset=0.3 s,
)
```

The moderate target area is deliberate. Experiment 004 used `2e-5 m²`, which
creates much stronger mode motion. E1-A uses a smaller intervention so the first
three resonance identities remain unambiguous across all four factorial
conditions.

No body-specific axial coordinate, section index, resonance target, formant
target, waveform target, or solver node is present in the canonical Gesture.

## 2 × 2 design

| | Rest | Same non-empty Gesture |
|---|---|---|
| M0 | M0-rest | M0-G |
| M1 | M1-rest | M1-G |

This separates:

- the morphology main effect,
- the Gesture main effect,
- the physical realization of the same task,
- and the scale-covariance invariant.

## Independent Wolfram oracle

`wolfram/scale_covariance_oracle.json` is generated from an independent
transfer-matrix calculation in Wolfram Language.

For a serial lossless tube section,

```text
T_i =
[ cos(k l_i)              j Z_i sin(k l_i) ]
[ j sin(k l_i) / Z_i      cos(k l_i)       ]
```

with `Z_i = rho c / A_i`. The pressure-release resonance condition is obtained
from the composed matrix denominator.

The oracle is not called by the Python simulator. It is checked in as an
external expected-value record.

## Primary acoustic observables

The first three input-impedance resonance frequencies are extracted in fixed
windows:

- mode 1: 400–550 Hz
- mode 2: 1300–1650 Hz
- mode 3: 2150–2600 Hz

The candidate observer grid is 0.05 Hz. A 0.01 Hz observer is used as a local
reference perturbation.

For each condition and mode,

```text
numerical_floor =
max(
    0.05 Hz,
    |candidate_peak - reference_peak|
)
```

Section count is **not** used as a numerical perturbation in E1-A. At this
fidelity, one CONSTRICT task changes one entire selected section; changing the
section count therefore changes the physical width of the realized task and is
a model intervention rather than a pure numerical refinement.

## Task-realization residuals

For M0-G and M1-G, the evaluator records:

- feasibility status,
- canonical score SHA-256,
- selected section index,
- modified section indices,
- realized target-area residual,
- normalized center of the modified section,
- normalized location residual,
- physical axial center,
- constricted section physical length.

With 10 equal sections and `location=0.65`, the expected modified section is
index 6 (zero-based), whose normalized center is exactly 0.65.

The physical centers are predicted to differ:

```text
M0: 0.65 × 0.170 = 0.1105 m
M1: 0.65 × 0.187 = 0.12155 m
```

and both the axial center and section length should scale by 1.1.

## Acoustic effects must be resolved

Two effect families must each exceed five times their local numerical floor.

### Morphology effect

For both Rest and Gesture conditions,

```text
|f(M1, condition) - f(M0, condition)| / floor > 5
```

### Gesture effect

For both bodies,

```text
|f(M, Gesture) - f(M, Rest)| / floor > 5
```

The 5× value is an engineering discrimination margin, not a perceptual
threshold.

## Scale covariance

Because M1 is an exact uniform 1.1× axial scaling of M0 and the same normalized
section receives the same area intervention, both Rest and Gesture conditions
should satisfy

```text
f(M1, c) = f(M0, c) / 1.1.
```

For each mode and condition,

```text
scale_residual_hz =
|f(M1,c) - f(M0,c)/1.1|
```

must be no larger than the conservative observer uncertainty budget

```text
floor(M1,c) + floor(M0,c)/1.1.
```

## Dimensionless task-transfer invariant

Absolute Gesture-induced shifts in Hz scale with body length, so raw
difference-in-differences is not the primary transfer metric.

Instead define, for each mode,

```text
g(M) = log( f(M, Gesture) / f(M, Rest) )
```

and

```text
D = |g(M1) - g(M0)|.
```

For this self-similar fixture the Wolfram oracle predicts `D = 0`.

The measured `D` must lie inside a conservative log-frequency uncertainty
budget obtained by summing the four per-frequency log uncertainty bounds
associated with the declared numerical floors.

This is the central E1-A invariant:

> absolute acoustics change with the body, while the dimensionless effect of
> the unchanged task is preserved.

## Gates

### SUPPORT_TASK_MORPHOLOGY_COVARIANCE

Requires all of:

1. the canonical non-empty score hash is unchanged before/after evaluation;
2. exactly the same score hash is used for M0-G and M1-G;
3. all four conditions are `FEASIBLE`;
4. target area residual <= `1e-15 m²`;
5. normalized task-location residual <= `1e-12`;
6. only the expected section is modified in both Gesture conditions;
7. M1/M0 physical axial-center and section-length scale = 1.1 within `1e-12`;
8. candidate peaks match the Wolfram oracle within 0.05 Hz;
9. reference peaks match the Wolfram oracle within 0.01 Hz;
10. every morphology effect exceeds 5× its local floor;
11. every Gesture effect exceeds 5× its local floor;
12. Rest and Gesture cross-body resonance scaling fit the 1/1.1 prediction
    within the declared observer budgets;
13. the cross-body difference in dimensionless log Gesture effect lies inside
    the declared log uncertainty budget.

### Failure classifications

Ordered classification:

- `MEASUREMENT_REGRESSION` — oracle/observer checks fail;
- `REPRESENTATION_LEAK` — the canonical score changes or differs by body;
- `TASK_REALIZATION_FAILED` — expected-feasible task fails or task residuals
  exceed tolerance;
- `PHYSICAL_REALIZATION_INCONSISTENT` — body-specific coordinates do not
  scale as preregistered;
- `MORPHOLOGY_EFFECT_UNRESOLVED` — morphology or Gesture effects do not
  separate from the observer floor;
- `SCALE_COVARIANCE_FAILED` — absolute acoustic scaling breaks;
- `TASK_TRANSFER_FAILED` — dimensionless Gesture effect is not preserved.

## Claim boundary

A pass supports only:

> In the specified self-similar Fidelity-0 prepared-morphology fixture, one
> unchanged non-empty CONSTRICT task transfers across a 10% tract-length
> intervention, is realized in morphology-specific physical coordinates, and
> preserves the preregistered dimensionless acoustic task effect.

It does not establish:

- arbitrary morphology transfer,
- nonlinear tissue/material effects,
- human vowel identity,
- perceptual equivalence,
- source-filter coupling,
- muscle or actuator realism,
- higher-fidelity FSI.

## Run

```bash
python experiments/016_same_task_morphology_covariance/run.py \
  --output-dir experiment-016-output
```
