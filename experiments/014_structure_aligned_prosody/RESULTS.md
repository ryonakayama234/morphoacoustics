# Experiment 014 results — structure-aligned prosody objective gate

Issue: #29

## Current decision

**CONTROL_REALIZATION_VALIDATED_AWAITING_LISTENING**

The preregistered objective gate passed. This result establishes that the experiment-local semantic boundary plan, structure-aligned F0 cue, duration realization, shared-timeline compilation, oral rendering, and listening-set generation behaved as specified.

It does **not** establish that the boundary cue is perceptually meaningful. The primary blinded early/late listening test remains outstanding.

## Provenance

Objective CI run:

- GitHub Actions run: 36980616997
- source branch: experiment-014-structure-aligned-prosody
- source commit: 99bfae67b1239e686a88ef227cb0029a3c9a252b
- full output artifact digest: sha256:471751b9c64684006beb45f360b4bac37529a8d95a739ee2d68323c30f14bb50
- primary blind-listening artifact digest: sha256:5319af9c5a4fd7a24ada139ca6992c0b5e750bb185e81d4698a8621a03ebe200

Repository tests and type checking also passed on Python 3.11, 3.12, and 3.13.

## Objective gate

All preregistered primary objective checks passed:

- shared-timeline compile: PASS
- semantic boundary provenance: PASS
- structure-aligned F0 reset >= 5 Hz: PASS
- F0 event timing error <= 1 ms: PASS
- F0 realization RMSE <= 0.1 Hz: PASS
- duration target error <= 0.1 ms: PASS
- total active-duration error <= 0.1 ms: PASS
- cycle-boundary jump / source RMS < 0.01: PASS
- startup peak / steady RMS < 20: PASS
- early/late F0-range mismatch <= 0.1 Hz: PASS
- finite outputs: PASS
- inherited oral-effect regression: PASS

The flat oral sequence remained observably different from the fixed-tract control:

- oral-vs-fixed normalized RMS difference: 0.4023791909
- flat candidate/reference discretization difference: 0.03910112834

The oral effect therefore remains above both the 0.01 floor and the inherited 5x numerical-discretization margin.

## Structure-aligned pitch realization

The early and late pitch-only conditions preserved identical cue magnitude and range.

### pitch_early

- semantic anchor: m3.end
- resolved boundary: 0.200 s
- F0 low: 96.5936328925 Hz
- F0 high: 103.5264923841 Hz
- reset: 6.9328594917 Hz
- event-time estimate: 0.2003958333 s
- event timing error: 0.395833 ms
- F0 RMSE: 6.10e-11 Hz
- cycle-boundary jump / RMS: 4.40e-5
- startup peak / steady RMS: 2.691
- candidate/reference discretization difference: 0.03797

### pitch_late

- semantic anchor: m5.end
- resolved boundary: 0.300 s
- same 6.9328594917 Hz F0 reset
- event-time estimate: 0.3003958333 s
- event timing error: 0.395833 ms
- F0 RMSE: 6.60e-11 Hz
- cycle-boundary jump / RMS: 4.40e-5
- startup peak / steady RMS: 2.650
- candidate/reference discretization difference: 0.03886

Early/late F0-range mismatch was exactly 0 within reported precision.

The non-structural diagnostic contour was also matched to the same F0 range; diagnostic-vs-structured range difference was 0 within reported precision.

## Duration realization

The duration conditions realized the preregistered 20% preboundary lengthening exactly.

### duration_early

- semantic anchor: m3.end
- target unit: 60 ms
- resolved boundary: 0.210 s
- active-duration error: approximately 5.6e-17 s

### duration_late

- semantic anchor: m5.end
- target unit: 60 ms
- resolved boundary: 0.310 s
- active-duration error: approximately 5.6e-17 s

The total 0.40 s active interval therefore remained matched.

## Early-vs-late intervention strength

The early/late waveform differences were compared with the larger candidate/reference discretization perturbation in each family.

| family | early-vs-late normalized RMS | max discretization | effect / discretization |
|---|---:|---:|---:|
| pitch | 0.8153460 | 0.0388578 | 20.98x |
| duration | 0.1345176 | 0.0379904 | 3.54x |
| combined | 0.8230857 | 0.0370560 | 22.21x |

This matters for interpretation.

### Pitch-only

The primary intervention is far larger than the tested renderer/control discretization perturbation. It is suitable for the preregistered blinded boundary-location test.

### Combined

The aligned pitch + duration intervention is also far larger than the tested discretization perturbation. It remains a useful secondary confirmation condition.

### Duration-only

The duration-only early/late difference is real and finite, but reaches only about **3.54x** the tested discretization perturbation. Experiment 011 used a 5x engineering discrimination margin.

That 5x margin was not preregistered as the primary Experiment-014 duration decision rule, so this is not retroactively converted into an objective failure. However, the duration-only ablation should be treated as **secondary / MORE_DATA-like evidence**, not as a robust standalone boundary intervention in rev1.

This supports the preregistered decision to make pitch-only the primary human Gate.

## Artifact / stability checks

All rendered outputs were finite.

Representative structure-aligned source values:

- cycle-boundary jump / RMS: about 4.4e-5
- fixed 10 ms lag correlation: about 0.9938
- startup peak / steady RMS: approximately 2.65–2.69

No Experiment-012-style snap/startup regression appeared under the objective metrics.

## Independent Wolfram oracle

The Python realization matched the checked-in independent Wolfram values for:

- nominal unit duration
- early / late nominal semantic-boundary times
- duration scale
- duration-adjusted early / late boundary times
- post-boundary compensation durations
- active duration
- ±0.6-semitone F0 endpoints
- 6.9328594917 Hz reset
- the 7/8 binary-choice reference probability

The latter remains:

9 / 256 = 0.03515625

It is used only as an auxiliary within-listener repeatability reference, not a population-level p-value.

## Human Gate now required

The primary listening set contains eight coded pitch-only trials:

- 4 early-boundary stimuli
- 4 late-boundary stimuli
- deterministic randomized order
- common playback gain across conditions
- no correctness feedback during the set

For each trial, record:

1. EARLY or LATE perceived boundary;
2. boundary not felt: yes/no;
3. confidence;
4. click/snap artifact;
5. alarm/buzzer-like vs voice-like;
6. meaningful intonation vs arbitrary wobble.

Auxiliary repeatability criterion: at least 7/8 target-consistent location responses.

The key must remain hidden until all eight location responses are frozen.

## Decision branches after listening

### SUPPORT_STRUCTURE_ALIGNED_PROSODY

Use only if the planned controls remain valid **and** boundary-location responses track the moved semantic anchor repeatably, with structure-aligned variation distinguishable from arbitrary diagnostic wobble.

### CONTROL_VALID_BUT_NOT_MEANINGFUL

Use if the objective controls are correct but the early/late boundary location does not reliably track perceptually.

### SUPPORT_BOUNDARY_CUE_ONLY

Use if boundary location tracks but general voice quality remains weak. In that case proceed to #31 vowel calibration; do not infer that a more complex vocal-fold model is immediately required.

## Claim boundary

The strongest objective claim at this point is:

> The current compiler and LF-family synthesis path can realize a pitch boundary cue at two different semantic anchors with matched range, sub-millisecond event alignment, finite artifact-controlled rendering, and an early/late acoustic effect far above the tested discretization perturbation.

Whether that cue is heard as a meaningful boundary is still an empirical human question.
