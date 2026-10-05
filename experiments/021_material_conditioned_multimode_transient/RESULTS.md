# Experiment 021 results

## Decision

**SUPPORT_MATERIAL_CONDITIONED_MULTIMODE_TRANSIENT**

for the narrow G1-C claim:

> In this 10-section reduced fixture, while preserving the same task intent and the same Experiment-019 material-specific equilibrium concept, a scalar finite-time path can be falsified by a multi-mode physical trajectory, and the reduced material intervention predictably changes both normalized transient realization and downstream acoustics.

This does not establish biological tongue dynamics, calibrated tissue mechanics, human speech motor control, or correct multi-Gesture competition.

## Objective execution

GitHub Actions `experiment-021` completed successfully on run:

- run ID: `37257109920`
- Python: 3.11.16
- NumPy: 2.4.6

The repository test workflow also passed:

- typecheck: success
- Python 3.11 tests: success
- Python 3.12 tests: success
- Python 3.13 tests: success

A preceding implementation run reached the scientific outputs but failed only while serializing a NumPy boolean into `decision.json`. The serializer was corrected and the objective run above completed with all gates passing.

## Representation and request validity

The timing-independent task-intent SHA-256 remained:

```text
6b2aeb5e728064923c80d66998d52c9effea6cc6f89d117b0c7634de4b9c441c
```

Full score hashes differed only because Gesture duration/offset is the intended intervention.

Every duration-specific CONSTRICT request remained FEASIBLE under the production Fidelity-0 validator and resolved to zero-based section 6.

No Hessian, eigenvector, modal state, section velocity, area vector, resonance target, or waveform target was added to Gesture.

## Material-specific equilibrium regression

Both reduced material equilibria matched the independent Wolfram oracle.

Maximum state absolute error:

```text
1.1102230246251565e-16
```

This is below the preregistered `1e-10` equilibrium regression threshold.

The R2 and R3 comparison therefore uses the same material-specific equilibrium endpoint within each material condition.

## Modal oracle

The Python candidate constructs the symmetric Hessian and uses `numpy.linalg.eigh` followed by the exact critically damped modal state transition.

Maximum error over preregistered eigenvalues, modal rates, primary R3 q/qdot state, and duration observables:

```text
1.7763568394002505e-14
```

This is below the preregistered `1e-11` modal-oracle threshold.

No generic ODE integrator is used.

## Exact propagation and event continuity

Maximum split-vs-single propagation discrepancy:

```text
1.9539925233402755e-14
```

against a preregistered threshold of `1e-11`.

Maximum state jump under an onset/offset target switch with `dt=0`:

```text
3.552713678800501e-15
```

against a preregistered threshold of `1e-12`.

The exact offset sample is treated as released under the half-open active interval convention.

## Primary 120-ms physical comparison

Measured values:

| material | model | path progress | d_perp | normalized equilibrium error |
|---|---|---:|---:|---:|
| baseline | R2 | 0.8008517265285442 | 8.29e-17 | 0.1991482734714558 |
| baseline | R3 | 0.8630956417552400 | 0.06427279262109425 | 0.15124085155051106 |
| stiff | R2 | 0.8008517265285441 | 1.64e-16 | 0.19914827347145583 |
| stiff | R3 | 0.9014542854467807 | 0.05523944357653906 | 0.11297191679107763 |

The R2 scalar-path null remains numerically zero within the `1e-12` threshold.

Both R3 conditions exceed the preregistered `d_perp > 0.05` discriminator.

Thus the R3 finite-time state is not representable as a single scalar interpolation from rest to the common equilibrium endpoint.

## Material-conditioned normalized transient

Measured R2 material delta in normalized equilibrium error:

```text
+2.7755575615628914e-17
```

which is numerically zero and below the preregistered `1e-12` null threshold.

Measured R3 material delta:

```text
-0.03826893475943344
```

Independent Wolfram prediction:

```text
-0.038268934759433076
```

The stiff material converges farther toward its equilibrium at the fixed 120-ms observation point, and the absolute material effect exceeds the preregistered `0.03` threshold.

The full 40/80/120/200/320-ms diagnostics also preserve the preregistered secondary trends:

- normalized R3 equilibrium error decreases with duration for both materials;
- R3 orthogonal transient fraction decreases toward zero at long duration;
- the stiff material has lower normalized R3 equilibrium error than baseline at every preregistered duration.

## Acoustic oracle

Maximum candidate-grid error versus the independent Wolfram roots:

```text
0.024700922407703274 Hz
```

against the `0.05 Hz` candidate threshold.

Maximum reference-grid error:

```text
0.0047009224076646206 Hz
```

against the `0.01 Hz` reference threshold.

Measured R3-minus-R2 shifts at 120 ms:

| material | mode | measured shift | Wolfram shift |
|---|---:|---:|---:|
| baseline | 1 | -19.20 Hz | -19.1978669 Hz |
| baseline | 2 | +22.60 Hz | +22.6189208 Hz |
| baseline | 3 | -72.70 Hz | -72.6670941 Hz |
| stiff | 1 | -26.90 Hz | -26.8924876 Hz |
| stiff | 2 | +26.95 Hz | +26.9861062 Hz |
| stiff | 3 | -96.60 Hz | -96.6195651 Hz |

All shift signs agree with the preregistered Wolfram oracle.

The weakest observed effect remained:

```text
384x local numerical floor
```

against the preregistered minimum of `5x`.

## Interpretation

Experiment 021 adds evidence not available from G1-M or G1-B alone.

G1-M established that the reduced material intervention can change the quasi-static physical equilibrium.

G1-B established that one scalar critically damped state can create finite-time realization, continuity, and state memory.

G1-C now shows that, under the same task intent and the same material-specific equilibrium endpoints:

1. the scalar-path null can be falsified by a multi-mode physical trajectory;
2. the normalized transient itself becomes material-conditioned;
3. the changed transient produces independently predicted acoustic consequences.

The important distinction is that the result is not merely caused by different equilibrium geometries. The R2 normalized timing remains material-independent, while R3 produces a material-dependent normalized transient.

## Claim boundary

Still unsupported:

- general Task Dynamics;
- multiple simultaneous or overlapping Gestures;
- shared-DOF task competition;
- biological muscle activation or force control;
- calibrated mass, damping, or Young's modulus;
- nonlinear or viscoelastic tissue mechanics;
- XPBD / FEM / FSI;
- source-filter coupling;
- phonetic identity;
- perceptual naturalness;
- production temporal/material APIs;
- Studio controls;
- neural components.

## Next falsification layer

The next scientific step can now test one stateful physical body under **two simultaneous or overlapping task-level Gestures**, with a preregistered shared-DOF interaction/competition intervention.

That should remain a separate experiment rather than being folded into G1-C.
