# Experiment 009 — fixed-tract waveform generation

Issue: #8 (M2)

## Question

Can an explicitly specified periodic source excite two manually prepared fixed
tracts and produce finite, reproducible pressure waveforms whose differences
come from the tract model rather than listening normalization?

This experiment is the first waveform-producing step. It does **not** claim a
realistic human voice, anatomically derived geometry, self-oscillating vocal
folds, or a final radiation model.

## Pre-registered hypothesis

1. A deterministic harmonic inlet volume-velocity source can be propagated
   through a fixed segmented 1D tract to a finite observer pressure waveform.
2. For the uniform tract, resonant peaks from the Python segmented composition
   agree within 0.5 Hz with an independent Wolfram closed-form uniform-tube
   reference evaluated on the same 0.25 Hz scan grid.
3. Replacing one fixed section with a constricted section changes resonant peak
   locations by at least 10 Hz, so the comparison is not merely a level change.
4. Raw pressure in Pa remains separate from per-file listening normalization.

If (2) or (3) fails, the decision is `MORE_DATA`, not a hidden post-hoc tuning
of the acceptance criterion.

## Fixed conditions

- sample rate: 48 kHz
- duration: 0.5 s
- source F0: 100 Hz
- source: deterministic harmonic volume-velocity series, harmonics 1..40,
  amplitude proportional to `h^-1.2`
- source peak volume velocity: `1e-5 m^3/s`
- source onset/release listening ramp: 10 ms
- air density: `1.21 kg/m^3`
- sound speed: `343 m/s`
- experiment-local attenuation: `0.4 Np/m`
- terminal load: real `0.05 * Zc_out`
- observer distance: 0.20 m
- body length: 0.17 m in both cases

The two bodies are manually prepared numerical geometries:

- `uniform`: ten 17 mm sections, each `3e-4 m^2`;
- `constricted`: same tract except section 6 is `8e-5 m^2`.

No anatomical derivation is implied.

## Source-to-output derivation

The experiment keeps the existing state convention

```text
[p_in]   [A B] [p_out]
[U_in] = [C D] [U_out]
```

with `exp(+j omega t)`.

For an explicit terminal load

```text
p_out = Z_L U_out
```

we obtain

```text
U_in = (C Z_L + D) U_out

U_out / U_in = 1 / (C Z_L + D)
```

This is the transfer used for synthesis. **Input impedance is not used as an
audio transfer filter.**

Each experiment-local tube section uses

```text
k_complex = omega / c - j alpha
Zc        = rho c / S

T = [[cos(kL),      j Zc sin(kL)],
     [j sin(kL)/Zc,    cos(kL)   ]]
```

where `alpha = 0.4 Np/m` is a deliberately simple constant attenuation
hypothesis. This loss model is not promoted to Fidelity 0.

Observer pressure is then approximated separately as a free-field monopole
proxy driven by outlet volume velocity:

```text
P_obs / U_out = j omega rho exp(-j k r) / (4 pi r)
```

The small terminal resistance and the observer radiation formula are separate
experiment assumptions. The observer does not feed back into the terminal
load. This is intentionally simpler than physical lip radiation.

## Independent Wolfram check

`wolfram/uniform_reference.wl` does **not** reproduce the Python ten-section
matrix loop. It evaluates the closed-form denominator of one uniform tube:

```text
H(f) = 1 / [ cos(k_complex L)
             + j (Z_L/Zc) sin(k_complex L) ]
```

and searches a 100–5000 Hz grid at 0.25 Hz spacing.

Recorded first five maxima:

| rank | Wolfram frequency (Hz) |
|---:|---:|
| 1 | 504.50 |
| 2 | 1513.25 |
| 3 | 2522.00 |
| 4 | 3531.00 |
| 5 | 4539.75 |

The Python experiment must reproduce each within 0.5 Hz before the workflow is
accepted.

The Wolfram acoustic documentation separately confirms the use of acoustic
pressure wave equations, impedance boundaries, and time/frequency-domain
modeling; see:

- https://reference.wolfram.com/language/ref/AcousticPDEComponent
- https://reference.wolfram.com/language/ref/AcousticImpedanceValue
- https://reference.wolfram.com/language/PDEModels/tutorial/Acoustics/AcousticsTimeDomain

These documentation sources support the modeling concepts; the numerical peak
values above come from the committed Wolfram script and its recorded output.

## Outputs

Run:

```bash
python experiments/009_fixed_tract_waveform/run.py --output-dir experiment-009-output
```

The output directory contains:

- `uniform_raw_pressure.csv`, `constricted_raw_pressure.csv` — pressure in Pa;
- `*_raw_pressure_pa.npy` — raw floating-point pressure arrays;
- `*_listen.wav` — independently peak-normalized listening copies;
- `summary.csv` — raw peak/RMS pressure and listening gain;
- `spectral_peaks.csv` — source-to-outlet transfer maxima;
- `metadata.json` — source, loss, boundary, body and environment provenance;
- `decision.json` — independent-reference errors and the `SUPPORTED` /
  `MORE_DATA` decision.

## Raw output versus listening output

The WAV files are normalized to 0.90 full scale **per file**. They therefore
must not be used to infer physical loudness differences between bodies.

Physical comparison uses the raw Pa arrays and transfer response. The listening
WAVs answer only: “is the generated waveform audible and qualitatively
different?”

## Failure checks

The run fails rather than hiding the result when:

- any pressure sample is non-finite;
- the source is silent or non-finite;
- the uniform transfer does not expose the expected five peaks;
- any uniform peak misses the Wolfram reference by more than 0.5 Hz;
- the body intervention fails the pre-registered 10 Hz peak-shift criterion.

No clipping or limiter is applied to the raw pressure result.

## Decision boundary

A `SUPPORTED` result means only that this **experiment-local** path is suitable
to proceed toward M3/X1:

```text
explicit source
→ fixed tract
→ source-to-output transfer
→ raw observer pressure
→ listening WAV
```

It does not promote the loss or radiation approximations into the universal
kernel. Any later core API change requires separate evidence.
