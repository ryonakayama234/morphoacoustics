# Experiment 013 results — parametric source / prosody ablation

## Objective decision

**`PARAMETRIC_CONTROLS_VALIDATED`** under the preregistered H1–H4 numeric gates.

This decision means that the experiment-local LF-family source, macroprosodic trajectories, and the explicit micro/aspiration probe were generated deterministically and survived the predefined numerical checks.  It does **not** mean that any condition has been shown perceptually natural, that the aspiration probe is production-ready, or that a self-oscillating vocal-fold model is unnecessary.

## H1 — LF pulse-shape capability: PASS

For `Rd = 1`, the Python LF implementation matched the independent Wolfram oracle:

- `Ra = 0.038`
- `Rk = 0.342`
- `Rg = 1.0322844169071468`
- `Tp/T0 = 0.4843626347650026`
- `Te/T0 = 0.6500146558546335`
- `Ta/T0 = 0.038`
- `alpha*T0 = 2.806613596144194`
- normalized net derivative integral: `-6.94e-16`

The maximum oracle discrepancy in the checked quantities was about `4e-15`.

For `lf_fixed`:

- cycle-boundary jump / source RMS: `4.41e-5` (`< 0.01` gate)
- fixed-tract startup peak / steady RMS: `2.766` (`< 20` gate)
- fixed-tract output: finite

The LF source has a stronger legitimate within-cycle excitation than the deliberately smooth Experiment-012 source.  Its fixed-tract pitch-phase peak ratio was `5.64` versus `2.17` for `smooth_fixed`; this quantity was preregistered as diagnostic only, not an LF rejection criterion.

## H2 — macroprosody realization: PASS

Adding the preregistered macroprosody trajectory produced the intended nonstationarity without a renderer-startup regression.

### F0 and envelope tracking

- F0 trajectory RMS error: `1.54e-8 Hz`
- normalized 20 ms source-RMS envelope correlation: `0.9822`
- fixed 10 ms lag correlation:
  - `lf_fixed`: `1.0000`
  - `lf_macroprosody`: `0.9728`
- steady source RMS-envelope CV:
  - `lf_fixed`: approximately `0`
  - `lf_macroprosody`: `0.0997`

### Preregistered boundary cue

Using the fixed windows:

- pre-boundary mean F0: `96.75 Hz`
- post-boundary mean F0: `104.87 Hz`
- F0 reset: `+8.12 Hz` (`>= 5 Hz` gate)
- boundary RMS / mean(pre, post RMS): `0.738` (`<= 0.8` gate)

Fixed-tract startup peak / steady RMS remained `2.478`, well below the `< 20` gate.

This validates control realization only.  Whether the reset is perceived as a useful word/phrase boundary is reserved for blinded listening.

## H3 — microprosody / aspiration realization: PASS, with an important acoustic warning

At the **source** level, the C3 intervention behaved as intended:

- aspiration-noise RMS / total source RMS: `0.0247`
- spectral flatness:
  - C2: `8.77e-7`
  - C3: `3.85e-4`
- cycle-boundary jump / RMS: `5.26e-4` (`< 0.01` gate)
- F0 RMS error: `5.05e-6 Hz`
- envelope correlation: `0.9815`
- output remained finite

However, the fixed-tract render exposed a major limitation of the **white inlet-noise probe**:

- C2 fixed-tract energy >= 2 kHz: `0.00151`
- C3 fixed-tract energy >= 2 kHz: `0.97907`
- C2 fixed-tract max derivative / RMS: `12,123`
- C3 fixed-tract max derivative / RMS: `581,521`

This is not a preregistered H3 failure because the H3 gate deliberately asked whether explicit aperiodicity could be introduced without cycle-boundary discontinuity and while preserving the planned macro controls.  But it is strong evidence that **unshaped white aspiration noise injected as inlet volume velocity is not a suitable production aspiration model** under the current acoustic/radiation surrogate.

Experiment 009's far-field pressure surrogate includes an explicit factor proportional to angular frequency in the monopole-radiation term.  Broad-band inlet noise is therefore strongly high-frequency weighted downstream.  The C3 result must be treated as an aperiodicity stress/probe, not as a candidate voice source to promote.

A later aspiration study should separate at least spectral shaping / bandwidth and physical source placement.  This can be done before deciding whether a reduced self-oscillating vocal-fold model is needed.

## H4 — oral coordination retention: PASS

Under C3:

- sequential-vs-overlap normalized RMS difference: `0.5473`
- candidate/reference discretization difference:
  - sequential: `0.03306`
  - overlap: `0.02878`
- effect / maximum discretization perturbation: approximately `16.6x`

The existing `> 0.01` and `> 5x` gates both pass, and all outputs are finite.

As in Experiment 012, this numerical effect size is not a naturalness score and should not be compared directly across different source conditions as if it were perceptual magnitude.

## What the objective result tells us

The experiment now establishes three separate facts under the current model class:

```text
LF pulse shape
    -> can be generated continuously and reproducibly

macroprosodic F0 / amplitude / boundary controls
    -> can be realized accurately and measurably break perfect stationarity

small explicit white aspiration probe
    -> introduces aperiodicity at the source,
       but is severely over-emphasized by the current downstream acoustic surrogate
```

Therefore the next scientific decision depends on human listening of at least C0–C2.  We should not jump to a two-mass model merely because the Experiment-012 smooth baseline sounded like a buzzer; macroprosody has now been added as an independently controlled intervention and has not yet been perceptually evaluated.

## Human follow-up

Freeze these numeric results before listening.

Prepare blinded listening renders of the same sequential oral condition:

- C0 `smooth_fixed`
- C1 `lf_fixed`
- C2 `lf_macroprosody`

C3 may be supplied as a separate diagnostic sample, but its strong high-frequency-noise amplification must not be interpreted as a fair test of “microvariation makes speech natural”.

Ask separately:

- click/snap present?
- alarm/buzzer-like vs voice-like?
- does C1 pulse shape change voice-likeness without prosody?
- does C2 restore useful fluctuation and a boundary impression?
- is the variation controlled or does it sound like artificial wobble?

Only after that perceptual result should we choose between:

1. refining the parametric/prosodic path;
2. separately repairing aspiration-noise modeling;
3. opening a matched reduced self-oscillating source experiment.

## Scope reminder

No production `PHONATE`, `PRESSURIZE`, `ProsodyPlan`, source backend, Studio UI, or self-oscillating model is promoted by Experiment 013 alone.
