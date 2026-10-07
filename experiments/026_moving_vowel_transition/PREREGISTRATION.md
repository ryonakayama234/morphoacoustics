# Experiment 026 — prescribed moving vowel transition

Issue: #32  
Short-term milestone: C1 Continuous Reference-Anchored Performance Slice

## Question

Can the current validated low-fidelity acoustic path render a **single continuous /a/ -> /i/ tract transition** from calibrated Arai endpoint geometries, while preserving endpoint acoustics and remaining distinguishable from a static-WAV concat control by more than the temporal numerical floor?

This is a moving-acoustics engineering experiment. It does **not** test task-level Gesture realization, general coarticulation, natural speech, or Studio live synthesis.

## Why this experiment is allowed after Experiment 025

Experiment 023 established the objective Arai-tract calibration but missed its frozen three-vowel perceptual Gate because /i/ was 7/10. Experiments 024–025 then isolated source-spectrum support. Experiment 025 restored answered closed-set vowel-category separation while the listener still described the signals as buzzer-like rather than voice-like.

Therefore this experiment uses the validated tract fixtures but **does not use Experiment-025's diagnostic cos/n^2 source**. It returns to the Experiment-013 fixed LF-family baseline and asks only whether time-varying tract acoustics work.

Perceptual/open-set evaluation remains owned by #37.

## Frozen target

Transition:

```text
/a/ -> /i/
```

Rationale fixed before execution:

- /a/ is the clearest qualitative endpoint in the completed listening work;
- /a/ and /i/ have strongly separated calibrated P1/P2 coordinates;
- the pair exercises a large low-order resonance movement without introducing a third category.

No endpoint pair will be changed after seeing Experiment-026 output.

## Endpoint fixture

Reuse Experiment 023 exactly:

- Arai Laboratory plate-type vowel fixture;
- 16 sections;
- section length 10 mm;
- table order reversed from lips->larynx to glottis->lips;
- diameter converted to circular area;
- primary endpoint geometries are the literal published /a/ and /i/ 16-section fixtures.

The 32x5 mm center-regridded fixtures from Experiment 023 are retained as a spatial-sensitivity diagnostic, not as a new physical truth.

## Fixed source / renderer

Fixed across all primary conditions:

- sample rate: 48 kHz;
- total duration: 0.500 s;
- source: Experiment-013 `lf_fixed`;
- F0: 100 Hz;
- Rd: 1.0;
- same source waveform bytes for T0 and T1;
- Experiment-009 loss/load/radiation formulation;
- Experiment-012 preroll-edge short-time renderer;
- no prosody intervention;
- no aspiration/noise intervention;
- no source-filter feedback.

Experiment-025 S2 is excluded.

## Prescribed trajectory

Transition window:

```text
t0 = 0.150 s
t1 = 0.350 s
duration = 0.200 s
```

Progress:

[
u(t)=operatorname{clip}left(rac{t-t_0}{t_1-t_0},0,1ight)
]

[
lambda(t)=3u^2-2u^3
]

Thus (lambda=0) before the transition, (lambda=1) after the transition, and the endpoint velocity is zero.

### Primary trajectory — log-area

For each section (j),

[
A_j(t)=expleft[(1-lambda(t))ln A_{a,j}
+lambda(t)ln A_{i,j}ight].
]

Reasons for choosing this as the primary candidate before execution:

- exact recovery of both endpoints;
- strict positivity for positive endpoint areas;
- multiplicative/ratiometric symmetry;
- midpoint is the geometric mean rather than an arithmetic average.

### Secondary trajectory — linear-area

[
A_j^{lin}(t)=(1-lambda(t))A_{a,j}+lambda(t)A_{i,j}.
]

This is a diagnostic comparator only. It is not allowed to replace the primary candidate post hoc because it sounds better.

## Control sampling and acoustic update cadence

Primary T1:

- control sample step: 5 ms;
- linear reconstruction of sampled (lambda);
- acoustic hop: 256 samples;
- frame size: 1024 samples.

Temporal reference:

