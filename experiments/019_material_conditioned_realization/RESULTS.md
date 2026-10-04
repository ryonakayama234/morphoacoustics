# Experiment 019 results

## Decision

**SUPPORT_MATERIAL_CONDITIONED_REALIZATION**

for the narrow G1-M claim:

> In this reduced ten-section Fidelity-0 fixture, one unchanged task target can
> be realized by different quasi-static physical area fields when a single
> dimensionless stiffness parameter changes, and the resulting physical and
> acoustic differences agree with an independent Wolfram oracle above the
> measured observer floor.

This is not evidence for calibrated biological tissue mechanics or a production
Material API.

## CI execution

GitHub Actions `experiment-019` completed successfully on:

- Python 3.11.16
- NumPy 2.4.6

Objective run: `37192957162`.

## Representation and R0 null

The canonical Gesture SHA-256 remained:

```text
9db776aab46c8e51592063310de78b75eb19d252012cc079f552978dcc4200bb
```

The production R0 hard-projector baseline/candidate states were exactly equal.
The selected target section remained at area ratio `1/6`; every other section
remained at `1`.

Thus the experiment-local stiffness intervention does not leak into the
canonical Gesture or into the R0 null model.

## Task preservation

All four R0/R1 realizations were FEASIBLE.

Target-area residuals were:

| condition | absolute residual |
|---|---:|
| R0 baseline | 0 |
| R0 candidate | 0 |
| R1 baseline | 6.78e-21 m² |
| R1 candidate | 2.71e-20 m² |

All are below the preregistered `1e-18 m²` fixture tolerance.

## R1 physical realization

Independent Wolfram and NumPy KKT solutions agreed to floating-point precision:

- baseline max absolute state error: `1.11e-16`
- candidate max absolute state error: `1.11e-16`

The stiffness intervention changed the left-neighbor area ratio by:

```text
+0.16997854077253216
```

while the right-neighbor difference was:

```text
-1.11e-16
```

consistent with the preregistered pinned-target locality prediction.

The candidate-vs-baseline R1 state effect was:

```text
measured L2 = 0.18394350598751427
Wolfram  L2 = 0.18394350598751433
```

## Acoustic oracle

Candidate 0.05-Hz-grid peaks and 0.01-Hz reference peaks both matched the
independent Wolfram transfer-matrix roots within their preregistered tolerances.

Maximum errors across R0/R1 conditions and the first three modes:

- candidate-grid error: `0.0227301 Hz` (< `0.05 Hz`)
- reference-grid error: `0.00282688 Hz` (< `0.01 Hz`)

## Material-conditioned acoustic effect

R1 baseline-to-candidate results:

| mode | observed shift | Wolfram shift | effect / floor |
|---|---:|---:|---:|
| 1 | -2.35 Hz | -2.39282 Hz | 47× |
| 2 | -29.45 Hz | -29.45296 Hz | 589× |
| 3 | -11.15 Hz | -11.12907 Hz | 223× |

Every mode has the predicted sign and exceeds the preregistered `5×` numerical
discrimination margin.

## Interpretation

Experiment 019 falsifies the idea that the only useful realization law at this
stage must be an instantaneous one-section hard projection. A reduced
quasi-static model can preserve the exact same task while producing a
material-conditioned deformation field and downstream acoustic response.

The result does **not** establish that this quadratic energy is anatomically
correct. It establishes that the model class is:

- task-preserving in this fixture;
- morphology/material-sensitive;
- independently reproducible;
- numerically resolved;
- compatible with the project's causal representation boundary.

## Claim boundary

Still unsupported:

- calibrated Young's modulus or tissue parameters;
- nonlinear or viscoelastic tissue behavior;
- FEM / XPBD / FSI validity;
- finite-time task dynamics;
- muscle or force-level actuation;
- arbitrary creature transfer;
- phonetic identity;
- perceptual naturalness;
- promotion of `ReducedMaterialProfile` into the production domain model.

## Next falsification layer

Proceed to G1-B only as a separate experiment:

```text
R1 quasi-static
    vs
R2 finite-time task dynamics
```

using Gesture duration / settling behavior to create predictions that R1 and R2
cannot both satisfy.
