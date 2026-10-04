# Experiment 018 — Local-area morphology sensitivity sweep (E1-C)

Issue: #40

Depends on Experiment 017 / PR #45.

## Research question

Can one unchanged non-empty task be carried through a **non-self-similar,
single-axis morphology sweep** while the simulator recovers the independently
predicted sign, monotonicity, and dimensionless acoustic sensitivity above its
observer floor?

This is E1-C from issue #40. It deliberately moves beyond a single A/B
difference.

## Fixed fixture

All conditions use:

- tract length: 0.170 m
- 10 equal-length sections
- baseline rest area: 3e-4 m²
- same CreatureSpec and articulator reach
- same Fidelity-0 realizer/backend
- same observer windows
- same non-empty CONSTRICT score in the Gesture condition

The canonical Gesture is:

```text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=2e-4 m²,
    onset=0.0 s,
    offset=0.3 s,
)
```

With 10 equal sections, this task realizes on zero-based section 6.

## Morphology axis

Only the **prepared rest area of zero-based section 0** changes:

```text
A0(epsilon) = 3e-4 * (1 + epsilon) m²

epsilon = -0.10, -0.05, 0, +0.05, +0.10
```

All other prepared sections remain at 3e-4 m².

The intervention section and Gesture section are intentionally different:

```text
morphology intervention -> section 0
task realization        -> section 6
```

This avoids the global 1/L symmetry used in Experiment 016 and prevents the
sweep from being merely a rescaling of the whole tract.

## 2 × 5 design

For every morphology sweep point the experiment evaluates:

- Rest: empty GestureScore
- Gesture: the exact same non-empty CONSTRICT score

This yields ten physical/acoustic conditions.

## Independent Wolfram oracle

`wolfram/local_area_sensitivity_oracle.json` is generated from an independent
lossless transfer-matrix calculation.

The oracle predicts that the first three input-impedance resonance frequencies
decrease monotonically as section-0 rest area increases, both at Rest and under
the fixed Gesture.

The oracle also provides central dimensionless sensitivities:

```text
S = d ln(f_n) / d ln(A_section0)
```

estimated at epsilon=0.05 and epsilon=0.10.

All six primary sensitivities are negative, but their magnitudes differ by mode
and by task condition. This is a local-geometry response, not a universal area
law.

## Observer and numerical floor

Candidate peak grid: 0.05 Hz.

Reference peak grid: 0.01 Hz.

Fixed mode windows:

- mode 1: 470–520 Hz
- mode 2: 1480–1600 Hz
- mode 3: 2400–2570 Hz

For each condition/mode:

```text
numerical_floor_hz =
max(
    0.05 Hz,
    |candidate_peak - reference_peak|
)
```

Section count is not varied: changing section count would move the physical
extent of the local morphology intervention and the one-section Gesture
realization, so it is not a pure numerical perturbation at this fidelity.

## Task invariance / realization

For every Gesture condition:

- canonical score SHA-256 must remain unchanged;
- realization must be FEASIBLE;
- section 6 must be the only section modified relative to that body's prepared
  rest geometry;
- realized section-6 area must equal 2e-4 m²;
- the body-specific section-0 morphology area must survive realization exactly.

Thus the local body intervention and the task act at different causal locations.

## Morphology effect gate

For every nonzero epsilon, task condition, and mode:

```text
|f(epsilon) - f(0)| / local_numerical_floor > 5
```

The 5× value is an engineering discrimination margin, not a perceptual
threshold.

## Monotonicity gate

For each of the six traces (Rest/Gesture × three modes), measured candidate
resonance frequency must be strictly decreasing as section-0 area increases.

This is fixture-specific and is preregistered from the Wolfram oracle.

## Dimensionless sensitivity gate

For epsilon in {0.05, 0.10}:

```text
S(epsilon) =
[ln f(+epsilon) - ln f(-epsilon)] /
[ln(1+epsilon) - ln(1-epsilon)]
```

Requirements:

- candidate sensitivities are negative;
- reference sensitivities are negative;
- candidate `|S - S_Wolfram| <= 0.001`;
- reference `|S - S_Wolfram| <= 0.0002`.

The tolerances were fixed before the Python objective run. An independent
Wolfram quantization check predicted worst-case 0.05-Hz-grid sensitivity error
of approximately 2.71e-4 and 0.01-Hz-grid error of approximately 4.1e-5.

## Nonlinear departure diagnostic

The experiment records

```text
N = |S(0.10) - S(0.05)|
```

for every mode/task condition.

It also records a conservative sensitivity observer bound by propagating the
declared per-frequency numerical floors through each log-sensitivity estimate
and summing the epsilon=0.05 and epsilon=0.10 bounds.

**N is diagnostic, not a PASS gate.**

The independent oracle predicts N around 6e-5 to 2.5e-4, below the conservative
propagated uncertainty at this resolution. Therefore this experiment must not
claim resolved nonlinearity merely because the two finite-difference estimates
are unequal.

## Decision

### SUPPORT_LOCAL_AREA_MORPHOLOGY_SENSITIVITY

Requires:

1. canonical Gesture representation unchanged;
2. morphology intervention isolated to section-0 rest area;
3. all ten conditions FEASIBLE and supported;
4. Gesture task residuals remain within exact/tight fixture tolerance;
5. candidate peaks match Wolfram within 0.05 Hz;
6. reference peaks match Wolfram within 0.01 Hz;
7. every nonzero morphology effect exceeds 5× local observer floor;
8. all six sweep traces have the preregistered monotone-decreasing direction;
9. all candidate/reference sensitivities have the predicted negative sign;
10. sensitivity magnitudes match the independent oracle within their
    preregistered tolerances.

Failure classes preserve causal meaning:

- `REPRESENTATION_LEAK`
- `CAUSAL_TRACE_INCONSISTENT`
- `INVALID_REQUEST_REGRESSION`
- `BACKEND_UNSUPPORTED`
- `TASK_REALIZATION_FAILED`
- `MEASUREMENT_REGRESSION`
- `NUMERICALLY_UNRESOLVED`
- `MONOTONICITY_FAILED`
- `SENSITIVITY_DIRECTION_FAILED`
- `SENSITIVITY_ORACLE_MISMATCH`

## Claim boundary

A pass supports only:

> For this Fidelity-0 non-self-similar local-area fixture, one unchanged
> CONSTRICT task remains correctly realized while a single prepared morphology
> area axis produces resolved, monotone, independently predicted acoustic
> sensitivity.

It does not establish:

- arbitrary area-function morphology transfer;
- biological vocal-tract calibration;
- phonetic identity;
- perceptual naturalness;
- deformable tissue mechanics;
- material sensitivity;
- source/filter coupling;
- FSI validity.

## Run

```bash
python experiments/018_local_area_morphology_sensitivity/run.py \
  --output-dir experiment-018-output
```
