# Experiment 016 results — Same-task morphology covariance

Issue: #40

## Decision

**SUPPORT_TASK_MORPHOLOGY_COVARIANCE**

All preregistered E1-A gates passed for the self-similar Fidelity-0
prepared-morphology fixture.

This supports the narrow claim that one unchanged non-empty CONSTRICT task can
be transferred across the specified +10% tract-length intervention, realized in
body-specific physical coordinates, and preserve the predicted dimensionless
acoustic task effect.

It does not establish arbitrary morphology transfer.

## Provenance

Final code-equivalent objective run before this results record:

- GitHub Actions run: `37114056911`
- source head: `b0489fee99f75f8f9b2f8be2f31e8b37e5e1f08e`
- artifact: `experiment-016-output`
- artifact ID: `11271137167`
- artifact ZIP SHA-256:
  `548e209c0293e0e86bc7d3e1a4112aba5bb707650f43131bdf9604af55f815c6`
- Python: 3.11.16
- NumPy: 2.4.6

The repository test/typecheck workflow and the dedicated Experiment 016 workflow
both passed on the same head.

## Representation invariance: PASS

The canonical non-empty score was:

```text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=2e-4 m²,
    onset=0.0 s,
    offset=0.3 s
)
```

Its canonical SHA-256 was:

```text
4ee1ff8b70a4bb2d6a52b167a39c1b9d770cdbe9909f52e2b90354ed230d4ed9
```

The hash was identical:

- before evaluation,
- after evaluation,
- for M0-G candidate/reference,
- for M1-G candidate/reference.

No body-specific axial coordinate, section index, resonance target, or acoustic
target was inserted into the Gesture.

## Task realization: PASS

Both Gesture conditions were `FEASIBLE`.

| quantity | M0 | M1 |
|---|---:|---:|
| target normalized location | 0.65 | 0.65 |
| selected zero-based section | 6 | 6 |
| modified sections | 6 only | 6 only |
| target area | 2e-4 m² | 2e-4 m² |
| area residual | 0.0 | 0.0 |
| realized normalized center | ~0.65 | 0.65 |
| normalized location residual | 1.11e-16 | 0.0 |

The candidate and 0.01 Hz reference observer runs produced identical physical
states for each body.

## Body-specific physical realization: PASS

The same normalized task was realized at different absolute physical
coordinates:

```text
M0 center = 0.1105 m
M1 center = 0.12155 m
```

Therefore:

```text
M1 / M0 axial-center scale = 1.1
```

The constricted section length also scaled:

```text
0.017 m -> 0.0187 m
M1 / M0 = 1.1
```

The measured axial scale was `1.0999999999999999`; section-length scale was
`1.1`.

This is the key physical realization result: the canonical task stayed at
`location=0.65`, while its body-specific metric coordinate changed.

## Independent Wolfram oracle: PASS

All four conditions × first three modes matched the independent Wolfram
transfer-matrix oracle.

Maximum absolute peak errors:

- 0.05 Hz candidate observer: `0.0192513 Hz`
- 0.01 Hz reference observer: `0.00470588 Hz`

The largest candidate/reference peak-location delta was `0.02 Hz`, so the
preregistered local floor remained `0.05 Hz`.

## Morphology and Gesture effects: PASS

Every morphology effect and every Gesture effect exceeded the 5× engineering
discrimination margin.

The weakest resolved effect was:

```text
M1, mode 1, Gesture effect:
|446.70 - 458.55| = 11.85 Hz
floor = 0.05 Hz
effect / floor = 237×
```

Other effect/floor ratios ranged upward into the thousands.

Thus E1-A did not obtain its transfer result by using an acoustically inert
Gesture or an unresolved morphology intervention.

## Absolute scale covariance: PASS

The preregistered physical symmetry predicts

```text
f(M1, c) = f(M0, c) / 1.1
expected M1/M0 frequency ratio = 0.909090909...
```

for both Rest and Gesture conditions.

Measured cross-body ratios:

| mode | Rest M1/M0 | Gesture M1/M0 |
|---:|---:|---:|
| 1 | 0.90909992 | 0.90912791 |
| 2 | 0.90906988 | 0.90907056 |
| 3 | 0.90910172 | 0.90909277 |

The maximum scale residual was `0.0318182 Hz`, below the conservative
preregistered `0.0954545 Hz` observer budget.

## Dimensionless task-transfer invariant: PASS

For each mode,

```text
g(M) = log(f(M, Gesture) / f(M, Rest))
D = |g(M1) - g(M0)|
```

was evaluated.

| mode | g(M0) | g(M1) | D | observer budget |
|---:|---:|---:|---:|---:|
| 1 | -0.02621290 | -0.02618211 | 3.079e-5 | 4.219e-4 |
| 2 | 0.03289107 | 0.03289182 | 7.484e-7 | 1.365e-4 |
| 3 | -0.03245946 | -0.03246931 | 9.847e-6 | 8.464e-5 |

All three body-to-body differences were inside their preregistered observer
uncertainty budgets.

The independent Wolfram oracle predicts exactly zero difference for this
self-similar fixture.

## Interpretation

Experiment 004 had already shown qualitatively that one unchanged Gesture could
produce different physical/acoustic results on different prepared bodies.

Experiment 016 strengthens that result in three ways:

1. it records explicit task residuals rather than only checking that responses
   differ;
2. it verifies body-specific metric realization of an unchanged normalized
   task;
3. it tests a preregistered dimensionless invariant that should survive the
   morphology change.

The supported causal statement is therefore:

```text
same task representation
        ↓
morphology-specific physical coordinate
        ↓
different absolute acoustic state
        ↓
preserved dimensionless task effect
```

for this specific self-similar Fidelity-0 fixture.

## What remains falsifiable

This experiment deliberately chooses a symmetry-friendly body intervention.
The next stronger E1 test should break that symmetry.

A useful next step is a **non-self-similar morphology intervention** in which
the same task remains meaningful but there is no global 1/L acoustic scaling
law to rescue the result. Candidate interventions include:

- nonuniform rest area-function morphology,
- altered articulator reach or task feasibility,
- material/compliance parameters once available.

That next experiment should preserve the same reporting split:

- task invariance,
- task residual,
- body-specific physical realization,
- acoustic effect vs numerical floor,
- explicit failure category.

## Claim boundary

This result does not show:

- arbitrary body transfer,
- phonetic identity retention,
- human articulatory realism,
- material or deformable-tissue covariance,
- source-filter coupling,
- perceptual equivalence,
- FSI validity.

It establishes only the preregistered E1-A self-similar transfer claim.
