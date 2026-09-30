# Experiment 010 — minimal dynamic gesture → waveform comparison (M3)

## Research question

Can the temporal representation adopted by Experiment 008 — **explicit onset/offset events plus a sampled continuous trajectory** — drive a minimal time-varying physical/acoustic rendering path such that changing only one motion parameter produces a reproducible waveform difference, while morphology effects remain separately observable?

This experiment is the implementation vehicle for M3. It does **not** promote a production temporal API.

## Hypotheses

- **H1 — motion intervention:** with body, source, onset/offset, target area and acoustic assumptions fixed, changing only gesture ramp duration (`30 ms` vs `90 ms`) changes the physical area trajectory and resulting waveform for both prepared bodies.
- **H2 — morphology intervention:** holding the motion trajectory fixed while changing prepared morphology produces a waveform difference for both motion cases.
- **H3 — temporal reconstruction:** 5 ms sampled smoothstep trajectories, with explicit event semantics, stay inside the independent Wolfram linear-interpolation error bound.
- **H4 — numerical stability:** halving both the control sampling interval (`5 → 2.5 ms`) and short-time filtering hop (`256 → 128` samples) does not materially change the rendered waveform under the preregistered normalized-RMS threshold.

## Fixed conditions

- sample rate: 48 kHz
- duration: 0.50 s
- deterministic harmonic inlet volume-velocity source: F0 = 100 Hz, 40 harmonics
- source peak volume velocity: `1e-5 m^3/s`
- gesture onset / offset: `0.08 / 0.42 s`
- normalized constriction location: `0.55`
- target area: `5e-5 m^2`
- 10 × 17 mm serial 1D sections
- Experiment-009 acoustic assumptions: constant attenuation, small resistive terminal-load surrogate, free-field monopole observer proxy

## Interventions

### Motion axis

Only smoothstep attack/release duration changes:

- `fast`: 30 ms
- `slow`: 90 ms

The event times and final target are identical.

### Morphology axis

Two manually prepared rest geometries are reused as an explicit morphology intervention:

- `wide-body`: `3e-4 m^2` rest area
- `narrow-body`: `2e-4 m^2` rest area

## Temporal representation

The experiment keeps onset and offset as exact events. Continuous activation is sampled on a control grid and linearly reconstructed only inside the active interval. The 5 ms grid is the tested candidate; 2.5 ms is used in the discretization comparison.

The smoothstep is

`S(x) = 3 x^2 - 2 x^3`.

For a ramp of duration `T`, `max |d²S/dt²| = 6/T²`, so linear interpolation on spacing `h` has the standard bound

`max error <= (6/8) (h/T)^2`.

`wolfram/activation_oracle.wl` evaluates these facts independently and the checked-in JSON records the numeric bounds used by the Python experiment.

## Physical / acoustic execution

At every short-time frame center:

1. reconstruct activation from the event + sampled-trajectory representation;
2. map activation to an experiment-local effective CONSTRICT target;
3. run the existing `Tract1DRealizer` / `simulate_snapshot` path to obtain the physical state;
4. derive the Experiment-009 source-to-observer transfer for that realized state;
5. apply it to the source frame and overlap-add the result.

This is deliberately a **quasi-stationary time-varying filter**. It does **not** carry acoustic wave state from frame to frame and therefore is not a true time-domain acoustic propagation model or FSI simulation. That distinction is part of the result, not hidden implementation detail.

## Preregistered measurements

For each `body × motion` condition:

- activation and realized area trace;
- raw pressure waveform in Pa;
- separately normalized listening WAV;
- raw peak and RMS pressure;
- normalized RMS difference against the finer control/hop rendering.

Across conditions:

- same-body `fast` vs `slow` normalized RMS waveform difference;
- same-motion `wide-body` vs `narrow-body` normalized RMS waveform difference;
- observed activation reconstruction error vs Wolfram bound;
- finite/non-finite output checks.

## Decision rule

`SUPPORTED` requires all of the following:

- all waveform samples are finite;
- both bodies show `fast` vs `slow` normalized RMS difference > 0.01;
- both motions show `wide-body` vs `narrow-body` normalized RMS difference > 0.01;
- every 5 ms / hop-256 rendering differs from its 2.5 ms / hop-128 reference by normalized RMS < 0.20;
- observed activation reconstruction errors remain within the Wolfram bounds.

Failure of a scientific effect or discretization criterion yields `MORE_DATA`. Non-finite output or violation of the independent activation bound is an execution failure.

These thresholds are discriminating gates for this minimal fixture, not perceptual-quality guarantees.

## Outputs

```bash
python experiments/010_dynamic_gesture_waveform/run.py \
  --output-dir experiment-010-output
```

The output directory contains:

- `summary.csv`
- `decision.json`
- `*_trace.csv`
- `*_raw_pressure_pa.npy`
- `*_listen.wav`

Raw pressure and normalized listening audio are intentionally distinct.

## Scope boundary

This experiment does not claim:

- anatomical derivation of the prepared tracts;
- self-oscillating vocal folds;
- source-filter back-coupling;
- true time-domain propagation through a moving tract;
- general gesture overlap / coarticulation;
- general emotion or arbitrary text-to-speech;
- a production temporal API.

A positive result supports the minimal dynamic capability needed to design X1b. It does not by itself define the future Studio control mapping.
