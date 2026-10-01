# Experiment 011 results

## Decision

**ADOPT** for the narrow M5a claim:

> Relative timing / overlap between two spatially distinct CONSTRICT Gestures is an independently observable compiler-relevant variable under the current model class.

This result supports designing a compiler-side `CoordinationPlan` candidate for M5. It does **not** promote a general coarticulation API or establish linguistic naturalness.

## CI execution

GitHub Actions workflow `experiment-011` completed successfully on Python 3.11.16 / NumPy 2.4.6.

The experiment uses the preregistered fixed conditions in `README.md`, including the 48 kHz Experiment-009 source/acoustic path and the wide-body prepared morphology.

## Preregistered semantic / Wolfram gates

### Activation amount

The reconstructed activation integrals remained effectively identical across active Gesture instances:

- Gesture A: `0.15000000000000002 s`
- sequential Gesture B: `0.15 s`
- overlap Gesture B: `0.14999999999999997 s`

Thus the intervention did not change the individual Gesture activation amount; it changed relative timing.

### Sequential vs overlap

- sequential overlap integral: `0`
- sequential normalized overlap coefficient: `0`
- overlap overlap integral: `0.03 s`
- reconstructed overlap normalized coefficient: `0.21132476373795991`
- independent Wolfram reference: `0.2108433734939759`

The coefficient difference is below the preregistered `1e-3` tolerance.

### Activation interpolation bound

Maximum observed 5 ms reconstruction error was approximately:

- `0.0173803324`

Independent Wolfram bound:

- `0.0208333333`

All activation reconstruction errors remained inside the bound.

## Physical result

The realized geometry showed simultaneous constriction at both target locations only in the overlap condition:

| Condition | simultaneous two-location constriction duration |
|---|---:|
| A only | 0 s |
| B only | 0 s |
| sequential | 0 s |
| overlap | 0.0586666667 s |

The difference from the nominal 60 ms event-window overlap is due to observation at short-time frame centers, not a changed event definition.

Because Gesture A and B target different normalized locations (`0.25` and `0.75`), this result is not produced by same-section overwrite ordering.

## Acoustic result

The preregistered main comparison produced:

- sequential vs overlap normalized RMS waveform difference: `0.0478466835`

Candidate-vs-finer-reference discretization differences were:

- sequential: `0.00308504168`
- overlap: `0.00283405730`

Therefore:

- effect `> 0.01`: **pass**
- effect `> 5 × max(discretization difference)`: **pass**

The coordination effect is about `15.5×` the larger tested discretization perturbation.

All waveform outputs were finite.

## Interpretation

Within this deliberately small fixture, the same two Gesture targets and individual activation amounts produce a distinct joint physical/acoustic trajectory when their relative timing is changed from sequential to overlapping.

That is enough evidence to treat **coordination / relative timing as an explicit derived representation in the performance compiler**, rather than reconstructing it implicitly from concatenated rendered audio.

The next design step should therefore be a small compiler-side candidate such as:

```text
Gesture inventory
      ↓
CoordinationPlan
  - event relations
  - overlap / relative timing
      ↓
Gestural Score
```

The candidate should remain outside the universal physical kernel until additional experiments establish what semantics generalize beyond this two-CONSTRICT fixture.

## Creator-listening status

Scientific ADOPT does not depend on preference listening.

A blinded sequential/overlap A/B pair is available from the workflow artifacts for creator evaluation of:

- perceived separation vs continuity;
- audible transition discontinuity;
- possible usefulness as a creative control.

That perceptual result should be recorded separately from this physical/numerical decision.

## Important limitations

Retained limitations include:

- manual prepared 1D geometry;
- only two CONSTRICT tasks;
- experiment-local activation reconstruction;
- no task-dynamic controller or articulator competition;
- quasi-stationary short-time filtering with no carried acoustic state;
- explicit periodic source rather than self-oscillating vocal folds;
- no source-filter back-coupling;
- no claim that the fixture corresponds to a valid phoneme, mora, word, or natural coarticulation pattern.

## Decision consequence

**Proceed to M5 compiler design with an explicit `CoordinationPlan` candidate, but keep it integration/compiler-side and experimental until broader evidence exists.**
