# Experiment 017 results — Embodied infeasibility boundary

Issue: #40

## Decision

**SUPPORT_EMBODIED_INFEASIBILITY**

All preregistered E1-B gates passed for the Fidelity-0 articulator reach-boundary
fixture.

This supports the narrow claim that an unchanged valid/supported CONSTRICT task
can cross from realizable to physically infeasible when only one articulator
reach endpoint crosses the requested task location, and that the infeasible
condition does not proceed into acoustic evaluation.

## Provenance

Final code-equivalent objective run before this results record:

- GitHub Actions run: `37171645071`
- source head: `0aa930181cd587be548a4546ac07aff9a70c0019`
- artifact: `experiment-017-output`
- artifact ID: `11291751448`
- artifact ZIP SHA-256:
  `31b03996fb9e2bbe1f86fe21b49db1b88db80a4fdcbb68dc53cbd7b6ccf22a8e`
- Python: 3.11.16
- NumPy: 2.4.6

## Canonical representation: PASS

The same task-level score was used for all three bodies:

```text
CONSTRICT(
    target="oral",
    location=0.65,
    target_area=2e-4 m²,
    onset=0.0 s,
    offset=0.3 s
)
```

Canonical SHA-256:

```text
4ee1ff8b70a4bb2d6a52b167a39c1b9d770cdbe9909f52e2b90354ed230d4ed9
```

The hash was identical before and after the complete experiment and in every
condition. No condition-specific target rewrite was performed.

## Morphology intervention isolation: PASS

The prepared tract geometry was exactly identical in all conditions:

- tract length: 0.170 m
- section count: 10
- rest area: 3e-4 m²
- same cavity and articulator identity/kind
- reachable_start: 0.30

Only `tongue.reachable_end` changed.

| condition | reachable_end |
|---|---:|
| M_plus | 0.70 |
| M_boundary | 0.65 |
| M_minus | 0.60 |

## Independent Wolfram reach oracle: PASS

The fixed Gesture location is `0.65`, or `0.1105 m` on the 0.17 m tract.

The independent Wolfram calculation gave:

| condition | normalized margin | metric margin | predicted |
|---|---:|---:|---|
| M_plus | +0.05 | +8.5 mm | FEASIBLE |
| M_boundary | 0.00 | 0.0 mm | FEASIBLE |
| M_minus | -0.05 | -8.5 mm | INFEASIBLE |

All fixture margins matched the checked-in Wolfram oracle within the
preregistered `1e-15` tolerance.

## Boundary classification: PASS

Observed statuses were exactly:

```text
M_plus     -> FEASIBLE
M_boundary -> FEASIBLE
M_minus    -> INFEASIBLE
```

No condition returned `INVALID` or `UNSUPPORTED`.

The exact-boundary result confirms the current inclusive contract:

```text
reachable_start <= location <= reachable_end
```

so `reachable_end == location == 0.65` remains realizable.

## Feasible task realization: PASS

Both feasible bodies selected section index 6 and modified only that section.

For M_plus and M_boundary:

- realized target area = `2e-4 m²`
- target-area residual = `0.0`
- modified section indices = `(6,)`
- acoustic backend call count = `1`

Thus the latent reach-capacity difference did not alter the realized task while
the requested location remained inside both reachable sets.

## Capability null control: PASS

M_plus and M_boundary differed only in unused positive reach slack. Their
realized physical states were exactly equal.

Their acoustic probe results were also exactly equal:

- response SHA-256 equal: yes
- maximum absolute impedance-array delta: `0.0`
- acoustic backend calls: `1` and `1`

This is an important negative control: not every morphology capability change
must produce an acoustic change.

## Embodied infeasibility / no fallback: PASS

M_minus crossed the reach boundary by -0.05 normalized units (-8.5 mm).

Observed causal chain:

```text
same valid CONSTRICT request
        ↓
reachable_end = 0.60 < requested location = 0.65
        ↓
LOCATION_UNREACHABLE (gesture index 0)
        ↓
INFEASIBLE
        ↓
physical state = None
        ↓
acoustic backend call count = 0
        ↓
acoustics = None
```

The negative body did not:

- move the Gesture location to 0.60;
- relax the target area;
- synthesize a nearby plausible acoustic result;
- call the acoustic backend and discard its output afterward.

The acoustic call-count gate directly verifies that causal evaluation stopped
at the physical infeasibility boundary.

## Interpretation

Experiments 016 and 017 now test complementary properties of Embodiment.

Experiment 016 established, for a feasible pair:

```text
same task
    -> morphology-specific physical realization
    -> body-dependent absolute acoustics
```

Experiment 017 establishes:

```text
same task
    -> morphology-specific reachable task set
    -> explicit physical infeasibility when outside that set
```

Together, the current Fidelity-0 model supports the narrow statement that
morphology determines both **how** a supported task is realized and **whether**
the task can be realized at all.

## What remains falsifiable

This fixture uses a deliberately simple normalized interval constraint. It does
not test a mechanically emergent feasibility boundary.

Stronger future tests should include boundaries arising from:

- non-self-similar geometry;
- local area/collision constraints;
- actuator force or stiffness limits;
- deformable tissue contact;
- coupled source/filter regimes.

A natural immediate next step under issue #40 is E1-C: sweep one morphology
parameter through several small interventions and measure sign, monotonicity,
local sensitivity, and nonlinear departure rather than relying on one A/B pair.

## Claim boundary

This result does not establish:

- biological realism of tongue reach;
- arbitrary creature capability transfer;
- muscle-force or tissue-contact feasibility;
- human phonetic identity;
- perceptual naturalness;
- source/filter coupling;
- FSI validity.

It establishes only the preregistered E1-B reach-boundary claim.
