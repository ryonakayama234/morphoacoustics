# Experiment 011 — sequential vs overlapping Gesture coordination (M5a)

Issue: #18

## Why this experiment exists

M5 needs to compile a short Script into a pronunciation plan, a Gesture inventory, a coordination/coupling plan, and finally one continuous Gestural Score.

The project already has evidence that:

- explicit onset/offset events plus sampled continuous trajectories are a viable temporal representation candidate (Experiment 008);
- changing one Gesture timecourse changes physical state and waveform under the current model class (Experiment 010 / M3);
- the validated dynamic capability can cross the Studio boundary as a reproducible Take (X1b).

What has not yet been tested is whether **relative timing / overlap between multiple Gestures** produces an independently observable physical/acoustic consequence under the current model class.

This experiment tests that question before any general coordination API is promoted.

## Research question

With body, source, Gesture targets, individual Gesture durations, trajectory family, acoustic backend and render duration fixed, does changing only the relative timing of two spatially distinct CONSTRICT Gestures from sequential to overlapping produce:

1. an explicitly different simultaneous physical state; and
2. a reproducible acoustic difference that is larger than the tested numerical discretization perturbation?

## Design principle

No production coordination API is added for this experiment.

`GestureScore` already holds multiple Gestures and the Fidelity-0 realizer can apply multiple active CONSTRICT requests. Experiment 011 uses that existing capability through experiment-local sampled activation reconstruction.

The two Gestures target **different tract locations** so tuple-order overwrite cannot masquerade as a coordination effect.

## Fixed conditions

- prepared morphology: Experiment-008 `wide-body`, rest area `3e-4 m^2`
- serial 1D tract: 10 × 17 mm sections
- sample rate: 48 kHz
- render duration: 0.50 s
- explicit deterministic source: Experiment-009 harmonic source, F0 = 100 Hz, 40 harmonics
- target area for both Gestures: `5e-5 m^2`
- Gesture A normalized location: `0.25`
- Gesture B normalized location: `0.75`
- individual Gesture duration: `0.18 s`
- activation attack/release: 30 ms smoothstep
- candidate control grid: 5 ms
- reference control grid: 2.5 ms
- candidate short-time hop: 256 samples
- reference short-time hop: 128 samples
- acoustic model: Experiment-009 lossy segmented-tube transfer plus observer proxy
- frame size: 1024 samples

Raw pressure output and listening-normalized WAV are kept separate.

## Intervention

Only Gesture B relative timing changes.

### Sequential

- Gesture A: `0.08–0.26 s`
- Gesture B: `0.26–0.44 s`

There is no simultaneous active interval.

### Overlap

- Gesture A: `0.08–0.26 s`
- Gesture B: `0.20–0.38 s`

The event windows overlap for 60 ms.

### Baselines

The same renderer also produces:

- `A_only`
- `B_only`

These are not the main intervention; they help distinguish individual Gesture effects from the combined simultaneous state.

## Independent Wolfram preregistration

For the activation envelope

`a(t; on, off) = S((t-on)/r) S((off-t)/r)`

with `S(x)=3x^2-2x^3` clipped to `[0,1]` and `r=30 ms`, Wolfram independently gives:

- activation integral for each individual Gesture: `0.15 s`
- activation squared integral for each individual Gesture: `0.1422857142857143 s`
- sequential overlap integral: `0`
- sequential normalized overlap coefficient: `0`
- overlap overlap integral: `0.03 s`
- overlap normalized coefficient: `0.2108433734939759`
- 5 ms linear-interpolation max-absolute-error bound: `0.020833333333333336`
- 2.5 ms bound: `0.005208333333333334`

The checked-in `wolfram/coordination_oracle.wl` is the independent derivation; JSON contains the numeric reference consumed by Python.

## Hypotheses

### H1 — semantic overlap

The sequential condition reconstructs zero simultaneous activation while the overlap condition reconstructs a positive overlap consistent with the Wolfram oracle.

### H2 — physical interaction

During the overlap interval, the realized geometry contains simultaneous constrictions at both target locations. The sequential condition never contains that combined state.

### H3 — acoustic consequence

The sequential and overlap conditions produce a reproducible raw-waveform difference under otherwise fixed conditions.

### H4 — effect exceeds tested discretization artifact

The sequential-vs-overlap normalized RMS waveform difference exceeds both:

- `0.01`; and
- five times the larger candidate-vs-reference discretization difference of the two main conditions.

The factor-of-five gate is preregistered as a discrimination margin for this fixture, not as a perceptual threshold.

### H5 — morphology-independent timing semantics

The relative timing representation contains no body-specific section indices, physical state, or acoustic parameters. Normalized locations remain Gesture semantics; backend section selection remains a realization concern.

## Measurements

### Gesture / coordination

- analytic and reconstructed activation for A and B
- individual activation integrals
- simultaneous-active duration
- overlap integral
- normalized overlap coefficient
- maximum activation interpolation error against analytic envelopes

### Physical state

- realized area at A location
- realized area at B location
- duration for which both locations are simultaneously below rest area
- realization feasibility / unsupported / invalid status

### Acoustics

- raw pressure waveform
- listening-normalized WAV
- normalized RMS sequential-vs-overlap waveform difference
- per-frame transfer magnitudes at 500, 1500 and 2500 Hz

### Numerical robustness

Each main condition is rendered at:

- candidate: 5 ms control grid / hop 256
- reference: 2.5 ms control grid / hop 128

Candidate-vs-reference normalized RMS difference is reported separately from the coordination effect.

## Decision rule

### ADOPT

All must hold:

- all outputs are finite;
- reconstructed activation errors stay within Wolfram bounds;
- sequential normalized overlap is effectively zero;
- overlap normalized overlap agrees with the oracle within `1e-3`;
- the overlap condition contains a nonzero simultaneous two-location physical constriction interval;
- the sequential condition contains no such interval;
- sequential-vs-overlap waveform difference is `> 0.01`;
- sequential-vs-overlap difference is `> 5 × max(discretization differences)`;
- no result depends on same-section overwrite or Gesture tuple priority.

An ADOPT result supports designing an explicit compiler-side `CoordinationPlan` candidate. It does **not** establish a general coarticulation model or production coordination API.

### MORE_DATA

Use when physical coordination is represented correctly but acoustic separation is not robust against the tested discretization, or when the quasi-stationary renderer is insufficient to interpret the result.

### REJECT

Use when the proposed overlap representation fails to produce an independent simultaneous physical state, or the apparent effect is only an implementation-order/backend artifact.

## Outputs

```bash
python experiments/011_gesture_coordination_overlap/run.py \
  --output-dir experiment-011-output
```

Expected outputs:

- `summary.csv`
- `decision.json`
- `*_trace.csv`
- `*_raw_pressure_pa.npy`
- `*_listen.wav`

## Creator evaluation

Creator listening is intentionally separate from the scientific decision. After artifacts exist, blinded A/B listening should record:

- whether the motion sounds like separate events or one continuous transition;
- whether an unnatural discontinuity is audible;
- whether the difference appears useful as a creative control.

Preference does not substitute for physical/numerical validity.

## Scope boundary

This experiment does not claim:

- linguistic correctness;
- phoneme or mora compilation;
- general coarticulation;
- articulator competition or task-dynamic control laws;
- true moving-boundary time-domain acoustics;
- anatomical derivation;
- source-filter back-coupling;
- a production coordination API.
