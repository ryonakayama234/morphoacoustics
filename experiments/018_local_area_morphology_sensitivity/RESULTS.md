# Experiment 018 results — Local-area morphology sensitivity sweep

Issue: #40

## Decision

**SUPPORT_LOCAL_AREA_MORPHOLOGY_SENSITIVITY**

All preregistered E1-C gates passed for the non-self-similar Fidelity-0
single-section rest-area sweep.

This supports the narrow claim that one unchanged non-empty CONSTRICT task
remains correctly realized while a single local prepared-morphology area axis
produces resolved, monotone, independently predicted acoustic sensitivity.

## Provenance

Final code-equivalent objective run before this results record:

- GitHub Actions run: `37172002294`
- source head: `f011cd4f76a00d8341a5f71ea6b86b4fb3b57246`
- artifact: `experiment-018-output`
- artifact ID: `11292021309`
- artifact ZIP SHA-256:
  `cc74195ab2a7e464f307d6cdd8f105efaaa73220bda3c1aa16c023e11ea3315b`
- Python: 3.11.16
- NumPy: 2.4.6

The dedicated Experiment 018 workflow and the repository test/typecheck
workflow both passed on the same head.

## Representation and task invariance: PASS

The canonical Gesture was unchanged across all five morphology points:

```text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=2e-4 m²,
    onset=0.0 s,
    offset=0.3 s
)
```

The morphology intervention acts on section 0, while the Gesture realizes on
section 6.

For every Gesture condition:

- selected section = 6;
- modified section relative to prepared body = 6 only;
- realized target area = `2e-4 m²`;
- target-area residual = `0.0`;
- candidate/reference physical states were exactly equal;
- section-0 morphology area survived realization exactly.

Thus the acoustic sweep was not produced by a body-specific Gesture rewrite.

## Morphology intervention isolation: PASS

Only zero-based prepared section 0 rest area changed:

| relative change | section-0 area |
|---:|---:|
| -10% | 2.70e-4 m² |
| -5% | 2.85e-4 m² |
| 0% | 3.00e-4 m² |
| +5% | 3.15e-4 m² |
| +10% | 3.30e-4 m² |

Tract length, section lengths, all other rest areas, CreatureSpec, articulator
reach, backend, observer, and canonical task were fixed.

## Independent Wolfram peak oracle: PASS

All 10 task/morphology conditions × first three resonance modes matched the
independent transfer-matrix oracle.

Maximum peak-location errors:

- 0.05 Hz candidate grid: `0.0246819 Hz`
- 0.01 Hz reference grid: `0.00496997 Hz`

Both remain inside the preregistered 0.05 Hz / 0.01 Hz bounds.

## Morphology effect vs observer floor: PASS

Every non-zero morphology intervention in both Rest and Gesture conditions
exceeded the 5× discrimination margin.

The smallest observed ratio was:

```text
Gesture, +5%, mode 1:
effect = 2.40 Hz
floor  = 0.05 Hz
effect / floor = 48×
```

The largest ratios were several hundred times the declared floor.

This demonstrates that the measured local-area response is not an observer-grid
artifact at the preregistered resolution.

## Monotonicity: PASS

For all six traces:

```text
Rest    × modes 1..3
Gesture × modes 1..3
```

resonance frequency decreased strictly as section-0 area increased.

This is a fixture-specific prediction from the independent Wolfram model, not a
claim that arbitrary tract-area perturbations must shift every resonance in the
same direction.

## Dimensionless morphology sensitivity: PASS

Primary observable:

```text
S = d ln(f_n) / d ln(A_section0)
```

estimated by symmetric finite differences at ±5% and ±10%.

All candidate and reference sensitivities were negative as preregistered.

Representative results:

| task | epsilon | mode | candidate S | Wolfram S |
|---|---:|---:|---:|---:|
| Rest | 0.05 | 1 | -0.0980505 | -0.0982817 |
| Rest | 0.05 | 2 | -0.0855023 | -0.0857731 |
| Rest | 0.05 | 3 | -0.0635802 | -0.0636377 |
| Gesture | 0.05 | 1 | -0.0996328 | -0.0996615 |
| Gesture | 0.05 | 2 | -0.0862512 | -0.0862592 |
| Gesture | 0.05 | 3 | -0.0554486 | -0.0554797 |

Across both epsilon values and both task conditions:

- maximum candidate sensitivity error:
  `2.70779e-4` < `0.001` gate;
- maximum reference sensitivity error:
  `4.09123e-5` < `0.0002` gate.

The response is therefore not merely monotone; its normalized local slope also
matches the independent model.

## Nonlinear departure: NOT RESOLVED, by design

The diagnostic

```text
N = |S(0.10) - S(0.05)|
```

was recorded for all six task/mode combinations.

The Wolfram oracle predicts small departures of approximately
`6e-5 ... 2.5e-4`.

After propagating the full per-frequency observer floors conservatively through
both log-sensitivity estimates, all six diagnostics were classified:

```text
BELOW_5X_OBSERVER_FLOOR
```

Resolved-nonlinearity count:

```text
0 / 6
```

This is not an E1-C failure. The experiment was preregistered to record
nonlinear departure without claiming it was resolved unless it exceeded its
own uncertainty budget.

The correct conclusion is:

> the ±10% sweep is consistent with the independent weakly nonlinear response,
> but the present 0.05 Hz candidate observer is not calibrated to make a strong
> claim about that small curvature.

## Interpretation

Experiments 015–018 now establish four complementary pieces of the current
Fidelity-0 Embodiment model:

```text
015 E0:
measurement instrument reproduces known geometry -> acoustics sensitivity

016 E1-A:
same feasible task transfers into body-specific physical coordinates

017 E1-B:
same valid task can become explicitly physically infeasible

018 E1-C:
one non-self-similar morphology axis has a reproducible local acoustic
sensitivity curve under the unchanged task
```

Experiment 018 is especially useful because global tract-length similarity is
no longer available as the explanatory symmetry. A local body parameter,
spatially separated from the Gesture realization, produces a mode-dependent
sensitivity vector.

For the ±5% candidate estimate under Gesture, for example:

```text
d ln(f) / d ln(A_section0)
≈ [-0.09963, -0.08625, -0.05545]
```

This is a first concrete candidate column for a future Embodiment sensitivity
matrix, while still retaining the underlying per-observable values rather than
collapsing them into one score.

## What remains falsifiable

The next useful step is not to immediately aggregate everything into a universal
index.

Stronger tests include:

- repeat the same sweep on another local-area section and compare sensitivity
  direction/magnitude;
- choose a morphology direction expected to be acoustically weak or near-null;
- add a genuinely different morphology axis such as material/compliance once a
  suitable backend exists;
- later assemble multiple validated columns into an experiment-level
  `J_emb` and inspect rank/conditioning.

This would distinguish "the evaluator can measure one chosen body axis" from
"the current task set can identify multiple independent morphology directions."

## Claim boundary

This result does not establish:

- arbitrary area-function anatomy;
- human vocal-tract calibration;
- vowel or phonetic identity;
- perceptual naturalness;
- deformable tissue or material sensitivity;
- source/filter coupling;
- FSI validity.

It establishes only the preregistered Fidelity-0 local-area E1-C sensitivity
claim.
