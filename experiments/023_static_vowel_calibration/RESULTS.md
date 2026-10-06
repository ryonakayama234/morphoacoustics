# Experiment 023 results — static vowel calibration

Issue: #31

Migration note: the scientific execution originally lived on an older branch as `Experiment 015`. Current `main` later assigned experiment number 015 to the Embodiment measurement calibration track, so this completed vowel-calibration record is ported to **Experiment 023** without changing the frozen scientific inputs, thresholds, blind responses, or decoded outcome. The original run/artifact IDs below remain authoritative provenance for the human gate.

## Current decision

**ACOUSTICS_VALID_PERCEPTION_FAILED**

The preregistered objective gate passed, but the blinded human gate did not: overall identification was 27/30, while /i/ reached only 7/10 and therefore missed the preregistered per-vowel threshold of >=8/10.

This establishes that:

- the published 16-section fixtures were reproduced deterministically;
- the Python transfer response matches the independent Wolfram oracle;
- the /a i u/ low-order resonance patterns remain separated under the preregistered 32-section regrid perturbation;
- the inherited LF source / renderer artifact gates pass;
- /a/ and /u/ were identified 10/10 in this single-listener engineering gate;
- the current complete source/filter/rendering path does **not** yet satisfy the frozen three-vowel perceptual criterion because /i/ was identified 7/10.

The failed per-vowel gate is not relaxed post hoc. This revision does not proceed to #32.

## Provenance

Canonical completed objective run used for the human gate:

- GitHub Actions run: 37070023407
- branch: `v1-static-vowel-calibration`
- source commit: `4b9eacee8076b9cf285d24f79b6d6daa26d71449`
- full output artifact ID: `11254830785`
- full output artifact digest: `sha256:b3e520dca05dd59bb0faede7ddce8b739a25e9ddf6563a21da880ccca5371129`
- primary blind-listening artifact ID: `11255010363`
- primary blind-listening artifact digest: `sha256:24c57931f542e9b0264e6ea83cbf21ae137d6f7f07bdf96d2cc49f5bd3bb97b7`

Repository tests and the original Experiment 015 workflow passed for the same PR head. A later same-head workflow produced byte-identical uncompressed blind entries; the canonical human gate remained tied to the PR-body artifact above.

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

## Blinded human gate result

Responses were frozen in Issue #31 before the blind key was opened. Ambiguous notation was resolved before reveal: entries marked `u ?` counted as /u/ with low confidence; T08 (`i u 混ざった感じ`) was frozen as UNIDENTIFIABLE.

The exact decoded trial record is checked in as `human_gate.csv`.

Confusion matrix, rows = true class and columns = response `a / i / u / UNIDENTIFIABLE`:

| truth | a | i | u | UNIDENTIFIABLE | correct |
|---|---:|---:|---:|---:|---:|
| /a/ | 10 | 0 | 0 | 0 | **10/10** |
| /i/ | 0 | 7 | 1 | 2 | **7/10** |
| /u/ | 0 | 0 | 10 | 0 | **10/10** |

Overall: **27/30 = 90%**.

Preregistered gate:

- each vowel >=8/10: **FAIL** because /i/ = 7/10;
- total >=24/30: PASS.

Final decision: **ACOUSTICS_VALID_PERCEPTION_FAILED**.

The qualitative listener report ranked clarity as `a > i > u`: /a/ sounded clearly identifiable, /i/ reasonably identifiable, and /u/ noticeably lower in quality. This is importantly different from categorical accuracy: /u/ was nevertheless identified 10/10, while /i/ caused all three categorical errors. Therefore intelligibility/identity and voice quality must remain separate evaluation axes.

### Post-reveal diagnostic analysis

The /i/ failure has a concrete source/filter hypothesis worth testing before changing geometry.

Using the checked-in segmented-tube model, independent Wolfram evaluation at the nearest 100 Hz source harmonics gives the tract transfer ratio near P2 versus P1:

- /a/: +1.33 dB
- /i/: **+3.82 dB**
- /u/: -3.27 dB

But analysis of the rendered steady-state listening WAVs gives P2-near versus P1-near harmonic levels of approximately:

- /a/: -10.55 dB
- /i/: **-28.80 dB**
- /u/: -23.56 dB

For /i/, the tract itself therefore does not explain a weak P2 cue: the current complete rendering is approximately 32.6 dB lower at the 2.3 kHz source harmonic than at the 300 Hz harmonic after subtracting the tract-transfer ratio. This is consistent with the fixed LF-family source spectral tilt starving the high-F2 cue required by this /i/ fixture.

This is a **diagnostic hypothesis**, not a proven cause. The next experiment should change the excitation spectrum only while keeping vowel geometry, acoustic backend, observer/radiation, level normalization, and blind evaluation fixed.

The listener also hypothesized that /u/ quality may relate to stronger mouth/lip-shaping demands. The Arai fixture already contains both a mid-tract constriction and a narrower lip-end opening for /u/, so coarse lip narrowing is present in the current 1D geometry. A remaining /u/ quality gap could instead involve source spectrum, radiation, 3D/protrusion detail, or the difference between coarse tube opening and real articulatory lip configuration. Because /u/ categorical identification was 10/10, this quality question should not be conflated with the /i/ gate failure.

## Implementation correction before successful run

The first implementation attempted to require five response peaks below 5 kHz for the refined 32-section perturbation. The preregistered discretization gate uses only P1/P2. The refined /i/ fixture exposes only four local maxima below 5 kHz, so the run stopped before producing a scientific decision.

The code was corrected to require only the preregistered P1/P2 for the refined condition. No gate threshold, fixture, primary oracle, source condition, or human criterion was changed.

## Claim boundary

The strongest completed claim is:

> The current morphoacoustics acoustic path numerically reproduces three published plate-model vowel tract fixtures and yields strong but incomplete single-listener vowel identification under the frozen LF/rendering path: /a/ 10/10, /i/ 7/10, /u/ 10/10. Because /i/ missed the preregistered 8/10 per-vowel threshold, this revision does not establish the three-vowel perceptual capability required to proceed to continuous vowel motion.

This result supports a narrow follow-up on excitation-spectrum versus high-F2 cue availability rather than immediate expansion to Gesture realization, general TTS, or higher-fidelity anatomy.

## Next branch

- record this revision as **ACOUSTICS_VALID_PERCEPTION_FAILED**;
- do **not** start #32 yet;
- run a narrow V1b diagnostic holding tract geometry fixed and intervening on source spectral tilt / high-frequency excitation;
- only after the frozen three-vowel human gate is satisfied should #32 begin;
- keep /u/ voice-quality investigation separate from categorical vowel identity unless a later experiment links them.
