# Experiment 026 results — prescribed moving vowel transition

Issue: #32  
PR: #61  
Milestone role: C1 physical hard Gate

## Decision

**SUPPORT_MOVING_ACOUSTICS**

The preregistered objective Gate passed without changing any frozen threshold after execution.

This supports the narrow claim:

> With calibrated Arai /a/ and /i/ endpoint states and a prescribed positive continuous tract trajectory, the current quasi-stationary backend can render a stable continuous acoustic transition whose effect is resolved above the temporal discretization floor while reproducing the static endpoint acoustics.

It does not establish task-level articulation, natural speech, general coarticulation, moving-boundary FSI, or TTS.

## Provenance

Canonical PR execution:

- GitHub Actions run: `37600635390`
- branch: `v2-experiment-026-moving-vowel-transition`
- source head commit: `863a2ca834cc8d184ca43495139661f800c0d9e0`
- full output artifact ID: `11472960474`
- full output artifact digest: `sha256:60320ed311691378d29726cdff591e34992444229690f1e2319ed499ec4c2cd3`
- exploratory blind-listening artifact ID: `11472034547`
- blind-listening artifact digest: `sha256:cee1ffaf0fec7b406376fafbc90adc85a30860a526fb21d23dab8dd6ca55bc21`
- source waveform SHA-256 over little-endian float64 bytes: `4d075fd89958ff481507661ea43e4602ed5fe72b0104bc897685b1f696abf529`

Repository tests passed on Python 3.11, 3.12, and 3.13, and the typecheck job passed for the same PR head.

## Frozen primary condition

- transition: `/a/ -> /i/`
- endpoint family: Experiment-023 Arai 16 x 10 mm fixtures
- primary interpolation: log-area
- transition window: 0.150–0.350 s
- progress law: smoothstep `3u^2 - 2u^3`
- source: Experiment-013 `lf_fixed`
- F0: 100 Hz
- Rd: 1.0
- primary control step: 5 ms
- primary acoustic hop: 256 samples
- frame size: 1024 samples
- temporal reference: 2.5 ms control / 128-sample hop
- renderer: Experiment-012 preroll-edge short-time renderer with Experiment-009 transfer
- Experiment-025 diagnostic cos/n² source: excluded

T1 is one full-duration renderer invocation. It is not assembled from rendered endpoint WAVs.

## Independent Wolfram oracle agreement

The Wolfram oracle was frozen before Python execution.

All first five checked peaks matched exactly on the 0.25 Hz scan grid:

| geometry | P1 Hz | P2 Hz | P3 Hz | P4 Hz | P5 Hz |
|---|---:|---:|---:|---:|---:|
| /a/ | 720.25 | 1288.50 | 2918.25 | 4196.00 | 4657.25 |
| /i/ | 281.25 | 2309.25 | 3212.00 | 4102.00 | 4899.25 |
| log-area midpoint | 517.25 | 1750.50 | 2940.50 | 4130.50 | 4710.50 |
| linear-area midpoint | 567.25 | 1737.25 | 2915.25 | 4063.75 | 4673.75 |

Observed absolute peak error: **0.0 Hz** for all 20 checked peaks.

Midpoint area oracle:

- log-area maximum absolute area error: `3.2526065e-19 m²`
- linear-area maximum absolute area error: `0.0 m²`

Both passed.

## Progress reconstruction

Independent Wolfram frozen bounds and Python observations:

| cadence | observed max absolute error | frozen upper bound | result |
|---|---:|---:|---|
| 5 ms | 0.0004570395622500009 | 0.000457039562251 | PASS |
| 2.5 ms | 0.00011572265625003908 | 0.000115722656251 | PASS |

The endpoint geometry is recovered exactly and all analysed geometry remained finite and positive.

## Source regression

Experiment-013 `lf_fixed` remained the source:

- planned F0 identically 100 Hz: PASS
- stochastic-noise component exactly zero: PASS
- cycle-boundary jump / RMS: **4.40621855e-05**
- frozen limit: **< 0.01**
- result: PASS

The same source bytes were used across T0/T1/T1-ref/T2.

## Resonance trajectory

