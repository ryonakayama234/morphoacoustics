# V4-A preregistration candidate — one-run /a/-like → /i/-like → /a/-like

**Status: DRAFT / NOT EXECUTED / NO SCIENTIFIC ADOPTION.**  
Tracking: [Core #74](https://github.com/ryonakayama234/morphoacoustics/issues/74); related Core #76 (future stateful mechanics), #71 (independent timbre study), and Studio [Voice Atelier #16](https://github.com/ryonakayama234/morphoacoustics-studio/issues/16).

## Scientific question and capability boundary

Does the **currently adopted algebraic V3 task-field realizer** plus **time-varying short-time overlap-add acoustic renderer** remain numerically stable, reproducible, and acoustically traceable for **two changes of target geometry in one 1.00 s run**?

This is an integration/continuity falsification test. A passing result **does not** demonstrate material inertia, force-limited motor control, time-domain acoustic PDE state, source-filter feedback, phase-based gestural competition, syllabic coarticulation, or natural Japanese phoneme identity. Those need separate experiments. In particular, a single scalar forward-and-reverse activation schedule is **not** a demonstration that independently timed gestures cooperate.

## Frozen input, one intervention

| Item | Value / provenance |
| --- | --- |
| prepared body | V3c validated `M_plus` exactly as in the adopted Core #69 live fixture |
| phonetic/acoustic start | Experiment 023/026 calibrated `/a/` prepared rest state |
| fixed task inventory | all three Experiment 027 OPEN/CONSTRICT locations, degrees, Gaussian kernels, kappa and widths, unchanged |
| reference target | Experiment 027 frozen three-task `/i/-like` endpoint; do **not** silently replace it with exact calibrated `/i/` |
| source | Experiment 013 `lf_fixed`, Rd=1.0, F0=100 Hz, noise=0, unchanged pulse shape and peak flow setting |
| duration / audio grid | 1.00 s / 48,000 Hz / exactly 48,000 output samples |
| primary control / acoustic | 5 ms / 1024-sample Hann frame / 256-sample hop |
| convergence comparator | 2.5 ms control / same frame / 128-sample hop |
| seed | 0, recording Python/NumPy/source revisions as provenance |
| sole study intervention | **task-activation schedule lengthens from existing 0.5 s one-way ramp to 1.0 s round trip**; do not co-change body, source timbre, source–filter solver, or task field |

The Experiment 027 `onset_s` and `offset_s` are **start and completion of activation**, not an automatic gestural release. The new experiment must name its separate activation/hold/release semantics explicitly, without modifying the original frozen task plan.

### Analytically frozen task schedule

Let `s(u)=3u²−2u³` for `0≤u≤1`. For all three unchanged spatial task fields, the experiment-local scalar activation is

```text
a(t) = 0                       0.00 ≤ t ≤ 0.15
     = s((t-0.15)/0.20)         0.15 < t < 0.35
     = 1                       0.35 ≤ t ≤ 0.65
     = s((0.85-t)/0.20)         0.65 < t < 0.85
     = 0                       0.85 ≤ t ≤ 1.00
```

Compute realized log area **from the three separately represented task contributions**, each with its own activation record; the coincident schedule is this candidate's intentional constraint, not an API assumption:

```text
log A_j(t) = log A_a,j + 2 Σ_i a_i(t) delta_i(x_j).
```

Do not reverse audio samples or reset geometry/oscillator at the 0.5 s midpoint. Do not make 0.35 or 0.65 s a new audio segment.

**Independent Wolfram schedule oracle (2026-10-10):** at t = 0, .15, .25, .35, .50, .65, .75, .85, 1.00 s, `a(t) = 0,0,.5,1,1,1,.5,0,0`. Maximum `|a'|` = 7.5 s⁻¹; maximum one-sided `|a''|` = 150 s⁻². The command is C¹, but not C², at its ramp boundaries. This checks only the **command trajectory**, not actual inertial articulator motion. The 1.0 s signal has 48,000 samples and 100 nominal F0 cycles. With the existing Experiment-012 preroll pad of 1024 samples on each side, the expected transfer callback counts are 196 (hop 256) and 391 (hop 128), assuming the implementation remains unchanged.

## Experiment-local conditions (no production-contract widening)

1. **B0: frozen reference.** Regenerate adopted 0.5 s Core #69 baseline independently, recording exact committed scientific oracle/digest and pinned execution environment. No old experiment source file or waveform is overwritten.
2. **R1: single-run round trip.** Construct one continuous 1.00 s LF source from the original pulse formula and the continuous 100 Hz oscillator phase. Construct one global task-geometry timeline; call the existing renderer once for the entire signal (its *internal* overlap-add is allowed). Apply one global 10 ms onset and one 10 ms terminal envelope; do not concatenate or crossfade two 0.5 s rendered files. Preserve the fixed source family and pulse calibration; record any implementation changes needed only to support the longer source as separate audited experiment-local code.
3. **R1-ref: discretization comparator.** Same continuous source and analytic schedule, finer control and acoustic hop; no retuning.
4. **C0: naive two-render concatenation.** Deliberate negative-control **diagnostic only**, never the accepted physical waveform or a supported live capability.

The existing backend uses a windowed short-time frequency-domain transfer, not a wave-PDE integrator. Therefore “one run” establishes only continuous input/control/source phase and one renderer call with shared overlap-add accumulation, **not** dynamical memory of acoustic pressure or tissue displacement.

## Predeclared machine gates

- **G0, frozen reference:** regenerated B0 must pass every existing adopted Core #69 and Experiment 027/029 oracle/check, including no-fallback semantics. Do not overwrite baseline data or silently bless new hashes.
- **G1, schedule/representation:** exact analytical values above at listed anchors (absolute error ≤1e−12); exact 0→1→0 per task; task identity/location/degree/field unchanged; no section-area vector, formant target, or waveform embedded in the canonical task definition. Emit sampled and analytical activation CSV and versioned provenance.
- **G2, realized geometry:** every area finite and strictly positive. At t=0 and t=1, the realized area vector agrees with calibrated `/a/` (`rtol=1e−12, atol=1e−15 m²`); t=.50 s agrees with frozen Experiment-027 task endpoint by the same tolerances. Check P1/P2/P3 sampled every 10 ms and its endpoint acoustic error against the frozen Experiment-027 reference; `/i/-like` midpoint normalized P1/P2 target error ≤0.20. The first five static endpoint peaks must agree with independent adopted 0.25 Hz-grid oracle within 0.5 Hz.
- **G3, time/acoustic stability:** max adjacent 10 ms P1/P2 trajectory step divided by adopted `/a/→/i/` distance <0.20; all pressure samples finite; normalized RMS R1-vs-R1-ref difference <0.20; no clipped comparison WAV. Use the existing Experiment-026 jump-ratio definition with one **predeclared** 30 ms interval around each of 0.15, 0.35, 0.65, 0.85 s and stable-reference samples from 0.05–0.10, 0.43–0.57, and 0.90–0.95 s; maximal absolute adjacent-sample jump across transition windows divided by the maximal absolute stable-reference jump must be <3.0. Publish individual window ratios, not only the maximum. These are engineering guardrails, **not perceptual thresholds**.
- **G4, source and single-run provenance:** one uninterrupted pulse-phase trajectory across all interior task boundaries; recorded source cycle-boundary jump/RMS <0.01 away from file edges (adopted Experiment-026 style). One source build and one full-duration accepted render (diagnostic comparator excluded). Check 48,000 samples and, if preroll renderer is unchanged, 196/391 transfer calls. Save raw pressure separately from playback-normalized WAV, trace, solver/NumPy revision, seed, task digest, artifact digests, and number of physical/acoustic calls. Independent identical run/environment/seed yields identical declared content digests; floating-point cross-environment bitwise equality is not assumed.
- **G5, no false phonetics:** no outcome label claims `/a i a/` as a correctly perceived Japanese utterance without separate listener data. Do not promote this pilot to arbitrary Script/Direction or Studio contracts.

A failed G0–G4 is recorded as **REFERENCE_DRIFT**, **REPRESENTATION_OR_SCHEDULE_MISMATCH**, **PHYSICAL_ENDPOINT_FAILURE**, **NUMERICALLY_UNSTABLE**, **SOURCE_OR_PROVENANCE_FAILURE**, or **UNSUPPORTED**, as appropriate; do not change preregistered thresholds in place. If actual mechanical/acoustic state continuity is claimed, the correct result with this backend is **UNSUPPORTED**, not a passing test.

## Listening gate (independent from physics)

Archive named randomized A/B previews only after objective metrics are frozen, with matching playback level reported transparently (RMS equality ≠ equal perceived loudness). Ask, separately: free kana transcription without prompts; perceived vowel ordering; transition discontinuity; buzzing/harshness; naturalness; enjoyment. Store ordering/seed, rating scale and all individual responses before unmasking. A single listener is exploratory pilot evidence, not a population validation. Aesthetic failure does not erase a numerically valid physical result.

## Decision and scope of next PR

**If G0–G4 pass:** `SUPPORT_ONE_RUN_ROUNDTRIP` — supports only a stable and reproducible 1.0 s **quasi-static task geometry + windowed acoustic rendering** round trip. Acoustic/perceptual quality is a separate decision.

**Otherwise:** publish the failed gate and artifacts without retuning; distinguish `MORE_DATA` for missing human observations. Do not amend production `CreatureSpec`, `GestureScore`, `Performance Contract v0` or Studio. Do not copy an unsupported source into a purported physical result.

Next change should be **one experiment-local implementation Draft PR** with independent oracle, software/scientific CI, generated audio and review. V4-B (#76) must later independently establish actual finite-time mechanical state `q, q̇` and its consequences on geometry/sound. MotorPersona (#75) and neural correction (#43) are not part of this gate.

## Evidence and references

- Adopted Experiment 027 [preregistration](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/027_task_field_vowel_transition/PREREGISTRATION.md) and [results](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/027_task_field_vowel_transition/RESULTS.md).
- Actual static↔stateful reduced-order contrast: [Experiment 020 results](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/020_stateful_finite_time_realization/RESULTS.md). This successful isolated experiment is **not** in the V3 live waveform path.
- Windowed acoustic code: [Experiment 012 `frame_render`](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/012_source_renderer_artifacts/run.py); task-field driver: [Experiment 027](https://github.com/ryonakayama234/morphoacoustics/blob/main/experiments/027_task_field_vowel_transition/run.py).
- Browman & Goldstein (1992), articulatory gestures and overlap: https://pubmed.ncbi.nlm.nih.gov/1488456/ . The paper motivates later motor-coordination tests, **not proof from this round trip**.
