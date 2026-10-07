# Experiment 025 — smooth source-spectrum vowel-cue diagnostic

Issue: #55

## Motivation

Experiment 024 showed that a source-only spectral intervention changed the /i/ rendered P2/P1 cue by +31.52 dB, but its 1/n sine-phase source failed the frozen cycle-boundary artifact limit. Experiment 024 remains failed and is not reinterpreted.

Experiment 025 asks whether a smoother periodic diagnostic source can retain at least +10 dB of /i/ cue improvement while satisfying the same artifact limit.

## Fixed variables

Keep Experiment 024/023 values unchanged:
- Arai /a i u/ tracts;
- 48 kHz, 0.5 s, F0=100 Hz;
- acoustic backend, observer conversion and frame renderer;
- steady analysis window 0.05–0.45 s;
- listening normalization;
- startup limit <20;
- cycle-boundary jump/RMS <0.01;
- human categories and thresholds.

No geometry, prosody, Gesture, neural, material or /u/ quality intervention.

## Conditions

S0: exact LF baseline from Experiment 023/024.

S2: deterministic 40-harmonic diagnostic source

```text
s(t) = envelope(t) * Sum[Cos(2*pi*n*F0*t)/n^2, n=1..40]
```

Use the same file envelope and peak normalization.

S2 is diagnostic only.

## Independent magnitude oracle

Nearest P1/P2 harmonics remain /a/ {7,13}, /i/ {3,23}, /u/ {4,15}.

For S2, source P2/P1 amplitude ratio is 40 log10(n1/n2):

- /a/: -10.75381249 dB
- /i/: -35.38426325 dB
- /u/: -22.96125071 dB

Frozen S0 source ratios from Experiment 024:

- /a/: -15.24544121 dB
- /i/: -49.21473174 dB
- /u/: -31.62084988 dB

Therefore the predicted source-only cue changes are:

- /a/: +4.49162872 dB
- /i/: +13.83046849 dB
- /u/: +8.65959917 dB

Because tract and renderer are unchanged, the primary differential oracle is:

```text
delta rendered P2/P1 == delta source P2/P1
```

within a frozen tolerance of 0.5 dB for each vowel.

## Objective Gate

All must pass before listening:

1. S0 reproduces the existing baseline path.
2. S2 uses exactly 40 cosine harmonics with amplitude 1/n^2 before envelope/normalization.
3. S2 source P2/P1 ratios agree with Wolfram within 0.25 dB.
4. S2 cycle-boundary jump/RMS <0.01.
5. S2 /i/ rendered P2/P1 improves by at least +10 dB versus S0.
6. For every vowel, rendered cue change versus S0 matches source cue change within 0.5 dB.
7. tract oracle remains unchanged.
8. rendered startup/steady RMS <20 for every vowel.
9. finite outputs and no clipping.
10. the same listening normalization is used for all S2 vowels.
11. /a/ and /u/ remain untuned controls.

Objective success means only `SMOOTH_SOURCE_DIAGNOSTIC_READY_FOR_LISTENING`.

## Human Gate

Fresh S2-only blind set, seed 25025:
- 10 trials each /a i u/;
- every vowel >=8/10;
- overall >=24/30;
- blind key excluded from public artifact.

Identity and voice quality are reported separately.

## Decision

- objective + human pass: SOURCE_SPECTRUM_HYPOTHESIS_SUPPORTED_DIAGNOSTICALLY; next replace S2 with a physically interpretable source strategy before #32.
- objective pass, human fail: SOURCE_SPECTRUM_ACOUSTIC_EFFECT_ONLY.
- objective fail: SMOOTH_SOURCE_DIAGNOSTIC_FAILED.

