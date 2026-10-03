# Experiment 015 results — Embodiment measurement calibration

Issue: #40

## Decision

**SUPPORT_EMBODIMENT_MEASUREMENT**

The preregistered E0 calibration gates all passed for the rigid, lossless,
closed-open uniform-tube fixture.

This result supports the narrow claim that the current Fidelity-0 measurement
path can recover a known tract-length acoustic sensitivity and separate the
intervention from its declared observer/numerical floor.

It does **not** yet support the broader H_E1 claim that arbitrary
morphology-independent task intent is realized causally across different
bodies.

## Provenance

Final code-equivalent objective run before this results record:

- GitHub Actions run: `37108496114`
- source head: `0bcb427806171ba4f83fc66543b48f5c38136ea7`
- Python: 3.11.16
- NumPy: 2.4.6
- output artifact: `experiment-015-output`
- artifact ID: `11268288752`
- artifact ZIP SHA-256:
  `304c0ff07faf336a81e3707fdc7b2c18c5584661df4aba6c22b2923e71bda95f`

Repository tests and type checking also passed on the same experiment
implementation before the documentation-only results commit.

## E0-A — identity negative control: PASS

The exact baseline calculation was run twice on the same observer grid:

- run 1 first resonance: `504.4 Hz`
- run 2 first resonance: `504.4 Hz`
- absolute delta: `0.0 Hz`
- preregistered tolerance: `1e-12 Hz`

The evaluator therefore did not create an apparent morphology effect when no
intervention was applied.

## E0-B — analytical tract-length positive control: PASS

All five tract lengths and all first three resonance modes matched the
independent Wolfram quarter-wave oracle within the preregistered observer-grid
bounds.

Maximum observed absolute errors:

- 0.05 Hz candidate grid: approximately `0.02353 Hz` (< 0.05 Hz gate)
- 0.01 Hz reference grid: approximately `0.004706 Hz` (< 0.01 Hz gate)

For every mode, measured resonance frequency decreased monotonically as tract
length increased.

### Dimensionless log sensitivity

The analytical prediction is

```text
d ln(f_n) / d ln(L) = -1.
```

Measured central log sensitivities were:

| epsilon | mode 1 | mode 2 | mode 3 |
|---:|---:|---:|---:|
| 0.05 | -0.99965335 | -0.99996699 | -1.00004952 |
| 0.10 | -1.00000000 | -1.00000000 | -0.99998024 |

The largest absolute sensitivity error was approximately
`3.47e-4`, well inside the preregistered `0.005` tolerance.

## E0-C — observer / partition controls: PASS

### Observer-grid floor

Across the tract-length sweep, the largest difference between the 0.05 Hz
candidate grid and 0.01 Hz reference grid was `0.02 Hz`.

The experiment preregistered a conservative floor using the **full** candidate
grid step, so the final numerical floor was:

| mode | numerical floor |
|---:|---:|
| 1 | 0.05 Hz |
| 2 | 0.05 Hz |
| 3 | 0.05 Hz |

### Uniform section partition invariance

At the 0.17 m baseline, splitting the same uniform tube into 1, 10, or 40 equal
sections gave identical measured peak locations on the candidate grid:

- mode 1: `504.4 Hz`
- mode 2: `1513.25 Hz`
- mode 3: `2522.05 Hz`

All section-partition peak deltas were `0.0 Hz`.

This is retained as a partition-invariance negative control, not interpreted as
general spatial mesh convergence.

## Morphology intervention vs numerical floor: PASS

Every non-zero tract-length intervention exceeded the preregistered 5x
discrimination margin.

The smallest observed ratio was the +5% length intervention on mode 1:

```text
morphology effect = 24.0 Hz
numerical floor   = 0.05 Hz
effect / floor    = 480x
```

The largest observed ratio was the -10% intervention on mode 3:

```text
morphology effect = 280.25 Hz
numerical floor   = 0.05 Hz
effect / floor    = 5605x
```

Thus the known physical intervention is separated from the declared observer
floor by a large margin in this calibration fixture.

## Causal-trace check

The recorded chain remained internally consistent:

```text
prepared total tract length changed
        ↓
realized empty-Gesture state retained that exact length
        ↓
uniform-tube input impedance changed
        ↓
resonance peaks shifted with the predicted inverse-length law
```

The realized tract lengths matched the requested intervention values to the
preregistered floating-point tolerance.

## Interpretation

Experiment 015 calibrates the **measurement instrument**, not the full
Embodiment hypothesis.

What is now supported:

> For a backend-specific prepared uniform-tube length intervention with an
> analytical response law, the current evaluator recovers the expected
> direction and normalized sensitivity, reports a no-intervention null result,
> and separates the intervention from the observer/partition controls.

What is still unsupported:

- that a non-empty morphology-independent Gesture is preserved across bodies;
- that two feasible bodies realize the same task in different physical
  coordinates;
- that a morphology constraint alone can create FEASIBLE vs INFEASIBLE;
- that material stiffness or deformable tissue interventions are measurable;
- that any of these differences are perceptually meaningful or natural.

## Consequence for #40

The E0 measurement prerequisite is now satisfied strongly enough to proceed to
the next falsification layer:

```text
E1-A
same non-empty task-level Gesture
+ one preregistered morphology-axis intervention
        ↓
task target remains invariant
        ↓
body-specific physical realization
        ↓
predicted acoustic difference > numerical floor
```

The next experiment should reuse the calibrated reporting pattern but must add
explicit task residuals so that a morphology effect cannot be manufactured by
changing the canonical Gesture target.
