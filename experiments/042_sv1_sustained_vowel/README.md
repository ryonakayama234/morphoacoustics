# SV-1 — Sustained Vowel Performance (Core only)

**Status: DRAFT / PRE-ADOPTION RESEARCH.** Task: [Core #124](https://github.com/ryonakayama234/morphoacoustics/issues/124), parent [Studio Voice Atelier #16](https://github.com/ryonakayama234/morphoacoustics-studio/issues/16). The earlier Studio Scene Composer proposal SC-1 remains a downstream idea, not the task here.

## Creative outcome

Compare independently rendered **0.25-second single /a/-like sustain (A)**, **0.50-second single /a/-like sustain (B)** and **two completed A clips concatenated into 0.50s (C; diagnosis only)**. Creator's percept of "one held あー" versus "two あ, あ" is an independent human Gate.

A/B have independent prescribed LF source flow and fresh computed physical pressure through the *same* vocal tract, not stretched, looped or concatenated old WAVs. This is NOT breathing, glottal contact, tissue dynamics or actual self-oscillating vocal folds.

## Architecture and data flow

~~~mermaid
flowchart TD
    E["Experimental SV1 duration: 0.25 or 0.50s"]
    P["Adopted exact CC-A2 M0@1 body + frozen preflight"]
    S["Experiment013 LF: 100Hz Rd1; one phase / 10ms envelope"]
    G["Experiment023 /a/ static rest geometry"]
    R["Fresh Experiment023 render_static / Experiment012 frame_render"]
    O["Raw pressure Pa.npy + WAV + source NPY + trace + SHA"]
    C["C: DIAGNOSTIC A+A PCM splice, never one physical run"]
    L["Blind trials 01, 02, 03"]
    X["Creator listening, separate Gate"]
    P --> G
    E --> S
    G --> R
    S --> R
    R --> O
    O --> C
    O --> L
    C --> L
    L --> X
~~~

Core owns body, source, physical acoustics and provenance. Studio remains unchanged, responsible for creative controls, Take comparisons, and future scene composition. No new production Performance Contract surface.

## Conditions

| Property | A | B | C (diagnostic) |
| --- | --- | --- | --- |
| Physics | one fresh source + render | one fresh source + render | none: completed A WAV PCM repeated |
| Duration | 0.25s | 0.50s | 0.50s |
| Frames | 12,000 | 24,000 | 24,000 |
| Source | 100Hz LF Rd1, one phase | same, matches old 0.5s LF fixed source exactly | file envelope starts/stops twice |
| Body | exact CC-A2 16cm M0@1 static /a/ | same | no new body run |
| Playback | normalized 48kHz mono PCM16 | same | labeled negative control |

**Static /a/ M0 resonance oracle is P1=720.25, P2=1288.50 Hz** from the accepted Experiment028 Wolfram reference, with absolute 0.25Hz tolerance. The older draft Issue initially confused these with 275/2101.75 Hz (/i/-like task endpoint); this was transparently corrected on Issue #124 **before SV-1 execution**.

The inherited 10ms source-amplitude envelope denotes imposed file fade-in/out, not physically solved phonation onset/offset or Experiment027 task activation. A/B share byte-identical source float64 inside the 0.05s-to-0.15s steady common region. Their raw pressure and playback WAV are computed separately; listening WAV is normalized, NOT calibrated sound pressure.

## Acceptance gates

1. A/B exact samples, finite nonzero raw pressure, one monotonic LF phase trajectory each, file envelope only at ends, no internal envelope retrigger. Source steady segment matches between A/B. Equal geometry and source parameters.
2. Reuse adopted CC-A2 exact prepared body and transitive frozen scientific/NumPy gate; /a/ static resonance matches independent Wolfram reference. One real acoustic calculation per A and B, no WAV post-processing as physical evidence.
3. Byte reproducibility on repeated execution: float64 source, pressure, PCM, receipt digests; exact playback format and full provenance. Unsupported vowel, body, revision, duration and reusing output path fail without accepted output.
4. C is NOT a physical Take. The blind listening package asks for free kana/transcription, then perceived number of starts (one/two/unknown), artifacts, naturalness and creative usefulness. Human pilot N=1 is separate from numeric pass.
5. Existing CC-A2 and full normal test suite must remain green; independent code/security/numeric/scientific-claim review is required before merge. The V4-A Draft #123 is unchanged.

**Gate distinction:** SUPPORT_DURATION_CONTROL is a possible numeric conclusion. SINGLE_SUSTAIN_PERCEPT_CONFIRMED_PILOT requires user listening. Neither means natural Japanese TTS or biomechanically demonstrated phonation.

## Run in pinned Python 3.11 environment

~~~bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install 'numpy==2.4.6'
python -m pip install -e '.[dev]'
SV1_REAL_PHYSICS=1 python -m pytest -v tests/test_sv1_sustained_vowel.py
python experiments/042_sv1_sustained_vowel/run.py --output-dir sv1-output
~~~

The parent output directory must exist and the output path must be new. Presence of the final 'manifest.json' is the completion marker. A crash without it is not evidence of success.

GitHub Actions artifacts:
- sv1-blind-listening-trials: only three anonymized WAV files; use before viewing the key.
- sv1-full-research-evidence: A/B source flow arrays, raw pressure in Pa, separate normalized WAVs, physical time traces, artifact SHA digests, C negative control, answer key and scientific manifest.

Sources: [Core Issue #124](https://github.com/ryonakayama234/morphoacoustics/issues/124), [static /a/ fixture Experiment023](../023_static_vowel_calibration/RESULTS.md), [Wolfram frozen M0 Experiment028](../028_task_field_morphology_transfer/RESULTS.md), [adopted CC-A2](../../docs/research/cc-a2-two-body-live.md), [V4-A Draft #123](https://github.com/ryonakayama234/morphoacoustics/pull/123), [speech evaluation Core #37](https://github.com/ryonakayama234/morphoacoustics/issues/37).

Future Studio duration selector and immutable physical Take are subsequent distinct tasks. Human listening and independent review must not be waived by successful CI.
