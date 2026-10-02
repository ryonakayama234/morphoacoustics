# Experiment 015 results — static vowel calibration objective gate

Issue: #31

## Current decision

**ACOUSTIC_VOWEL_FIXTURE_VALIDATED_AWAITING_LISTENING**

The preregistered objective gate passed for the published Arai /a i u/ plate-model fixtures under the current low-fidelity acoustic path.

This establishes only that:

- the published 16-section fixtures were reproduced deterministically;
- the Python transfer response matches the independent Wolfram oracle;
- the /a i u/ low-order resonance patterns remain separated under the preregistered 32-section regrid perturbation;
- the inherited LF source / renderer artifact gates pass;
- level-matched blinded listening stimuli were generated without clipping.

It does **not** establish that the outputs are perceived as /a/, /i/, and /u/. The primary blinded human gate remains outstanding.

## Provenance

Successful objective CI run:

- GitHub Actions run: 37069840637
- branch: `v1-static-vowel-calibration`
- source commit: `53000ef5c835dac0d136808b1ccf51fae67eb5a4`
- full output artifact ID: `11254585474`
- full output artifact digest: `sha256:3bd01186376dccd3d874b8495a5a8ab557dcca50062a90dccc780f9828ce0608`
- primary blind-listening artifact ID: `11254460679`
- primary blind-listening artifact digest: `sha256:f38a6ca7bc7cb3d89a2fb9d9fb200909265253d1c902eaf9c11aa7439e81a1ed`

Repository tests also passed for the same PR head.

## Reference fixture

Primary fixtures use the Arai Laboratory plate-type Japanese-vowel model documented in PREREGISTRATION.md:

- 16 sections
- 10 mm per section
- published table order reversed from lips -> larynx to morphoacoustics glottis -> lips
- diameter converted to circular section area
- target vowels: /a/, /i/, /u/

The fixture remains an educational physical vocal-tract reference, not an MRI-derived population reference.

## Wolfram oracle agreement

All five checked primary response peaks for all three vowels matched the checked-in independent Wolfram values exactly on the 0.25 Hz scan grid.

| vowel | P1 Hz | P2 Hz | P3 Hz | P4 Hz | P5 Hz |
|---|---:|---:|---:|---:|---:|
| /a/ | 720.25 | 1288.50 | 2918.25 | 4196.00 | 4657.25 |
| /i/ | 281.25 | 2309.25 | 3212.00 | 4102.00 | 4899.25 |
| /u/ | 419.25 | 1481.75 | 3106.50 | 3892.75 | 4580.25 |

Preregistered tolerance: <= 0.5 Hz.

Observed absolute error: 0.0 Hz for all 15 peaks.

The inherited Experiment-013 LF parameter oracle also passed; the largest reported numerical difference was the LF alpha root at approximately `4.0e-15`.

## Spatial-discretization sensitivity

The preregistered perturbation linearly regrids the 16 diameter samples at 10 mm cell centers to 32 diameter samples at 5 mm cell centers with endpoint clamping.

Refined P1/P2:

| vowel | refined P1 Hz | refined P2 Hz | primary->refined P1/P2 displacement |
|---|---:|---:|---:|
| /a/ | 733.50 | 1333.50 | 46.9102 Hz |
| /i/ | 288.75 | 2334.50 | 26.3403 Hz |
| /u/ | 429.25 | 1526.00 | 45.3659 Hz |

Primary between-vowel P1/P2 distances:

- /a/ vs /i/: 1111.1488 Hz
- /a/ vs /u/: 357.6962 Hz
- /i/ vs /u/: 838.9280 Hz

Therefore:

- minimum between-vowel distance: 357.6962 Hz
- maximum primary-vs-refined displacement: 46.9102 Hz
- separation / discretization ratio: **7.6251x**
- preregistered requirement: **> 5x**
- result: PASS

This is an engineering robustness result, not a psychoacoustic distance metric.

## Source and renderer artifact regression

The fixed LF-family source uses Rd=1 and F0=100 Hz.

Source cycle-boundary jump / RMS:

- observed: `4.4062e-05`
- limit: `0.01`
- result: PASS

Rendered startup peak / steady RMS:

| vowel | startup / steady RMS |
|---|---:|
| /a/ | 2.5599 |
| /i/ | 2.3419 |
| /u/ | 2.7332 |

Preregistered limit: < 20 for every vowel.

All pressure arrays were finite.

## Listening level control

Raw pressure is retained separately.

For listening only:

1. each vowel waveform is divided by its own steady-state RMS over 0.05–0.45 s;
2. one common safety gain is then applied across the three normalized waveforms;
3. the largest listening sample is constrained to 0.90 full scale.

Observed steady-state listening RMS spread across /a i u/: **0.0** within reported floating-point precision.

No listening waveform clipped.

This prevents overall level from being an intended primary vowel-identification cue while preserving spectral/temporal differences.

## Primary human gate now required

The generated blind set contains 30 coded WAV files:

- 10 /a/
- 10 /i/
- 10 /u/
- deterministic randomized order
- no label information in the public manifest
- blind key stored outside the primary listening artifact

For each trial answer one of:

- /a/
- /i/
- /u/
- UNIDENTIFIABLE

Separately record confidence, click/snap, voice-like vs alarm/buzzer-like, and optional notes.

Engineering pass criterion:

- each vowel >= 8/10
- total >= 24/30

The independent-unbiased three-choice chance references remain:

- P(X >= 8 of 10) ~= 0.00340395 for one vowel
- P(X >= 24 of 30) ~= 2.09016e-7 overall

These are not population-level p-values.

## Implementation correction before successful run

The first implementation attempted to require five response peaks below 5 kHz for the refined 32-section perturbation. The preregistered discretization gate uses only P1/P2. The refined /i/ fixture exposes only four local maxima below 5 kHz, so the run stopped before producing a scientific decision.

The code was corrected to require only the preregistered P1/P2 for the refined condition. No gate threshold, fixture, primary oracle, source condition, or human criterion was changed.

## Claim boundary

The strongest objective claim before human listening is:

> The current morphoacoustics acoustic path reproduces three published plate-model vowel tract fixtures with exact agreement to the independent transfer-response oracle on the chosen scan grid, preserves their low-order resonance separation beyond the preregistered discretization margin, and renders finite artifact-controlled level-matched listening stimuli.

Whether those stimuli actually carry vowel identity perceptually remains an empirical human question.

## Next branch

- human Gate passes -> SUPPORT_STATIC_VOWEL -> #32
- objective path valid but identification fails -> ACOUSTICS_VALID_PERCEPTION_FAILED
- do not introduce task-level Gesture realization until the perceptual result is known
