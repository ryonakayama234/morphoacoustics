# CC-B1 spatial probe after a no-distinction listening report

**RESEARCH ONLY. POST-HOC SITE SCREENING; NOT PROSPECTIVE GATE B; NOT IMPLEMENTED IN STUDIO; DO NOT MERGE TO MAIN WITHOUT REVIEW.**

A creator informally reported inability to hear a difference among three CC-B1 section-0 (±10% area) previews. This is **one unblinded individual observation** without standardized playback conditions. Unlike the earlier experiment's computational "waveform changed" Gate, this is a user-facing **negative/indeterminate perception finding** and the reason for the revision.

The original physical effect was approximately 15 Hz over the two ±10% area variants at the final /i/-like second resonance (~2100Hz), with first resonance essentially unaffected. An independent [Wolfram 16-site scan](wolfram/spatial_sensitivity.wl) at the **exact same 5Hz-grid ideal 16-tube model and exact terminal task field** predicted:

| Zero-based changed section | final-state F2 at area x0.9 / x1.1 | span |
| --- | --- | --- |
| 0 (prior) | 2110 / 2095 Hz | 15 Hz |
| 2 (new follow-up) | 2130 / 2075 Hz | 55 Hz |
| 4 (new follow-up) | 2065 / 2130 Hz | 65 Hz |

**These sites were selected after inspecting the spectral model. They cannot count as unseen prediction confirmation.** The spatial scan is a diagnostic, not a procedure for optimizing a speech signal post hoc.

## A bounded genuine physical rerun, not filtering old WAV

`run.py` uses the exact already pinned CC-A2→Exp029→Exp027 LF physical generator and 16x10mm tract. It changes **one rest cross-section of one new body per condition** (sections 0, 2, or 4) by +10% or -10%, plus unchanged baseline; in total seven new 0.5 s 48kHz mono raw-Pa pressure traces. Every time-series uses the same source sample stream and 3-task plan. Evaluate physically, verify the baseline quantized pressure oracle, input validity, every moving-body section ratio, 102 real acoustic calls and numerical correspondence to the exploratory independent Wolfram F2 reference (±7.5Hz). Neither amplitude automation nor synthetic equalization changes the raw physical sound.

For self-consistent audition the runner writes 7 WAVs with **ONE shared playback gain across all conditions**, plus 7 raw float64 NPYs and SHA-bearing decision.json. Names `s00_090.wav`, `s02_090.wav`, `s04_110.wav` identify conditions, making this an **UNBLINDED demo**. No one should call it ABX or listenership validation.

## Run

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install "numpy==2.4.6"
pip install -e ".[dev]"
SPATIAL_PHYSICS=1 python -m pytest -v tests/test_cc_b1_spatial_probe.py
python experiments/cc_b1_spatial_probe/run.py --output-dir /tmp/new-cc-b1-spatial
```

Re-running the same output directory is forbidden. Source pin and NumPy version must match or the runner aborts. All new SHA identities and precise physical F1/F2/core raw L2 measurements are recorded only after a genuinely completed CI run.

## After this screen

Collect creator listening informally first, then independently preregister a later-blind test with controlled hardware, randomized labeled three-interval ABX, identical null controls, and genuine positive controls. Predefine balanced trial count and chance-level statistics; preserve listening responses before unblinding. There is NO rationale for advancing production Studio BodyRevision while perceptual distinguishability and human-sounding voice quality remain unproven.
