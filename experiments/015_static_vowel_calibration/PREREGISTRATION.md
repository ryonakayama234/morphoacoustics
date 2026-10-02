# Experiment 015 — static vowel calibration

Issue: #31

## Question

Can the current low-fidelity morphoacoustics acoustic path turn three published Japanese-vowel tract fixtures into acoustically distinct outputs that are identifiable as /a/, /i/, and /u/ under blinded listening?

The claim is intentionally narrow. This experiment does not establish general Japanese phonology, motor realization, naturalness, or production-ready vowel synthesis.

## Reference fixture

Use the plate-type vocal-tract model published by Arai Laboratory:

- https://splab.net/apd/ja/g210/
- basis: T. Arai (2007), "Education system in acoustics of speech production using physical models of the human vocal tract," Acoustical Science and Technology 28(3), 190–201.

The published table gives 16 plate diameters in millimetres for each Japanese vowel.

The table is ordered lips -> larynx. morphoacoustics Tract1DGeometry is inlet/glottis -> outlet/lips, so the values must be reversed before constructing the tract.

Each plate is 10 mm thick.

Initial target vowels:

- /a/
- /i/
- /u/

Diameter-to-area conversion:

A = pi (d / 2)^2

with SI conversion from mm to m before area calculation.

This fixture is an educational/physical vocal-tract model, not an MRI-derived population reference. Successful identification is therefore evidence for this published tract family and the current backend only.

## Published diameter fixtures

Web-table order, lips -> larynx, millimetres:

- /a/: 32, 28, 30, 34, 34, 38, 34, 30, 26, 20, 14, 12, 16, 26, 12, 12
- /i/: 24, 14, 12, 10, 10, 10, 16, 24, 32, 32, 32, 32, 32, 32, 12, 12
- /u/: 16, 14, 20, 22, 22, 24, 22, 14, 18, 26, 30, 30, 30, 30, 12, 12

## Fixed source and renderer

Reuse existing validated experiment-local components.

- sample rate: 48 kHz
- duration: 0.5 s
- F0: 100 Hz
- LF-family source from Experiment 013
- Rd = 1.0
- sound speed: 343 m/s
- air density: 1.21 kg/m^3
- rendered listening path: Experiment-009 loss/load/radiation formulation
- resonance identity is measured from the transfer response, never inferred from harmonic peaks in the rendered waveform

No prosody intervention is added.

## Independent Wolfram oracle

The independent oracle uses the same explicit segmented-tube equations as Experiment 009:

- 16 sections
- section length: 0.01 m
- attenuation: 0.4 Np/m
- terminal load: 0.05 * outlet characteristic impedance
- frequency scan: 100–5000 Hz
- frequency step: 0.25 Hz

Expected first five local maxima of |Uout/Uin|:

| vowel | P1 Hz | P2 Hz | P3 Hz | P4 Hz | P5 Hz |
|---|---:|---:|---:|---:|---:|
| /a/ | 720.25 | 1288.50 | 2918.25 | 4196.00 | 4657.25 |
| /i/ | 281.25 | 2309.25 | 3212.00 | 4102.00 | 4899.25 |
| /u/ | 419.25 | 1481.75 | 3106.50 | 3892.75 | 4580.25 |

These are fixture/backend oracle values, not natural-speech population formants.

Uniform 17 cm regression oracle:

504.4117647, 1513.2352941, 2522.0588235, 3530.8823529, 4539.7058824 Hz.

## Conditions

Only tract geometry changes between primary vowel conditions.

Fixed across /a i u/:

- source family
- F0
- source level rule
- duration
- renderer
- observer
- sample rate
- listening level-normalization rule

## Objective preregistered Gate

All must pass before listening.

1. Fixture provenance is serialized and diameter arrays match the published table exactly.
2. Reversed geometry is finite and positive and contains exactly 16 sections of 0.01 m each.
3. Python transfer peaks match the checked-in Wolfram oracle within 0.5 Hz, following the existing Experiment-009 scan tolerance.
4. The resonance pattern remains distinguishable under the following frozen spatial-discretization perturbation:
   - treat the published 16 diameters as samples at the centers of 16 equal 10 mm cells;
   - linearly interpolate diameter along axial position with endpoint clamping;
   - resample at the centers of 32 equal 5 mm cells;
   - rebuild the 32-section tract from those diameters;
   - measure the Euclidean displacement of (P1, P2) between 16-section and 32-section versions for each vowel;
   - require the minimum pairwise distance between primary 16-section vowel (P1, P2) points to exceed 5x the maximum 16-vs-32 regrid displacement.
5. All rendered pressure arrays are finite.
6. No clipping occurs before listening normalization.
7. Inherited artifact regression thresholds are fixed before results:
   - LF source cycle-boundary jump / source RMS < 0.01;
   - rendered startup peak / steady RMS < 20 for every vowel.
8. Listening level cannot be used as the primary vowel cue:
   - measure each raw-pressure steady-state RMS over 0.05–0.45 s;
   - divide each stimulus by its own steady-state RMS;
   - compute one common safety gain across the three RMS-normalized waveforms so the largest absolute sample is 0.90 full scale;
   - use these level-matched waveforms for both named calibration and blinded confirmation.
9. Raw pressure is retained separately from listening WAVs, and all normalization factors are recorded.
10. Calibration outputs and blinded confirmation outputs are separate and the confirmation key is not inspected before responses are frozen.

Objective success yields only:

ACOUSTIC_VOWEL_FIXTURE_VALIDATED_AWAITING_LISTENING

## Spatial-discretization interpretation

The 32-section condition is not a second physical reference and is not claimed to be more accurate than the published plate model. It is an engineering sensitivity perturbation of the area-profile discretization. The primary oracle remains the literal published 16-plate fixture.

The 5x margin is inherited as an engineering discrimination convention from the prior coordination experiments; it is not a psychoacoustic threshold.

## Human Gate

Primary confirmation:

- 3 vowel categories
- 10 coded trials per vowel
- 30 total trials
- choices: /a/, /i/, /u/, UNIDENTIFIABLE
- no correctness feedback during the set

Engineering pass criterion inherited from #31:

- each vowel >= 8/10
- total >= 24/30

Record separately:

- perceived vowel
- identifiable / unidentifiable
- confidence
- click/snap artifact
- alarm/buzzer-like vs voice-like
- optional free-form observation

Wolfram chance references under an independent unbiased 3-choice model:

- P(X >= 8 of 10) ~= 0.00340395265 for one vowel
- P(X >= 24 of 30) ~= 2.09016e-7 overall

These are engineering references only. Repeated trials from one listener are not treated as independent population observations.

## Decision branches

### SUPPORT_STATIC_VOWEL

Use only when the objective Gate passes and blinded identification meets the engineering Gate.

Then proceed to #32.

### ACOUSTICS_VALID_PERCEPTION_FAILED

Use when the objective calibration passes but blinded vowel identification fails.

Next intervention must isolate one of source spectrum, loss/radiation/observer assumptions, or fixture suitability. Do not simultaneously add a new motor model.

### ACOUSTIC_CALIBRATION_FAILED

Use when the fixture does not reproduce the independent oracle or the numerical path is unstable.

### MORE_DATA

Use when the reference fixture or provenance cannot be reproduced reliably.

## Non-goals

Do not add in Experiment 015:

- task-level vowel realization
- general Gesture inventory
- coarticulation model
- prosody changes
- two-mass/body-cover source
- FSI
- deformable tongue
- neural polish
- Studio-facing controls

## Next capability

If Experiment 015 supports static vowel identity, #32 will test prescribed continuous motion between two calibrated vowel states before #33 attempts task-level motor realization.
