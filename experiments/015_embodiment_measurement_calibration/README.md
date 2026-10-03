# Experiment 015 — Embodiment measurement calibration (E0)

Issue: #40

This experiment preregisters the first calibration fixture for the Embodiment
measurement harness. It does **not** claim human-vocal-tract validity,
naturalness, phonetic identity, or morphology causality beyond this analytical
uniform-tube fixture.

## Research question

Can the current Fidelity-0 measurement path distinguish a known morphology
intervention from its own numerical/observer floor?

The calibrated causal chain is:

```text
prepared rest geometry: tract length L
        ↓
lossless closed-open 1D tube
        ↓
input-impedance resonances
        ↓
measured resonance frequencies
```

No Gesture is active in this E0 fixture. The empty `GestureScore` is held
identical across all conditions.

## Analytical positive control

For a rigid, lossless uniform tube with an acoustically closed inlet and ideal
pressure-release outlet,

```text
f_n = (2n - 1)c / (4L)
```

and therefore

```text
d ln(f_n) / d ln(L) = -1.
```

The checked-in `wolfram/embodiment_oracle.json` was generated independently
with Wolfram Language before inspecting Python experiment results.

## Fixed model assumptions

- sound speed: 343 m/s
- air density: 1.21 kg/m^3
- cross-sectional area: 3e-4 m^2
- baseline tract length: 0.17 m
- boundary: ideal pressure release at outlet
- walls: rigid
- propagation: lossless 1D plane wave
- source / waveform synthesis: none
- task plan: empty, identical across conditions
- candidate prepared-geometry section count: 10

The intervention is deliberately applied to the backend-specific prepared rest
geometry. `CreatureSpec` is held fixed because the current universal domain
schema does not yet expose a tract-length morphology parameter. This is an E0
measurement calibration, not evidence that arbitrary CreatureSpec morphology
axes are already represented.

## Morphology intervention sweep

Only total tract length changes:

| relative change | length |
|---:|---:|
| -10% | 0.153 m |
| -5% | 0.1615 m |
| 0% | 0.17 m |
| +5% | 0.1785 m |
| +10% | 0.187 m |

The first three resonances are measured in fixed windows that cover the entire
preregistered sweep:

- mode 1: 430–590 Hz
- mode 2: 1300–1750 Hz
- mode 3: 2200–2850 Hz

The candidate observer grid spacing is 0.05 Hz. A 0.01 Hz grid is used as a
reference observer perturbation.

## Numerical controls

### E0-A — identity negative control

Run the exact baseline calculation twice.

Expected: measured peak locations are identical up to floating-point noise.

### E0-B — analytical positive control

Compare the five-length sweep with the independent quarter-wave oracle.

Expected:

- resonance decreases monotonically as length increases;
- each candidate peak is within one candidate-grid step (0.05 Hz) of the oracle;
- central log sensitivity for eps=0.05 and eps=0.10 is within 0.005 of -1 for
  each of the first three modes.

### E0-C — observer / partition controls

Two distinct controls are recorded.

1. **Observer-grid control:** compare 0.05 Hz and 0.01 Hz resonance extraction
   grids. This is the primary numerical/measurement floor for peak location.
2. **Section-partition invariance:** at baseline length, compare 1, 10, and 40
   equal uniform sections on the same 0.05 Hz grid.

The second control is **not** treated as a conventional mesh-convergence study:
for this lossless piecewise-uniform transfer-matrix backend, subdividing an
otherwise uniform tube is algebraically equivalent apart from floating-point
composition error.

For each mode the conservative numerical floor is

```text
max(
    candidate grid step,
    max |candidate-grid peak - reference-grid peak|,
    max baseline section-partition peak delta
)
```

Using the full 0.05 Hz candidate step rather than half a step is intentionally
conservative.

## Primary discrimination gate

For every non-zero length intervention and every measured mode:

```text
|peak_intervention - peak_baseline| / numerical_floor > 5
```

The factor 5 is an engineering discrimination margin inherited from earlier
morphoacoustics experiments. It is not a perceptual threshold.

## Decision

`SUPPORT_EMBODIMENT_MEASUREMENT` requires all of:

1. identity peak delta <= 1e-12 Hz;
2. all measured peak frequencies are finite;
3. candidate peak error <= 0.05 Hz against the Wolfram oracle;
4. reference-grid peak error <= 0.01 Hz against the Wolfram oracle;
5. peak frequency is strictly monotone decreasing with tract length;
6. all six measured central log sensitivities (3 modes × 2 epsilons) are
   within 0.005 of -1;
7. baseline 1/10/40-section peak differences are <= 0.05 Hz;
8. every non-zero intervention exceeds 5× the preregistered numerical floor.

Otherwise the result is `MEASUREMENT_UNCALIBRATED`.

A failure does not imply that morphology has no causal acoustic effect. It
means the evaluator / observer / fixture is not yet calibrated well enough to
test H_E1.

## Outputs

The run writes:

- `sweep.csv` — oracle, candidate and reference peaks for all sweep points;
- `sensitivity.csv` — measured and oracle central log sensitivities;
- `partition_control.csv` — section-count invariance control;
- `decision.json` — gates, numerical floors, provenance and causal trace.

The ideal lossless input impedance has mathematical poles at resonance, so raw
impedance magnitudes are not required to remain finite. The measured resonance
**frequencies** and report quantities must be finite.

## Scope boundary

This experiment does not promote a production `EmbodimentReport` schema into
the domain package. A common evaluator API should be extracted only after this
calibration and at least one same-task/different-morphology E1 fixture establish
which fields are genuinely reusable.

## Reproduction

```bash
python experiments/015_embodiment_measurement_calibration/run.py \
  --output-dir experiment-015-output
```
