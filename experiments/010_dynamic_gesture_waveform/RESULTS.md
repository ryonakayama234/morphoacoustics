# Experiment 010 results

## Decision

**SUPPORTED** for the minimal M3 dynamic-capability claim.

This result supports using the Experiment-008 temporal representation (`explicit onset/offset events + sampled continuous trajectory`) to drive the next X1b design step. It does **not** promote a general temporal API or claim true moving-domain acoustics.

## CI run

GitHub Actions `experiment-010` completed successfully on Python 3.11.16 / NumPy 2.4.6 after correcting the implementation to use the preregistered Experiment-010 event window (`onset=0.08 s`, `offset=0.42 s`). The ordinary repository test workflow also passed on the corrected PR head.

## Preregistered gates

### Event window

The corrected run uses the preregistered event times:

- onset: `0.08 s`
- offset: `0.42 s`
- active-window duration: `0.34 s`

These values are defined locally by Experiment 010 rather than inherited from Experiment 008.

### Motion intervention

Same body, ramp duration only changed (`fast=30 ms`, `slow=90 ms`):

| Body | normalized RMS waveform difference |
|---|---:|
| wide-body | 0.0398919 |
| narrow-body | 0.0343889 |

Both exceed the preregistered `> 0.01` gate.

### Morphology intervention

Same motion, prepared body changed:

| Motion | normalized RMS waveform difference |
|---|---:|
| fast | 0.0355333 |
| slow | 0.0294974 |

Both exceed the preregistered `> 0.01` gate.

### Discretization sensitivity

Candidate rendering used a 5 ms control grid / 256-sample hop and was compared with a 2.5 ms / 128-sample reference:

| Condition | normalized RMS difference |
|---|---:|
| wide-body / fast | 0.00190442 |
| wide-body / slow | 0.00147658 |
| narrow-body / fast | 0.00164118 |
| narrow-body / slow | 0.00133553 |

All are well below the preregistered `< 0.20` gate.

### Independent Wolfram temporal oracle

For `S(x)=3x^2-2x^3`, Wolfram independently confirmed endpoint values/slopes `{0,1,0,0}` and `max |S''| = 6` on `[0,1]`. The resulting 5 ms linear-interpolation bounds were:

- fast 30 ms ramp: `0.0208333333`
- slow 90 ms ramp: `0.00231481481`

Observed maximum activation errors were:

- fast: `0.0173795556`
- slow: `0.00218621399`

Both remain inside the independent bounds. The bound depends on the normalized smoothstep curvature and sampling/ramp ratio, so correcting the absolute onset/offset times does not change it.

### Finite output

All four body × motion waveform conditions were finite. No NaN/Inf gate failed.

## Interpretation

The corrected experiment distinguishes the intended interventions under the current fixture:

- changing only gesture timecourse changes the resulting waveform;
- changing only prepared morphology also changes the resulting waveform;
- the observed effects are much larger than the tested discretization perturbation;
- the adopted event + sampled-trajectory representation remains consistent with the independent smoothstep interpolation bound.

Therefore the minimal dynamic capability needed to design X1b is supported under this model class.

## Important limitation

The waveform renderer is a **quasi-stationary short-time time-varying transfer filter**. It recomputes transfer from instantaneous realized geometry and overlap-adds filtered source frames; it does not propagate acoustic state through a continuously moving tract. The result must not be reported as full time-domain moving-boundary acoustics or FSI.

Other retained limitations include manual prepared 1D geometry, Experiment-009 attenuation/load/radiation surrogates, an explicit periodic source, no vocal-fold self-oscillation, no source-filter back-coupling, and only one CONSTRICT gesture / one motion-axis intervention.
