# Experiment 022 — Shared-body multi-Gesture interaction (G1-D)

Issue: #51

Baseline: PR #50 head `fa23ce60f1e71e31330d11e512165c360191ad2d`.

## Research question

Can two overlapping task-level `CONSTRICT` Gestures be realized by one shared material-conditioned stateful body in a way that falsifies an independent-state superposition null, while contradictory exact task demands are rejected explicitly before dynamics or acoustics are evaluated?

This experiment adds exactly one layer beyond Experiment 021: **more than one active task constraint on one physical state**.

It does not add general Task Dynamics, anatomical tongue/jaw/lip coordinates, muscles, calibrated biological tissue, FEM/XPBD/FSI, production multi-Gesture APIs, Studio controls, neural components, phoneme identity, or a claim of natural coarticulation.

## Fixed fixture

Inherited unchanged from Experiment 021 unless stated otherwise:

- tract length: 0.170 m
- 10 equal-length sections
- rest area: 3e-4 m²
- baseline reduced material only: all relative stiffnesses = 1
- smoothness lambda: 1
- omega: 25 s^-1
- one shared 10-dimensional normalized area-ratio state `q`
- exact symmetric modal propagation from Experiment 021
- existing segmented-tube acoustic observer
- candidate/reference acoustic grids: 0.05 / 0.01 Hz

Only the second Gesture and temporal overlap are new.

### Gesture A

```text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=5e-5 m²,
    onset=0.00 s,
    offset=0.20 s,
)
```

In this experiment-local reduced fixture it maps to zero-based section 6 and area ratio 1/6.

### Gesture B

```text
CONSTRICT(
    target="oral",
    location=0.45,
    target_area=1e-4 m²,
    onset=0.08 s,
    offset=0.28 s,
)
```

In this experiment-local reduced fixture it maps to zero-based section 4 and area ratio 1/3.

The canonical Gestures contain no section index, Hessian, eigenmode, deformation vector, resonance, or waveform target.

## Timeline

```text
0.00 ───── 0.08 ───────── 0.20 ───── 0.28 ───────── 0.40 s
      A             A+B            B          release
```

The shared candidate changes only its equilibrium target:

```text
0.00–0.08  q*_A
0.08–0.20  q*_{AB}
0.20–0.28  q*_B
0.28–0.40  q0
```

Existing half-open event semantics are retained.

## Reduced material energy and simultaneous constraints

With baseline stiffness `k_i = 1` and the Experiment-019/021 path-Laplacian smoothness term,

```text
H = diag(k) + lambda L
```

and the equilibrium for an active task set is

```text
min_q  1/2 (q-q0)^T H (q-q0)
subject to C q = d
```

using an equality-constrained KKT solve.

Compatible simultaneous constraints are

```text
q_6 = 1/6
q_4 = 1/3
```

and must be solved jointly in one state.

The positivity inequality is not promoted into a general active-set solver. This preregistered fixture is required to stay strictly positive.

## N0 — independent-state superposition null

Gesture A and Gesture B each receive an independent Experiment-021 R3 state:

```text
(q_A, v_A)
(q_B, v_B)
```

Each state sees only its own onset and offset.

The observable null is

```text
q_N0 = q_A + q_B - q0
v_N0 = v_A + v_B
```

and the quasi-static endpoint is

```text
q*_N0 = q*_A + q*_B - q0.
```

This is deliberately not a production model. It is the falsifiable hypothesis that overlapping Gestures can be realized independently and added afterward.

## R4 — one shared physical state candidate

R4 owns only one state:

```text
(q, v)
```

For each constant-target interval it reuses Experiment 021 exactly:

```text
q'' + 2 omega H^(1/2) q' + omega^2 H(q-q*) = 0.
```

For `H = V Lambda V^T`, each mode remains critically damped with

```text
r_i = omega sqrt(lambda_i).
```

No generic ODE integrator is introduced.

When the active task set changes, the target changes but `q` and `qdot` must remain continuous.

## Independent Wolfram preregistration

Before the Python R4 candidate exists:

1. check in `wolfram/shared_body_multigesture_oracle.wl`;
2. evaluate the exact/rational fixture independently in Wolfram Language;
3. freeze `wolfram/shared_body_multigesture_oracle.json`;
4. only then implement the Python null and shared candidate.

The oracle freezes:

- the 10 modal eigenvalues/rates;
- `q*_A`, `q*_B`, `q*_{AB}`, and the independent equilibrium overlay;
- exact task residuals;
- equilibrium nonadditivity metrics;
- shared/null state and velocity at the primary overlap endpoint;
- scalar event diagnostics at 80 / 200 / 280 / 400 ms;
- primary shared/null acoustic resonances;
- compatible and contradictory constraint ranks.

### Preregistered equilibrium discriminator

Independent Wolfram prediction:

```text
||q*_{AB} - q*_N0||_2
≈ 0.183919879344340491

normalized nonadditivity
= ||q*_{AB} - q*_N0|| / ||q*_{AB} - q0||
≈ 0.145918897958551044
```

The shared equilibrium satisfies both exact task constraints. The overlay null does not:

```text
shared residuals = [0, 0]

overlay residuals
≈ [-0.0973782771535580524,
   -0.121602288984263233]
```

