# Experiment 014 — structure-aligned prosody and movable boundary cue

Issue: #29

## Question

Experiment 013 established that an LF-family source plus nonstationary macroprosody can reduce the buzzer/alarm failure mode, but the diagnostic contour was not heard as meaningful intonation.

Experiment 014 asks a narrower, falsifiable question:

> If the same oral task sequence is paired with a prosodic cue anchored to a semantic boundary, does moving that boundary from an earlier to a later anchor move the perceived boundary location?

The success claim is limited to a boundary cue in a Japanese-like diagnostic fixture. This experiment does not claim natural Japanese intonation, lexical segmentation, calibrated vowels, or general speech synthesis.

## Research basis

- Warner, Otake & Arai (2010), DOI 10.1177/0023830909351235: Tokyo Japanese listeners can use accentual-phrase onset intonational structure as a word-boundary cue.
- Seo, Kim & Cho (2021), DOI 10.1016/j.dib.2021.106919: Tokyo Japanese production data include preboundary / phrase-final lengthening.
- PMID 25019156: pitch reset, final lengthening, and pause can all cue phrase boundaries.

Pause is deliberately excluded from the primary condition because it is a strong cue and would make the first test less diagnostic.

## Fixture

The 0.50 s utterance contains an active interval from 0.05 to 0.45 s divided into eight mora-like units.

Nominal timing:

- 8 units
- 50 ms per unit
- early semantic boundary: m3.end = 0.20 s
- late semantic boundary: m5.end = 0.30 s

The oral task identity and order are fixed: eight CONSTRICT gestures alternate between normalized tract locations 0.25 and 0.75 with the same target area.

This alternating-constriction sequence exists only to make local duration changes acoustically observable before phonetic calibration. It is not a phoneme or mora model.

The shared-timeline compiler from #28 maps stable semantic anchors to the existing GestureScore; no solver section index or raw waveform parameter is inserted into the plan.

## Conditions

- flat: fixed 100 Hz F0, nominal timing, no boundary cue.
- diagnostic: Experiment-013-style non-structural F0 contour, rescaled to the same ±0.6-semitone range.
- pitch_early / pitch_late: local F0 reset centered on m3.end / m5.end.
- duration_early / duration_late: 20% preboundary-unit lengthening with total active duration preserved.
- combined_early / combined_late: aligned pitch and duration cues.

Gain/effort is held fixed in rev1 so that pitch and duration remain the only boundary interventions.

## Pitch realization

The structure-aligned cue uses:

- pre-boundary plateau: -0.6 semitone
- post-boundary plateau: +0.6 semitone
- baseline: 100 Hz

Independent Wolfram values:

- low: 96.59363289248456 Hz
- high: 103.52649238413775 Hz
- reset: 6.93285949165319 Hz

The magnitude is an engineering diagnostic choice informed by Experiment 013. The cited Japanese literature supports the existence/use of pitch-rise boundary cues, not this exact numeric excursion.

## Duration realization

DURATION_SCALE = 1.20.

Independent Wolfram values:

- early duration condition: boundary resolves to 0.21 s; five following units become 48 ms each
- late duration condition: boundary resolves to 0.31 s; three following units become 46.6666667 ms each
- active duration remains 0.40 s

The 20% lengthening is an experiment-local diagnostic magnitude, not a claimed population mean for Tokyo Japanese.

## Objective preregistered gate

All must pass before listening:

1. shared-timeline compilation is VALID;
2. boundary provenance resolves to the intended semantic anchor;
3. structure-aligned F0 reset is >= 5 Hz;
4. F0 event timing error is <= 1 ms;
5. F0 realization RMSE is <= 0.1 Hz;
6. duration target error is <= 0.1 ms;
7. total active-duration error is <= 0.1 ms;
8. cycle-boundary jump / source RMS is < 0.01;
9. rendered startup peak / steady RMS is < 20;
10. early/late F0-range mismatch is <= 0.1 Hz;
11. outputs are finite;
12. Experiment-011/013 oral-effect regression remains > 0.01 and > 5x the flat candidate/reference discretization difference.

Candidate/reference renderer sensitivity is reported separately from the boundary intervention effect.

Passing this gate yields only CONTROL_REALIZATION_VALIDATED_AWAITING_LISTENING. It does not yield perceptual support.

## Primary human confirmation

The primary confirmation is pitch_early vs pitch_late.

The run generates eight randomized coded trials:

- 4 early
- 4 late
- fixed seed 14014
- no correctness feedback during confirmation

The listener answers EARLY or LATE for the perceived boundary and separately records boundary-not-felt, confidence, click/snap, alarm/buzzer-like vs voice-like, and meaningful intonation vs arbitrary wobble.

Auxiliary repeatability threshold: >= 7/8 target-consistent answers.

Under an independent unbiased 50/50-choice model, Wolfram gives:

9/256 = 0.03515625

This is not treated as a population-level p-value because one listener hearing repeated stimuli does not provide eight independent population observations.

## Outputs

Run:

~~~bash
python experiments/014_structure_aligned_prosody/run.py --output-dir experiment-014-output
~~~

Outputs include condition_metrics.csv, boundary_pair_metrics.csv, control_trajectories.csv, plan_provenance.json, decision.json, raw pressure arrays, named secondary listening WAVs, and the primary coded T01..T08 listening set.

Do not inspect blind_key.csv before primary listening.

## Scope boundary

This experiment does not establish Japanese lexical/phonemic correctness, natural Japanese intonation, calibrated vowel identity, a production ProsodyPlan-to-F0 law, general coarticulation, source-filter back-coupling, self-oscillating vocal folds, or Studio-facing emotion/prosody controls.

If the objective controls pass but the boundary location does not track in listening, the next intervention is to revise one cue/fixture axis, not to jump directly to a two-mass source model.
