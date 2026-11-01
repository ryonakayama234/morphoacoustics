# Experiment 043 — preregistered pilot reasoning (before real scoring)

Status: **DESIGN + IMPLEMENTATION CANDIDATE, actual full execution NOT YET RECORDED**.
This research lane is independent of formal CVI-1 Gate B and must not substitute
its preregistered body/habit criteria or its independent scientific review.

## Question

Can the existing Core physics, without new audio postprocessing, produce a
repeatable **two-factor causal difference** in physical acoustic observations
when only body axial length and one gesture onset are varied?

## Intervention

- Body: Arai-derived 16-section `/a/` numerical rest body M0 (0.010m/section)
  vs exactly 1.10× section length M1 (0.011m/section). All areas unchanged.
- Motor schedule: same three task targets and offsets, but the second
  `CONSTRICT` starts at 0.19 instead of 0.15 s; end remains 0.35 s.
- Fixed: same source samples, F0 100 Hz, source phase, 0.5s duration,
  task shapes, acoustic backend, observation point and common playback gain.
- No change to installed `src/morphoacoustics`, `src/morphoacoustics_graph`,
  adopted CC-A2 adapter or Studio contracts.

## Falsifiers and software gates

1. An absent or incorrect 10% body-length change; any unintended area change.
2. A change in the final realized task target between timing profiles.
3. No realized geometric change during the schedule intervention at t=0.17 s.
4. Nonfinite or incorrectly shaped raw pressure or shared-gain clipped WAV.
5. Identical raw pressure under one-factor physical interventions.
6. Loss of true upstream source or a model mismatch at execution: stop, do\n   not create synthetic substitute waveforms. The frozen source must pass the\n   inherited Exp026 source-regression check AND an independent 100 Hz planned-F0\n   assertion. Negative control: a 120 Hz source/expected-F0 drift must refuse.\n7. A missing/unresolvable Git checkout revision or missing runtime metadata\n   must stop receipt publication. Record tracked-worktree dirty status even\n   for non-CI exploratory runs. Previously archived evidence is not relabelled.

These are numerical viability checks, not natural-voice or phonetic-validity
gates. No arbitrary perceptual magnitude threshold is imposed after seeing
outputs. If four conditions are numerically distinguishable, the only justified
outcome is **NUMERICAL_PILOT_ONLY**, never GO for Character Voice Identity.

## Analysis after execution

Archive the complete 4 × raw-pressure + WAV + receipt result and an exact
Core commit/environment run reference. Compare body within each timing profile
and timing within each body. Report both waveform difference and RMS/SPL
context under the same gain; identify any unexpectedly larger transition
artifacts. A later blind audition must test open-ended voice likeness and
character distinction separately from closed-set discriminability.

Formal CVI voice identity (same speaker across phonation, text, effort and
performance) requires additional physiology and independent evidence.

## Post-review Gate-A amendment (2026-10-31; not prospective to the original WAVs)

The 2026-10-30 independent reviewer observed a false-negative source-drift test: changing Exp026's expected `BASE_F0_HZ` does not actually mutate Exp013's generated phase. To close this separate integrity gap, the revised pilot must fail **before rendering** when (A) Exp013 actual phase progresses at 120 Hz but planned F0 still says 100 Hz, (B) both nominal source and inherited regression expectations drift to 120 Hz together, or (C) emitted LF flow differs from the declared opening/gain controls while phase metadata remains unchanged. Original experiment intervention/thresholds, old WAVs, and voice-quality HOLD are unchanged. A fresh exact-head CI and review are required; this amendment does not retroactively certify the archived output.
