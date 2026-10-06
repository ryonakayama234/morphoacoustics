# Experiment 024 — source-spectrum vowel-cue diagnostic

Issue: #55

## Question

Experiment 023 reproduced the Arai /a i u/ tract fixtures numerically, but the frozen blinded human gate produced /a/=10/10, /i/=7/10, /u/=10/10. Does the current fixed LF source under-excite the high-frequency harmonic support needed for the /i/ fixture's high second resonance?

This experiment is diagnostic. It does not promote a new production voice source.

## Hypothesis

H_V1B_SOURCE: holding tract geometry, acoustic backend, observer/radiation, F0, duration, listening normalization, and evaluation fixed, a source with stronger high-harmonic support will improve the acoustic cue available near /i/ P2 without changing the tract.

## Fixed variables

Reuse Experiment 023 without changing:

- Arai 16-section /a i u/ primary tract fixtures;
- sample rate 48 kHz;
- duration 0.5 s;
- F0 = 100 Hz;
- Experiment-009 loss/load/radiation formulation;
- Experiment-012 frame renderer and edge handling;
- observer and boundary assumptions;
- 0.05–0.45 s steady-state analysis window;
- per-stimulus steady-RMS normalization followed by one common safety gain;
- artifact limits: source cycle-boundary jump/RMS < 0.01 and rendered startup/steady RMS < 20;
- blind choices: a, i, u, UNIDENTIFIABLE.

No tract, prosody, aspiration, neural, Gesture, or material intervention is allowed.

## Source conditions

### S0 — baseline

Exact Experiment 023 source:

- Experiment-013 `lf_fixed`;
- Rd = 1;
- F0 = 100 Hz;
- same file envelope and source peak rule.

### S1 — diagnostic 1/n harmonic source

Construct a deterministic periodic diagnostic excitation

```text
s(t) = envelope(t) * sum[n=1..40] sin(2*pi*n*F0*t) / n
```

then apply the same Experiment-013 peak-normalization rule as S0.

This source is deliberately simple and non-biological. It exists only to intervene on spectral tilt while preserving F0, timing, duration, and determinism.

## Independent Wolfram oracle

For a source with harmonic amplitude A_n proportional to 1/n, using the source harmonics nearest the first two tract peaks:

| vowel | P1 harmonic | P2 harmonic | source P2/P1 dB | tract P2/P1 dB | predicted rendered P2/P1 dB |
|---|---:|---:|---:|---:|---:|
| /a/ | 7 | 13 | -5.3769 | +1.3340 | -4.0429 |
| /i/ | 3 | 23 | -17.6921 | +3.8173 | -13.8749 |
| /u/ | 4 | 15 | -11.4806 | -3.2705 | -14.7511 |

These are diagnostic harmonic-ratio expectations under the existing linear transfer model, not natural-speech targets.

Experiment 023 baseline rendered ratios were approximately:

- /a/: -10.55 dB
- /i/: -28.80 dB
- /u/: -23.56 dB

## Objective Gate

All conditions are frozen before human listening.

1. S0 reproduces the Experiment 023 source and rendered cue ratios within numerical tolerance.
2. S1 has finite samples, fixed 100 Hz F0, the same duration/envelope convention, and no stochastic component.
3. S1 source harmonic P2/P1 ratios agree with the Wolfram 1/n oracle within 0.25 dB.
4. Experiment 023 tract resonance oracle remains unchanged.
5. Under S1, rendered /i/ P2-near/P1-near improves by at least **+10 dB** relative to S0.
6. S1 rendered harmonic ratios agree with the linear source-plus-transfer oracle within 2 dB.
7. Source cycle-boundary jump/RMS < 0.01.
8. Rendered startup/steady RMS < 20 for every vowel.
9. All pressure/listening arrays are finite and no listening WAV clips.
10. The same steady-RMS normalization rule is used for /a i u/.
11. /a/ and /u/ remain control vowels; no result-dependent tuning of S1 is allowed.

Objective success yields only:

`SOURCE_SPECTRUM_DIAGNOSTIC_READY_FOR_LISTENING`

## Human Gate

Generate a fresh S1-only blinded set:

- 10 trials each of /a/, /i/, /u/;
- deterministic randomized order using a new frozen seed;
- no correctness feedback;
- blind key excluded from the public listening artifact.

Pass criterion:

- every vowel >= 8/10;
- overall >= 24/30.

Record categorical identity separately from voice quality. In particular, Experiment 023 showed that /u/ can be 10/10 identifiable while still sounding lower quality.

## Decision

### SOURCE_SPECTRUM_HYPOTHESIS_SUPPORTED

Use only if the objective Gate passes and S1 also passes the frozen human Gate. Then investigate a physically interpretable source/phonation parameterization that can provide the required excitation without treating S1 as a production source.

### SOURCE_SPECTRUM_ACOUSTIC_EFFECT_ONLY

Use if objective /i/ cue improvement occurs but blinded identity still fails.

### SOURCE_SPECTRUM_HYPOTHESIS_NOT_SUPPORTED

Use if the source-only intervention fails the objective cue-improvement Gate. Next investigate radiation/observer/reference-fixture assumptions rather than tuning the same source after seeing the result.

## Non-goals

- changing Arai geometry;
- fixing /u/ naturalness;
- moving-vowel synthesis;
- task-level Gesture realization;
- neural polish;
- general Japanese TTS.

# Provenance

Experiment 023 is the frozen baseline. Its negative perceptual result remains unchanged.
