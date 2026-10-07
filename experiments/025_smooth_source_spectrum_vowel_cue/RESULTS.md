# Experiment 025 results — smooth source-spectrum vowel cue

Issue: #55

## Current decision

**SMOOTH_SOURCE_DIAGNOSTIC_READY_FOR_LISTENING**

The preregistered objective Gate passed. No human decision is recorded yet.

## Provenance

- GitHub Actions run: 37553098145
- branch: `v1b-smooth-source-spectrum`
- source commit: `25a9046773015946fc21fe4f8240b820ed1f614b`
- full output artifact ID: `11453931273`
- full output digest: `sha256:fd3644cd60d67764272982f7ca924a19a136df8cf8f3746d91de2dea585648e5`
- public blind-listening artifact ID: `11454125625`
- public blind-listening digest: `sha256:b2ec2d19d149fd37a18a8ec5ff12f987ce48e192c91e36696930d83821b8be0e`

## Objective Gate

### Tract oracle

PASS.

All 15 checked Arai /a i u/ tract peaks remain exactly equal to the checked-in Experiment-023 oracle on the 0.25 Hz scan grid.

### Source oracle

PASS.

Maximum source harmonic-ratio error against the independent Wolfram oracle is below `6e-14 dB`.

### Cycle-boundary artifact

PASS.

- S0 LF baseline: `4.4062e-05`
- S2 cos/n² diagnostic: **`0.0047490`**
- frozen requirement: **< 0.01**

Independent Wolfram pre-implementation prediction for S2 was `0.0047014`.

### Rendered vowel cue

S0 P2/P1:

- /a/: -10.5463 dB
- /i/: -28.7989 dB
- /u/: -23.5550 dB

S2 P2/P1:

- /a/: -6.0487 dB
- /i/: **-14.9687 dB**
- /u/: -14.8911 dB

For /i/:

- improvement: **+13.8302 dB**
- frozen requirement: **>= +10 dB**
- result: PASS

The pre-implementation Wolfram prediction was approximately +14.9241 dB.

### Other objective checks

- rendered oracle tolerance: PASS under the preregistered 2.5 dB engineering tolerance;
- startup artifact: PASS;
- all outputs finite: PASS;
- listening level match: PASS;
- steady-RMS spread: `5.55e-17`;
- no clipping.

## Human Gate

A fresh blind set uses seed 25025:

- 10 /a/
- 10 /i/
- 10 /u/
- choices: a / i / u / UNIDENTIFIABLE

Response semantics are explicit:

> If two vowels seem mixed and neither is clearly primary, choose UNIDENTIFIABLE.

Frozen Gate:

- each vowel >=8/10;
- total >=24/30;
- no previously passing vowel may fall below 8/10.

Voice quality is evaluated separately from categorical identity.

## Claim boundary

Objective success supports the narrow claim that a smoother source-spectrum intervention can preserve materially more /i/ high-F2 support while satisfying the existing source-artifact Gate.

It does **not** establish:
- biological vocal-fold realism;
- human perceptual rescue;
- general Japanese vowel synthesis;
- readiness for #32.

Human listening remains required before deciding #55.