Static /a/-to-/i/ P1/P2 endpoint distance:

- **1111.148758 Hz**

Maximum adjacent 10 ms P1/P2 step relative to that endpoint distance:

- primary 16 x 10 mm path: **0.0783054**
- refined 32 x 5 mm path: **0.0767857**
- frozen limit: **< 0.20**

P1/P2/P3 remained finite and trackable throughout both paths.

## Spatial sensitivity

Inherited Experiment-023 endpoint separation / regrid ratio recomputed in this run:

- **7.62513x**
- prerequisite: **> 5x**

Maximum matched-time primary-vs-refined P1/P2 displacement:

- **46.91015 Hz**
- as fraction of primary /a/-to-/i/ endpoint P1/P2 distance: **0.0422177**
- frozen dynamic spatial-path limit: **< 0.20**

Result: PASS.

The primary-vs-refined path difference remains a geometry/discretization diagnostic and is not folded into the temporal floating-point floor.

## Waveform / reset-artifact Gate

All T0/T1/T1-ref/T2 pressure arrays were finite.

For primary T1:

- transition-region max adjacent-sample jump: **0.0007458720 Pa**
- larger steady-endpoint-region max adjacent-sample jump: **0.0007357798 Pa**
- ratio: **1.013716**
- frozen limit: **< 3.0**

Result: PASS.

This is an engineering reset/click detector, not a psychoacoustic threshold.

## Temporal convergence and intervention size

Normalized RMS definition:

[
d(x,y)=\frac{\operatorname{RMS}(x-y)}{\operatorname{RMS}(y)}.
]

Observed:

- temporal numerical floor, T1 vs T1-ref: **0.00954862**
- frozen temporal-stability limit: **< 0.20**
- moving-vs-concat effect, T1 vs T0: **0.354199**
- effect / temporal floor: **37.0942x**
- frozen discrimination requirement: **> 5x**

Therefore the moving-acoustics intervention is strongly resolved above the chosen temporal discretization perturbation.

## Raw signal summary

| condition | peak Pa | RMS Pa |
|---|---:|---:|
| T0 static concat | 0.00533832 | 0.00210383 |
| T1 continuous log-area | 0.00539448 | 0.00205565 |
| T1-ref continuous log-area | 0.00536069 | 0.00205579 |
| T2 continuous linear-area | 0.00532697 | 0.00203779 |

Listening WAVs use one common safety gain across T0/T1/T2, preserving their relative level.

## Gate summary

All preregistered machine Gates passed:

- endpoint / Wolfram oracle reproduction: PASS
- geometry validity: PASS
- progress reconstruction: PASS
- source regression + single-pass contract: PASS
- finite waveform + artifact check: PASS
- resonance tracking: PASS
- temporal convergence + effect resolution: PASS
- spatial-path diagnostic: PASS

Final objective decision: **SUPPORT_MOVING_ACOUSTICS**.

## Human observation

A two-condition exploratory blind package was generated for:

- T0 — static independent endpoint renders concatenated with no crossfade
- T1 — one continuous log-area transition render

This listening observation is deliberately not part of the objective PASS/FAIL Gate.

Before opening `blind_key.csv`, record separately:

1. click / snap / reset;
2. pasted-two-sounds vs one moving sound;
3. transition smoothness;
4. voice-like quality;
5. free notes.

Do not interpret this as an open-set speech evaluation. #37 remains the source of truth for free transcription, constrained identification, voice-likeness/artifact, and natural-reference evaluation.

## Handoff

The following V2 revision is now eligible to freeze for downstream work:

- Arai /a/ and /i/ endpoint revision from Experiment 023;
- log-area interpolation;
- smoothstep 0.150–0.350 s trajectory;
- Experiment-013 `lf_fixed` source;
- primary 5 ms control cadence / 256-sample acoustic hop;
- Experiment-012 preroll-edge frame renderer;
- Experiment-009 transfer/radiation approximation;
- explicit one-call continuous-render semantics;
- full provenance and numerical diagnostics above.

Next physical capability after C1 is #33: replace the prescribed physical trajectory with task-level Gesture -> body-specific realization. That step must not retroactively change the Experiment-026 Gate.