### Primary finite-time discriminator

Primary comparison: `t = 0.20 s`, after 120 ms of overlap.

Independent Wolfram prediction:

```text
shared-vs-null state L2
≈ 0.154907113016036674

normalized shared-vs-null state difference
≈ 0.122900663581456112

shared-vs-null velocity L2
≈ 0.612591003014681867
```

At 80 ms, before B has evolved, shared and null states must still agree within numerical tolerance.

### Primary acoustic discriminator

At 200 ms, independent transfer-matrix oracle predicts:

| mode | shared Hz | null Hz | shared-null Hz |
|---|---:|---:|---:|
| 1 | 404.697869521259 | 356.539988903289 | +48.157880617971 |
| 2 | 1699.759879371595 | 1725.016496272597 | -25.256616901002 |
| 3 | 2343.420564954221 | 2236.020320110472 | +107.400244843749 |

## Contradictory positive control

Two individually valid task requests target the same task coordinate with different exact values:

```text
q_6 = 1/6
q_6 = 1/3
```

Independent Wolfram rank test predicts:

```text
rank(C)       = 1
rank([C | d]) = 2
target gap    = 1/6
```

Therefore the simultaneous constraint set is inconsistent.

This case must produce a machine-readable `TASK_CONFLICT` diagnostic and must not call equilibrium dynamics or acoustics for the contradictory pair.

## Preregistered gates

### G1 — Representation isolation

- canonical A/B Gesture serialization is unchanged between null/candidate;
- no body coordinates or solver state appear in the task representation;
- no independent-null state leaks into canonical representation.

Failure: `REPRESENTATION_LEAK`.

### G2 — Request / fixture validity

- A and B are individually supported and FEASIBLE;
- compatible pair has equal constraint and augmented rank;
- all preregistered compatible equilibrium/state ratios are positive;
- event ordering matches the frozen timeline.

Failures:

- `TASK_REQUEST_INVALID`
- `STATE_DOMAIN_VIOLATION`

### G3 — Shared equilibrium oracle

Require:

- max absolute error for `q*_A`, `q*_B`, `q*_{AB}`, and `q*_N0` <= 1e-10;
- max shared compatible task residual <= 1e-12.

Failure: `SHARED_EQUILIBRIUM_ORACLE_MISMATCH`.

### G4 — Independent-overlay null falsification

Require:

- normalized nonadditivity matches Wolfram and > 0.10;
- shared-vs-overlay L2 > 0.10;
- overlay task residual matches the oracle;
- shared solution, not the overlay, satisfies both exact targets.

Failure: `INDEPENDENT_OVERLAY_NULL_NOT_FALSIFIED`.

### G5 — Exact propagation / continuity

Require:

- split vs single exact modal propagation <= 1e-11;
- target switch with dt=0 changes neither q nor qdot by more than 1e-12;
- all states finite;
- at 80 ms shared and null state/velocity agree within 1e-11;
- existing half-open offset semantics are preserved.

Failure: `STATE_PROPAGATION_FAILED`.

### G6 — Shared-body transient interaction

At 200 ms require:

- shared and null q/qdot match frozen Wolfram oracle within 1e-11;
- normalized shared-null state difference > 0.10;
- state L2 > 0.10;
- velocity L2 > 0.5;
- all shared active ratios remain > 0.

Failure: `SHARED_BODY_TRANSIENT_UNRESOLVED`.

### G7 — Contradictory task rejection

Require:

- each conflicting Gesture alone is valid;
- simultaneous consistency check rejects the pair;
- no last-wins, averaging, coercion, dynamic propagation, or acoustic observation occurs;
- experiment diagnostic is exactly `TASK_CONFLICT`.

Failure: `TASK_CONFLICT_NOT_REJECTED`.

### G8 — Acoustic oracle

For the first three 200-ms resonances:

- candidate-grid peak error <= 0.05 Hz;
- reference-grid peak error <= 0.01 Hz;
- shift signs match the Wolfram oracle.

Failure: `ACOUSTIC_ORACLE_MISMATCH`.

### G9 — Acoustic effect above numerical floor

For each mode:

```text
numerical_floor =
max(
    0.05 Hz,
    |candidate_peak - reference_peak|
)

|f_shared - f_null| / numerical_floor > 5
```

Failure: `NUMERICALLY_UNRESOLVED`.

Downstream gates after an upstream failure are `null`, never synthetic PASS.

## Artifacts

- `equilibrium_states.csv`
- `equilibrium_effects.csv`
- `state_trace.csv`
- `event_summary.csv`
- `task_residuals.csv`
- `resonances.csv`
- `acoustic_effects.csv`
- `conflict_case.json`
- `decision.json`

## Decision

All primary gates pass:

```text
SUPPORT_SHARED_BODY_MULTI_GESTURE_INTERACTION
```

A pass supports only:

> In this reduced 10-section fixture, two compatible task-level constrictions acting on one shared material-conditioned stateful body produce a physical trajectory that is distinguishable from independent deformation overlay, with the difference reproduced by an independent Wolfram oracle and downstream acoustics; contradictory exact task demands can also be rejected explicitly before physical/acoustic fallback.

It does not establish natural human coarticulation, biological articulator competition, a general multi-Gesture controller, or a production API.
