# SV-1 — Sustained Vowel Performance (Core only)

**Status: ADOPTED / GO_LIMITED on Core main in [PR #125](https://github.com/ryonakayama234/morphoacoustics/pull/125), merge commit [a499290](https://github.com/ryonakayama234/morphoacoustics/commit/a499290b549214223cfa3cb616fc288d64f51cbb). [Issue #124 final adoption receipt](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6288450396) is authoritative.** Bounded experiment, NOT a general TTS or Studio feature. Task: [Core #124](https://github.com/ryonakayama234/morphoacoustics/issues/124), parent [Studio Voice Atelier #16](https://github.com/ryonakayama234/morphoacoustics-studio/issues/16). The earlier Studio Scene Composer proposal SC-1 remains a downstream idea, not the task here.

## Creative outcome

Compare independently rendered **0.25-second single /a/-like sustain (A)**, **0.50-second single /a/-like sustain (B)** and **two separately computed 0.25s short-voice WAVs (A and C_second) concatenated into 0.50s (C; diagnosis only)**. Creator's one-shot N=1 pilot **supports both** short A (one 「あ」) and long B (one 「あーー」); the C splice remains bumpy and is not physically continuous. The apparent multiple starts in A from the original report were caused by the **external player looping** trial_03, not by synthesis. [Original report, correction and key](https://github.com/ryonakayama234/morphoacoustics/issues/124#issuecomment-6287370288).

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
    C["C: DIAGNOSTIC PCM splice of two independent renders, never one continuous physical run"]
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
| Physics | one fresh source + render | one fresh source + render | 2 separate short-voice physical renders then PCM concatenation; NO continuous combined physical run |
| Duration | 0.25s | 0.50s | 0.50s |
| Frames | 12,000 | 24,000 | 24,000 |
| Source | 100Hz LF Rd1, one phase | same, matches old 0.5s LF fixed source exactly | file envelope starts/stops twice |
| Body | exact CC-A2 16cm M0@1 static /a/ | same | 2 fresh executions with identical static body |
| Playback | normalized 48kHz mono PCM16 | same | labeled negative control |

**Static /a/ M0 resonance oracle is P1=720.25, P2=1288.50 Hz** from the accepted Experiment028 Wolfram reference, with absolute 0.25Hz tolerance. The older draft Issue initially confused these with 275/2101.75 Hz (/i/-like task endpoint); this was transparently corrected on Issue #124 **before SV-1 execution**.

The inherited 10ms source-amplitude envelope denotes imposed file fade-in/out, not physically solved phonation onset/offset or Experiment027 task activation. A/B share byte-identical source float64 inside the 0.05s-to-0.15s steady common region. To prevent per-file peak normalization from introducing a second experimental variable, both use a common scale derived from the frozen 0.50s LF source reference. This was an explicitly recorded repair after initial failed CI; see RESULTS.md and Issue #124. Their raw pressure and playback WAV are computed separately; listening WAV is normalized, NOT calibrated sound pressure.

## Acceptance gates

1. A/B exact samples, finite nonzero raw pressure, one monotonic LF phase trajectory each, file envelope only at ends, no internal envelope retrigger. Source steady segment matches between A/B. Equal geometry and source parameters.
2. Reuse adopted CC-A2 exact prepared body and transitive frozen scientific/NumPy gate; /a/ static resonance matches independent Wolfram reference. One real acoustic calculation per A and B, no WAV post-processing as physical evidence.
3. Byte reproducibility on repeated execution: float64 source, pressure, PCM, receipt digests; exact playback format and full provenance. Unsupported vowel, body, revision, duration and reusing output path fail without accepted output.
4. C's two short voice components each have freshly computed source/pressure, including separately archived C_second arrays; C's *joined audio* is NOT a single physical Take. The blind listening package asks for free kana/transcription, then perceived number of starts (one/two/unknown), artifacts, naturalness and creative usefulness. Human pilot N=1 is separate from numeric pass.
5. Existing CC-A2 and full normal test suite must remain green; independent code/security/numeric/scientific-claim review is required before merge. The V4-A Draft #123 is unchanged.

**Gate distinction:** SUPPORT_DURATION_CONTROL was validated numerically, and creator single-onset N=1 listening is positive for **A and B** on one-shot playback. C was an intentionally concatenated diagnostic and is audibly less natural; natural connected speech requires separate, preregistered study [SV-2 #126](https://github.com/ryonakayama234/morphoacoustics/issues/126). None of this proves general Japanese TTS, biomechanical phonation or population-level naturalness.

## Run in pinned Python 3.11 environment

~~~bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --only-binary=:all: --require-hashes -r requirements/sv1-physical-py311.lock.txt
python -m pip install --no-deps --no-build-isolation -e .
SV1_REAL_PHYSICS=1 python -m pytest -v tests/test_sv1_sustained_vowel.py
python experiments/042_sv1_sustained_vowel/run.py --output-dir sv1-output
~~~

The parent output directory must exist and the output path must be new. Presence of the final 'manifest.json' is the completion marker. Publication uses O_NOFOLLOW + exclusive file creation under an open output-directory file descriptor, with a fsynced staged manifest made visible atomically via an exclusive hard link; a directory-path symlink swap cannot redirect writes to overwrite another file. The parent directory should still be trusted (this is not a multi-tenant sandbox). A crash without it is not evidence of success.

GitHub Actions artifacts:
- sv1-blind-listening-trials: only three anonymized WAV files; use before viewing the key.
- sv1-full-research-evidence: A/B source flow arrays, raw pressure in Pa, separate normalized WAVs, physical time traces, artifact SHA digests, C negative control plus independently rendered C_second source/pressure, answer key and scientific manifest.

Sources: [Core Issue #124](https://github.com/ryonakayama234/morphoacoustics/issues/124), [static /a/ fixture Experiment023](../023_static_vowel_calibration/RESULTS.md), [Wolfram frozen M0 Experiment028](../028_task_field_morphology_transfer/RESULTS.md), [adopted CC-A2](../../docs/research/cc-a2-two-body-live.md), [V4-A Draft #123](https://github.com/ryonakayama234/morphoacoustics/pull/123), [speech evaluation Core #37](https://github.com/ryonakayama234/morphoacoustics/issues/37).

Future Studio duration selector and immutable physical Take are subsequent distinct tasks. The creator's single-listener pilot has occurred and is recorded separately from the original CI manifest, which historically says NOT_RUN at generation time. Independent review and accepted scope must not be waived by successful CI.

### Evidence chain and trust boundary

The dedicated CI runs on every push/PR even when a transitive Experiment009/012/013/026/027/028/029/CC-A2 source changes. Its actions/checkout, setup-python, upload-artifact are pinned to official immutable commit SHA values (see workflow). For Python3.11, the hash-locked requirements file verifies all installed wheel archives; the local editable Core install uses no dependency resolution or build isolation. Standard test CI is independent and not replaced.

The manifest's local SHA inventory checks *internal* byte consistency, **not authenticity** against a hostile re-packager. To verify provenance of a distributed copy, cross-check the expected git commit, exact GH Actions run URL, GitHub-hosted artifact archive SHA-256 (recorded in Issue #124) and the archive's manifest/payload hash inventory against the authoritative GitHub run. Independent cryptographic attestation/signature for offline copies is **not implemented**; do not claim this form of authentication. The human listening and external code/security review gates are still required.