- control sample step: 2.5 ms;
- acoustic hop: 128 samples;
- same analytic trajectory, source, endpoints, and renderer.

Independent Wolfram calculation freezes the expected maximum progress-reconstruction errors:

- 5 ms: <= 0.000457039562251;
- 2.5 ms: <= 0.000115722656251.

## Conditions

### T0 — static concat control

Render two independent 0.250 s source segments:

1. first half through the static /a/ endpoint;
2. second half through the static /i/ endpoint;

then concatenate with **no crossfade**.

This intentionally represents the bad "render completed sounds and paste them together" implementation.

### T1 — continuous primary

Render the full 0.500 s source in **one call** through the prescribed log-area /a/ -> /i/ trajectory.

No state reset or waveform splice is allowed inside T1.

### T1-ref — temporal reference

Same as T1 but with 2.5 ms control sampling and 128-sample acoustic hop.

### T2 — linear-area diagnostic

Same as T1 but with linear-area interpolation.

### S1 — spatial diagnostic

Repeat resonance-trajectory analysis on the inherited 32x5 mm center-regridded endpoints with the same log-area progress. This is reported separately from temporal numerical convergence.

## Independent Wolfram oracle

A checked-in Wolfram calculation freezes these segmented-tube response peaks on the same 0.25 Hz scan grid used by Experiment 023.

| geometry | P1 Hz | P2 Hz | P3 Hz | P4 Hz | P5 Hz |
|---|---:|---:|---:|---:|---:|
| /a/ | 720.25 | 1288.50 | 2918.25 | 4196.00 | 4657.25 |
| /i/ | 281.25 | 2309.25 | 3212.00 | 4102.00 | 4899.25 |
| linear midpoint | 567.25 | 1737.25 | 2915.25 | 4063.75 | 4673.75 |
| log-area midpoint | 517.25 | 1750.50 | 2940.50 | 4130.50 | 4710.50 |

Peak tolerance remains <= 0.5 Hz.

The same oracle also retains the closed-open uniform-tube regression:

[
f_n=rac{(2n-1)c}{4L},quad c=343 mathrm{m/s}.
]

- L=0.14 m: 612.5, 1837.5, 3062.5 Hz;
- L=0.17 m: 504.4117647, 1513.2352941, 2522.0588235 Hz;
- L=0.20 m: 428.75, 1286.25, 2143.75 Hz.

The uniform tube is a regression fixture only, not a vowel model.

## Recorded observables

At minimum save:

- source waveform identity / checksum;
- endpoint and midpoint geometry provenance;
- sampled progress trajectory;
- section-area trajectories;
- P1/P2/P3 resonance trajectories at 10 ms analysis cadence;
- T0, T1, T1-ref and T2 raw pressure waveforms;
- listening WAVs using a common comparison normalization rule;
- temporal numerical-floor metrics;
- T0-vs-T1 effect metrics;
- spatial regrid trajectory diagnostics;
- first-difference artifact diagnostics;
- environment and backend provenance.

Resonances are extracted from the tract transfer response, never from source harmonic peaks in the rendered waveform.

## Frozen objective Gate

### 1. Endpoint / oracle reproduction

- primary (lambda=0) geometry equals the Experiment-023 /a/ primary geometry exactly;
- primary (lambda=1) geometry equals /i/ exactly;
- endpoint first five peaks match the checked-in Wolfram oracle within 0.5 Hz;
- both midpoint candidates match their Wolfram first-five-peak oracle within 0.5 Hz.

Failure class: `STATIC_ENDPOINT_REGRESSION`.

### 2. Geometry validity

For all analysed times and sections:

- length finite and positive;
- area finite and positive;
- no NaN / Inf;
- endpoints exactly recovered.

Failure class: `ACOUSTIC_TRANSITION_FAILED`.

### 3. Progress-reconstruction oracle

Observed max absolute error relative to analytic (lambda(t)) must be no greater than:

- 0.000457039562251 for 5 ms;
- 0.000115722656251 for 2.5 ms;

plus (10^{-12}) floating tolerance.

