# Experiment 019 — Reduced material-conditioned realization (G1-M)

Issue: #40

Depends on Experiment 018 / PR #46.

## Research question

Can the exact same task-level `CONSTRICT` target remain achieved while an
experiment-local material/stiffness intervention changes the **body-specific
physical realization** and downstream acoustics?

This experiment is deliberately narrower than a tissue-mechanics claim. It
tests whether a reduced, falsifiable realization law can distinguish:

- **R0 — hard projector:** the current Fidelity-0 realizer, which changes only
  the selected section and is insensitive to material stiffness;
- **R1 — quasi-static minimum-energy realizer:** an experiment-local candidate
  that distributes deformation according to a dimensionless relative
  stiffness field plus nearest-neighbor smoothness.

No production `CreatureSpec`, Material API, FEM, XPBD, or FSI interface is
introduced.

## Fixed fixture

All conditions use:

- tract length: 0.170 m
- 10 equal-length sections
- rest area: 3e-4 m² in every section
- same `CreatureSpec`
- same articulator reach
- same acoustic model
- same observer windows
- same canonical non-empty Gesture

The canonical Gesture is:

```text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=5e-5 m²,
    onset=0.0 s,
    offset=0.3 s,
)
```

With ten equal sections the target is zero-based section 6.

The Gesture contains no stiffness, material, section index, deformation vector,
formant target, or waveform target.

## R0 — hard-projector null model

The production `Tract1DRealizer` remains unchanged.

Its predicted physical state in normalized area-ratio coordinates is:

```text
[1, 1, 1, 1, 1, 1, 1/6, 1, 1, 1]
```

Changing the experiment-local stiffness profile must not alter R0 because R0
does not consume that profile.

This is a preregistered null prediction, not a defect hidden from evaluation.

## R1 — reduced quasi-static candidate

Let

```text
q_i = realized_area_i / rest_area_i
```

and let `k_i > 0` be an experiment-local dimensionless relative stiffness.

R1 minimizes

```text
E(q) =
    1/2 sum_i k_i (q_i - 1)^2
  + lambda/2 sum_i (q_{i+1} - q_i)^2
```

subject to the exact task constraint

```text
q_6 = target_area / rest_area = 1/6
```

with `lambda = 1`.

The experiment solves the convex equality-constrained quadratic problem through
its KKT linear system using NumPy only.

The positivity inequality is not promoted into a general active-set solver. The
preregistered fixture is required to have a strictly positive unconstrained-KKT
solution. If it does not, the R1 candidate is outside this experiment's domain
rather than evidence of physical infeasibility.

## Single material intervention

Only zero-based section 5 — the left neighbor of the pinned target section —
changes relative stiffness:

```text
baseline:  k_5 = 1
candidate: k_5 = 4
```

Every other `k_i = 1`.

Prepared tract geometry and the canonical Gesture are bitwise/semantically
unchanged. Thus the only intended causal difference inside R1 is the reduced
material profile.

The stiffness values are **dimensionless penalties**. They are not Young's
modulus and are not calibrated tissue properties.

## Independent Wolfram oracle

`wolfram/material_realization_oracle.wl` independently constructs the same
quadratic energy, solves the equality-constrained linear system, and evaluates
the resulting area fields with an independently written lossless
transfer-matrix acoustic calculation.

The checked-in oracle predicts:

- R0 is stiffness-insensitive;
- both R1 conditions achieve `q_6 = 1/6` exactly;
- baseline R1 left-neighbor ratio is approximately `0.6816881259`;
- candidate R1 left-neighbor ratio is approximately `0.8516666667`;
- the pinned target decouples the right sub-chain, so the right-neighbor ratio
  remains unchanged at approximately `0.6794871795`;
- the R1 candidate-vs-baseline state L2 difference is approximately
  `0.183943506`;
- the first three R1 resonance shifts are approximately
  `-2.3928`, `-29.4530`, and `-11.1291 Hz`.

## Observer and numerical floor

Candidate peak grid: 0.05 Hz.

Reference peak grid: 0.01 Hz.

Mode windows:

- mode 1: 350–430 Hz
- mode 2: 1580–1790 Hz
- mode 3: 1980–2260 Hz

For each condition/mode:

```text
numerical_floor_hz =
max(
    0.05 Hz,
    |candidate_peak - reference_peak|
)
```

The R1 baseline-vs-candidate acoustic effect must exceed five times the larger
local floor for every mode.

## Preregistered gates

### G0 — Representation invariance

- the canonical Gesture SHA-256 is unchanged before/after every realization;
- the material profile exists only in the experiment-local R1 candidate;
- no body-specific section index or stiffness value is inserted into Gesture.

Failure: `REPRESENTATION_LEAK`.

### G1 — R0 null prediction

- R0 baseline/candidate physical states are exactly equal;
- R0 state matches the Wolfram hard-projector oracle.

Failure: `BASELINE_NULL_FAILED`.

### G2 — Task preservation

All four R0/R1 conditions are FEASIBLE and the selected section achieves
`5e-5 m²` within the fixture tolerance.

Failure: `TASK_REALIZATION_FAILED`.

### G3 — R1 state oracle

Both R1 normalized area fields must match the independent Wolfram reference
with maximum absolute error <= `1e-10`.

Failure: `MATERIAL_STATE_ORACLE_MISMATCH`.

### G4 — Resolved material-conditioned realization

The R1 candidate-vs-baseline physical-state L2 difference must:

- exceed `1e-3`;
- match the Wolfram L2 prediction within `1e-10`.

Failure: `MATERIAL_EFFECT_UNRESOLVED`.

### G5 — Causal locality

Increasing only left-neighbor stiffness must:

- increase the left-neighbor realized area ratio;
- leave the right-neighbor ratio unchanged within `1e-12`.

This fixture-specific prediction follows from pinning the target section in the
nearest-neighbor quadratic chain.

Failure: `CAUSAL_TRACE_INCONSISTENT`.

### G6 — Acoustic oracle

Candidate/reference resonance measurements must agree with Wolfram within
`0.05 / 0.01 Hz`, respectively.

Failure: `ACOUSTIC_ORACLE_MISMATCH`.

### G7 — Acoustic effect above floor

For all first three modes:

```text
|f_candidate - f_baseline| / numerical_floor > 5
```

and the measured shift sign must match the Wolfram oracle.

Failure: `NUMERICALLY_UNRESOLVED`.

## Decision

### SUPPORT_MATERIAL_CONDITIONED_REALIZATION

A pass supports only:

> In this reduced ten-section Fidelity-0 fixture, one unchanged task target can
> be realized by different quasi-static physical area fields when a single
> dimensionless stiffness parameter changes, and the resulting physical and
> acoustic differences agree with an independent oracle above the measured
> observer floor.

It does **not** establish:

- biological tissue mechanics;
- calibrated Young's modulus;
- nonlinear elasticity;
- FEM/XPBD/FSI validity;
- dynamic task control;
- articulator force production;
- arbitrary morphology transfer;
- phonetic identity;
- perceptual naturalness;
- a production Material API.

A successful result supports taking the next falsification step toward G1-B:
finite-time task dynamics versus quasi-static realization.

## Run

```bash
python experiments/019_material_conditioned_realization/run.py \
  --output-dir experiment-019-output
```

Expected outputs:

- `states.csv`
- `resonances.csv`
- `effects.csv`
- `decision.json`
