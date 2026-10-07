# Experiment 025 preregistration — smooth source-spectrum vowel cue

Issue: #55

## Question

Experiment 024 showed that changing only the excitation spectrum can raise the rendered /i/ high-F2 cue by more than 30 dB, but its phase-aligned `sin(n)/n` diagnostic source failed the preregistered source-artifact gate.

Experiment 025 asks whether a smoother periodic diagnostic source can retain at least +10 dB of the /i/ cue improvement while satisfying the existing cycle-boundary artifact threshold.

This remains a source-diagnosis experiment. It does not establish a biological laryngeal model.

## Fixed conditions

Unchanged from Experiments 023/024:

- Arai 16-section /a i u/ tract fixtures;
- F0 = 100 Hz;
- duration = 0.5 s;
- sample rate = 48 kHz;
- 40 source harmonics;
- same tract renderer, loss, radiation and observer path;
- same 10 ms file envelope;
- same steady-RMS listening normalization and common safety gain;
- no prosody, aspiration or neural processing.

S0 is the exact Experiment-023 LF baseline.

## Intervention

S2 is frozen before implementation as

```text
s(t) = sum_{n=1}^{40} cos(2*pi*n*F0*t) / n^2
```

followed by the same file envelope and peak normalization used by the existing source path.

The cosine phase family is selected because the derivative of every harmonic is zero at integer cycle boundaries. The 1/n^2 envelope is selected from the pre-implementation Wolfram sweep because it retains a comfortable margin on both the artifact and /i/ cue-improvement gates.

## Independent Wolfram predictions

Using the exact Experiment-013 cycle-boundary metric, 48 kHz sampling, 100 Hz F0, 0.5 s duration and 10 ms file envelope:

- predicted S2 cycle-boundary jump/RMS: 0.0047014357;
- required: < 0.01.

Predicted rendered P2/P1 ratios, after the existing frequency-proportional observer:

| vowel | harmonic pair | source ratio dB | observer dB | tract dB | predicted rendered dB |
|---|---|---:|---:|---:|---:|
| /a/ | 7 -> 13 | -10.7538 | +5.3769 | +1.3340 | -4.0429 |
| /i/ | 3 -> 23 | -35.3843 | +17.6921 | +3.8173 | -13.8748 |
| /u/ | 4 -> 15 | -22.9613 | +11.4806 | -3.2705 | -14.7511 |

Relative to Experiment-024 S0 /i/ rendered ratio (-28.7989 dB), the analytic prediction is approximately **+14.9241 dB improvement**.

## Objective Gate

All must pass before human listening:

1. Experiment-023 tract oracle remains unchanged and passes.
2. S0 reproduces the existing LF baseline.
3. S2 source harmonic ratios match the checked-in Wolfram oracle within 0.25 dB.
4. S2 rendered P2/P1 ratios match the analytic observer/tract oracle within **2.5 dB**.
   - This tolerance is frozen before Experiment-025 execution.
   - It is intentionally widened from 2.0 dB because Experiment 024 already observed a 2.0047 dB /a/ mismatch under the simplified analytic observer prediction.
5. /i/ S2 rendered P2/P1 improves by at least +10 dB relative to S0.
6. cycle-boundary jump/RMS < 0.01 for both S0 and S2.
7. startup peak / steady RMS < 20.
8. all rendered outputs finite.
9. listening normalization produces no clipping and <=1e-12 steady-RMS spread.

If any objective criterion fails, do not use the blind listening set.

## Human Gate if objective Gate passes

Generate a fresh deterministic blind set using seed 25025:

- 10 /a/, 10 /i/, 10 /u/;
- choices: a / i / u / UNIDENTIFIABLE;
- explicit instruction: if two categories seem mixed and no single category is preferred, choose UNIDENTIFIABLE;
- no correctness feedback.

Gate:

- each vowel >= 8/10;
- overall >= 24/30;
- no previously passing vowel may fall below 8/10.

Voice quality is recorded separately from categorical identity.

## Decision

- objective fail -> retain source-spectrum hypothesis but revise the diagnostic source without human listening;
- objective pass + human pass -> source/excitation limitation is supported; next select a physically interpretable source strategy and reconfirm before #32;
- objective pass + human fail -> source spectrum alone is insufficient; investigate radiation/observer/reference-fixture fit.

No threshold may be changed after Experiment 025 output exists.