### 4. Continuous single-pass rendering

T1 must be generated by one full-duration renderer invocation, not by concatenating independently rendered pieces.

This is recorded explicitly in provenance.

### 5. Finite / artifact regression

- every raw pressure array is finite;
- T1 transition-region max adjacent-sample jump must be < 3x the larger max adjacent-sample jump measured in the two steady endpoint regions 0.05–0.14 s and 0.36–0.45 s.

This is an engineering reset/click detector, not a psychoacoustic threshold.

### 6. Resonance trajectory tracking

At 10 ms cadence:

- at least P1/P2/P3 are available at every primary trajectory point;
- all tracked values are finite;
- for P1/P2, the maximum adjacent trajectory step divided by the static /a/-to-/i/ P1/P2 Euclidean endpoint distance must be < 0.20.

This catches peak-tracking discontinuities while allowing a nonlinear path.

### 7. Temporal convergence

Define normalized RMS difference

[
d(x,y)=rac{operatorname{RMS}(x-y)}{operatorname{RMS}(y)}.
]

Let:

- (D_{effect}=d(T1,T0));
- (D_{temporal}=d(T1,T1ref)).

Require:

- (D_{temporal}<0.20), inherited from the Experiment-010 engineering stability convention;
- (D_{effect}>5D_{temporal}).

The 5x factor is an engineering discrimination margin, not a perceptual JND.

### 8. Spatial sensitivity

The Experiment-023 primary endpoint spatial-discretization result remains a prerequisite:

- minimum between-vowel P1/P2 separation / maximum endpoint regrid displacement > 5x.

For Experiment 026, primary-vs-refined **dynamic path mismatch is recorded but not folded into the temporal numerical floor**, because the center-regrid changes the represented geometry as well as its discretization.

A large dynamic path mismatch yields `SPATIAL_PATH_SENSITIVE` diagnostic and blocks promotion of that path as a frozen reference until inspected, but it is not silently called floating-point error.

## Decision

### SUPPORT_MOVING_ACOUSTICS

Only if Gates 1–7 pass, inherited spatial prerequisite remains valid, and no spatial-path diagnostic reveals an untraceable discontinuity.

Then freeze:

- /a/ and /i/ endpoint revision;
- log-area trajectory;
- transition window;
- source identity;
- control cadence;
- acoustic hop/frame;
- backend revision;
- state-inheritance / single-pass semantics;
- artifact provenance.

This frozen revision can be handed to #37 and later #33.

### STATIC_ENDPOINT_REGRESSION

Dynamic path cannot reproduce calibrated endpoint acoustics.

### ACOUSTIC_TRANSITION_FAILED

Invalid geometry, non-finite rendering, reset/click failure, or resonance tracking failure.

### NUMERICALLY_UNRESOLVED

Temporal effect cannot be separated from the temporal numerical floor.

### SPATIAL_PATH_SENSITIVE

Endpoint prerequisite is valid but the interpolated dynamic path is excessively sensitive to the inherited spatial regrid. Diagnose before promotion.

## Human observation

Human listening is exploratory only for this experiment:

1. click / snap / reset?
2. two static sounds pasted together, or one moving sound?
3. smooth pronunciation transition?
4. voice-like quality maintained, degraded, or unchanged?

Do not run another three-way static-vowel forced-choice block as the primary Gate.

#37 owns free transcription, constrained identification, voice-likeness, and natural-reference evaluation.

## Non-goals

- task/gesture controller;
- #33 motor realization;
- general coarticulation theory;
- arbitrary Script;
- recording-specific copy synthesis;
- prosody optimization;
- two-mass/body-cover source;
- FSI/FEM;
- neural polish;
- Studio live execution.

## Maximum claim on success

> With calibrated Arai /a/ and /i/ endpoint states and a prescribed positive continuous tract trajectory, the current quasi-stationary backend can render a stable continuous acoustic transition whose effect is resolved above the temporal discretization floor while reproducing the static endpoint acoustics.

Do not call this autonomous articulation, natural speech, true moving-boundary FSI, or general TTS.
