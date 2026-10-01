# Experiment 013 — parametric source / prosody ablation

Issue: #24

This experiment is preregistered before Python results are inspected.

## Why

Experiment 012 removed pitch-synchronous snap and renderer-startup artifacts, but the low-artifact smooth periodic source sounded buzzer/alarm-like in human listening and lost much of the perceived fluctuation / word-boundary impression.

R1 concluded that the next controlled question is not yet “1D tract vs 3D tract”.  We first isolate three upstream layers:

1. glottal pulse shape;
2. macroprosodic time variation;
3. small microprosody / aspiration.

No production API is changed in this experiment.

## Fixed context

- 48 kHz sample rate
- 0.50 s duration
- Experiment-012 one-frame preroll/crop renderer edge handling
- Experiment-009 segmented 1D tract acoustics
- Experiment-011 prepared morphology and oral coordination for listening / retention tests
- nominal base F0: 100 Hz
- common source peak normalization: `1e-5 m^3/s`
- deterministic seed for the only noise-bearing condition

## Conditions

### C0 `smooth_fixed`

Experiment-012 smooth nonnegative periodic flow surrogate:

- fixed F0 = 100 Hz
- open quotient = 0.6
- no macroprosody
- no noise

This is the current low-artifact buzzer baseline.

### C1 `lf_fixed`

LF-family glottal-flow source:

- `Rd = 1.0` (modal reference for this experiment)
- fixed F0 = 100 Hz
- fixed amplitude
- no macroprosody
- no noise

The Rd-to-R parameter mapping follows Fant-style relations:

```text
Ra = (-1 + 4.8 Rd) / 100
Rk = (22.4 + 11.8 Rd) / 100
Rg = 0.25 Rk (0.5 + 1.2 Rk) / (0.11 Rd - Ra (0.5 + 1.2 Rk))
Tp/T0 = 1 / (2 Rg)
Te/T0 = (Tp/T0) (1 + Rk)
Ta/T0 = Ra
```

The LF derivative uses an exponentially weighted sinusoidal open phase and exponential return phase.  Its cycle integral is constrained to zero; the flow waveform is obtained by integration and normalized to nonnegative unit peak before the common source scale is applied.

### C2 `lf_macroprosody`

Same LF source shape as C1 plus an explicit, experiment-local control trajectory.

This contour is **diagnostic**, not a claim about canonical Japanese intonation.

F0 contour is specified in semitones relative to 100 Hz using smooth interpolation between these anchors:

| time (s) | semitones |
|---:|---:|
| 0.00 | -0.2 |
| 0.05 | 0.0 |
| 0.14 | +0.8 |
| 0.22 | -0.6 |
| 0.25 | -0.8 |
| 0.285 | +0.9 |
| 0.38 | +0.2 |
| 0.47 | -0.7 |
| 0.50 | -0.8 |

The 0.25–0.285 s reset is the intended boundary cue.

Amplitude / voicing envelope anchors:

| time (s) | relative gain |
|---:|---:|
| 0.00 | 0.0 |
| 0.02 | 1.0 |
| 0.20 | 1.0 |
| 0.245 | 0.58 |
| 0.28 | 1.0 |
| 0.47 | 1.0 |
| 0.50 | 0.0 |

The boundary dip is deliberately incomplete; the test does not create an artificial silent word break.

### C3 `lf_macroprosody_micro`

C2 plus two separately identified small interventions:

- deterministic micro-F0 term: `0.08 sin(2π·7t) + 0.04 sin(2π·13t)` semitones;
- aspiration component: seeded Gaussian noise at 2% of the deterministic source peak before final common peak normalization, weighted by the square root of the instantaneous normalized glottal-flow opening.

These values are fixed before results.  They are experiment-local probes, not proposed production defaults.

## Rendering / comparisons

### Source-only

Measure every generated inlet-flow source directly.

### Fixed tract

Render all four sources through the same fixed uniform tract with Experiment-012 preroll edge handling.  This removes oral coordination as a confound.

### Listening render

Render all four sources through the **same Experiment-011 sequential oral condition**.  This is used only to make the perceptual comparison more informative; source/prosody condition remains the intervention.

### Existing coordination retention

Under C3, render Experiment-011 `sequential` and `overlap` at candidate and finer reference discretizations and verify that the established oral-coordination difference remains above discretization sensitivity.

## Independent Wolfram oracle

For `Rd = 1`, `F0 = 100 Hz`, Wolfram independently evaluated the Fant-style Rd mapping and LF open/return integral constraint.  Reference values are checked in `wolfram/lf_oracle.json`.

The Python implementation must reproduce the dimensionless mapping / root quantities within numerical tolerance.  The oracle does not provide listening judgments.

## Metrics

### Source metrics

- RMS / crest factor
- max absolute derivative / RMS
- energy fraction >= 2 kHz
- cycle-boundary jump / RMS
- fixed 10 ms lag correlation
- 20 ms RMS-envelope coefficient of variation
- deterministic/noise RMS ratio where applicable

### Fixed-tract metrics

- Experiment-012 fixed 100 Hz phase peak ratio (diagnostic only for LF)
- max derivative / RMS
- >=2 kHz energy ratio
- startup peak / steady RMS
- finite output

### Control-realization metrics

For C2/C3:

- instantaneous phase-derived F0 vs planned full F0 trajectory
- normalized 20 ms block RMS envelope vs planned amplitude envelope
- boundary cue deltas around the preregistered 0.25–0.285 s region

### Coordination-retention metrics

- sequential-vs-overlap normalized RMS difference
- candidate-vs-reference discretization difference for both conditions
- finite output

## Gates / interpretation

### H1 — pulse-shape capability

C1 must produce a valid LF flow with:

- oracle-consistent Rd mapping / integral constraint;
- negligible cycle-boundary discontinuity;
- finite fixed-tract output.

A larger legitimate within-cycle closure excitation is not itself classified as an artifact.

### H2 — macroprosody realization

C2 must:

- realize the planned F0 trajectory with numerical error <= 0.1 Hz RMS;
- produce nonzero envelope variation and a measurable boundary-aligned amplitude/F0 reset;
- reduce fixed-period stationarity relative to C1;
- remain finite and free of renderer-startup regression.

### H3 — micro/aspiration realization

C3 must:

- increase aperiodic/noise energy relative to C2;
- not introduce a material cycle/file-boundary jump;
- remain finite;
- preserve the macroprosody control trajectory.

### H4 — oral coordination survives

Under C3:

- sequential-vs-overlap normalized RMS difference remains `> 0.01`;
- effect remains `> 5x` the larger tested discretization difference;
- all compared outputs are finite.

## Human observation

Objective gates do not select a “natural” winner.

After the numeric result is frozen, prepare blinded listening candidates and ask separately:

- click/snap present?
- alarm/buzzer-like vs voice-like?
- useful fluctuation vs artificial wobble?
- intended boundary perceptible?
- oral coordination difference still useful?

## Scope exclusions

This experiment does not implement or claim:

- physiological vocal-fold tissue dynamics;
- a production LF/LFLM API;
- self-oscillating two-mass/body-cover vocal folds;
- source-filter back-coupling;
- canonical Japanese prosody;
- production `PHONATE` / `PRESSURIZE` parameter semantics.

If C1–C3 correctly realize their controls but remain consistently alarm-like in listening, the next study is a matched comparison against a reduced self-oscillating source (Experiment 014 candidate).
