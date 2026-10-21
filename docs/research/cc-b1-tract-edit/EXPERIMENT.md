# CC-B1 — EXPERIMENT / prospective research ledger
**Status 2026-10-21: DESIGN ONLY / NO CC-B1 CORE RUN / NO PREREGISTERED GATE / NO HUMAN AUDIO GATE.** This file explicitly separates preflight reasoning from measured Core evidence.

## 2026-10-21 theoretical preflight, Wolfram independent algebra (NOT a CC-B1 experiment)
For a **different simplified example**: two lossless equal-length 1D cylindrical ducts in series, each L=0.08 m; speed c=343 m/s, A1=3e-4 m²; right outlet pressure release. From 1D transfer/input impedance, the first input-impedance resonance obeys
`tan(k L1) tan(k L2)=Z1/Z2=A2/A1` for `k=2πf/c`, `Zi=ρc/Ai`.
Here `L1=L2=L`, so `f_1(A2)=c atan(sqrt(A2/A1))/(2πL)`.
Wolfram Language evaluated these algebraic values:
- A2=0.00015 m² -> **419.98908545780716 Hz**
- A2=0.00030 m² -> **535.9375 Hz**
- A2=0.00060 m² -> **651.8859145421928 Hz**

This is merely a **sanity-check** that a local area change can change physical resonances; it is **not** the 16-section CC-A2 body, Experiment018 implementation, an audited independent prospective Oracle, a frequency sweep, or evidence of new voice quality. It cannot be used as a PASS for the planned Gate B.

## Proposed H_CC-B1
With source, seed, fixed 3-task GestureScore, duration, 16-section geometry except one frozen rest area, backend and observation fixed, one physical area edit produces independently predicted/causally attributable resonant and new raw-pressure differences. Same-body null gives identity. Studio can distinguish the exact immutable body versions and preserve both fresh physical Takes. This may hold **without improving voice-likeness**.

## Future Gate A, BEFORE new trial
- Freeze which existing **validated baseline** and exact solver SHAs are used; choose one section after inspecting task-field deformation and safe positive rest geometry.
- Freeze fixed area candidates (e.g., 0.9/1.0/1.1 *baseline* are only initial proposals), range and units, noise/seed, source/time grid, oracle frequencies, time-domain metrics, diagnostic checks and tolerance budget.
- Design independent transfer-matrix/global pressure-flow oracle with unobserved holdout cases **before** Core code and results. Include ill-conditioning, energy/power and moving-boundary legality: existing 1D moving filter must be checked in its own verified scope, not declared fully passive FSI.
- Prespecify separately (A) objective physical outcome, (B) audio A/B discrimination, (C) subjective voice-likeness/noise/artifacts and usability. Negative outcomes remain archived.

## Gate B–E TODO: immutable experiment receipts
- **Gate B Core:** original/edited/same-body-null, independently rebuilt oracle, exact byte reruns, verified source and GestureScore invariant, pressure trace and frequency change, finite/stability/capability refusals, wrong-section and hidden-fallback mutants. Record exact SHA, CI, NumPy/Wolfram versions, generated raw pressure SHA, reference conditions, error margins and failures here.
- **Gate C API:** only if objective Gate B and independence reviews pass; design exact revision creation/preparation and immutable result schemas before wiring Studio.
- **Gate D Studio:** fresh A/B physical WAVs, immutable historical Takes with reload/restart, human *one-shot* listen (difference/quality/usefulness are different questions).
- **Gate E decision:** explicit GO_LIMITED / REVISE / MORE_DATA / REJECT, named reviewed exact commits, CI and remaining limitations. A docs-only PR is **not** physical acceptance.

## Historical anchors
[Exp018](../../../experiments/018_local_area_morphology_sensitivity/RESULTS.md) supports only a static 10-section local rest-area perturbation. [Exp025](../../../experiments/025_smooth_source_spectrum_vowel_cue/RESULTS.md) reports buzzer-like quality despite 29/29 answered closed-set vowels. Do not replace a naturalness experiment with spectral novelty.

## 2026-10-21 second analytical preflight — real 16-section formulation
New independently assembled Wolfram 16-tube transfer products used Experiment023 /a/ diameters (glottis→lips), length 10mm each, 343m/s, rho=1.2, terminal pressure release, 100–3500 Hz / **5Hz exploratory grid**. For the full-activation Experiment027 field, used exact task locations/degrees/kernel widths, log-area delta=2×log-diameter delta. `p_in/U_in=M_12/M_22`. This independently reproduces coarse baseline modes from adopted previous oracles, but its assumptions are not full human voice or new blind prediction. Table: first three local |input impedance| peaks in Hz.

| zero-based section-0 rest area ratio | rest peaks, Hz | final three-task peaks, Hz |
|---|---|---|
| 0.90 | 720,1295,2920 | 275,2110,3165 |
| 1.00 | 720,1290,2915 | 275,2100,3160 |
| 1.10 | 715,1285,2915 | 275,2095,3160 |

The **first low resonance is unchanged on this coarse 5-Hz grid at the final gesture**, whereas higher peaks move: do not cherry-pick an expected monotone response of every mode. This remains known/post-hoc exploratory preflight, not preregistered future holdout. [Wolfram source](../../../experiments/cc_b1_rest_area_pilot/wolfram/cc_b1_exploratory_16section.wl), [JSON](../../../experiments/cc_b1_rest_area_pilot/wolfram/cc_b1_exploratory_16section.json).

## Exploratory Core pilot addition — execution status distinct from plan
A standalone 16-section runner now proposes actual 48 kHz 0.5s **fresh** raw Pa outputs for 0.90/1.00/1.10 with existing exact Experiment029 frozen source/realizer; checks baseline quantized M0 oracle, area-ratio persistence across gestural time, expected 102 acoustic calls, local 16-tube oracle (coarse 5Hz tolerance 7.5Hz), nonzero same-source raw pressure L2 for edited states and no-fallback. New `tests/test_cc_b1_pilot.py` and dedicated CI accompany it. **Pending CI results here must not be advertised as passed until a real run is inspected.** Gate A independent ratification, new unseen confirmatory oracle and speech-like perceptual Gate remain pending. No Core/Studio production API is adopted.

## 2026-10-21 genuine exploratory CI (run before adding preview WAVs)
**Completed machine evidence, NOT prospective scientific Gate acceptance**: [Actions 39580500879](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39580500879), exact HEAD `c8a42720f54c9a20f2ce1fb8bed08c6185c06853`, job 119156622189, `cc-b1-exploratory-evidence` artifact ID 12336058554, ZIP SHA256 `1b18c6961501ec8feca090805f5fb409569c7e6f61f8daeeee53cebf097e5d7a`, Python 3.11.17 + pinned NumPy 2.4.6. Dedicated 3/3 CC-B1 tests, fresh standalone run, and 7/7 adopted CC-A2 regression tests passed; 3 independently new raw Pa streams × 24000 samples were archived. Same frozen input `lf_fixed` source SHA256(le-f64) `724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc` and identical 3-task plan. Baseline quantized pressure SHA matched adopted Experiment029 (`dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e`).

| section0 rest-area multiplier | relative raw Pa L2 vs 1.00 | observed final peaks (Hz) | raw float64 LE SHA256 |
|---|---:|---|---|
| .90 | 0.0333967011 | see archived decision.json | `2e03a7d757084d7bc086c20d5a48605e8791bde515352fb5874f9af3f1f82375` |
| 1.00 | 0 | 275.0, 2101.75, 3164.75 | `86661ece1cd7a5f451b8185bad5b9578ad5ec0ccbc6da1ef5296137be79adcda` |
| 1.10 | 0.0315043129 | 274.5, 2095.0, 3163.0 | `ddbf488cece554ea4f38bf6bc3f2bc3ccc66db098a316387a3bcce5b2e6edc0e` |

The 16-tube independent Wolfram 5Hz reference compared against Core 0.25Hz-grid peak extraction: maximum error across all **six rest/final cases** ≤4.75Hz versus declared exploratory ≤7.5Hz. Difference in raw waveform **does not certify audibility, quality or real tissue physics**. The 0.90/1.10 waveforms are newly generated and not human-reviewed. Follow-up WAV preview code and its CI are separate unconfirmed work until new run finishes. The frozen research audio output policy requires one common normalization factor and no playback EQ; raw Pa hashes may not be rewritten.

## Multi-run nuance and audible preview provenance
After the initial CI, subsequent preview-equipped [exact implementation HEAD d6a84220a61b250a2c245b935a92ac097d5c5e4a](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39581011629) passed all 3 CC-B1 research tests plus 7 existing CC-A2 tests. It produced **seven archive files**: three new raw Pa NPYs, three mono 48kHz PCM16 preview WAVs, and decision.json; [artifact 12336158951](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39581011629/artifacts/12336158951), ZIP SHA-256 `9387815df2ba6dcf8018e50713520c95b513e714716a7535e9388c6726410de6`. The WAVs use one pair-shared gain, tested as PCM-derived from raw Pa, NOT sound calibrated to physical SPL and NOT a Studio Take. This validates software/audio encoding and actual physical causality, **not human distinguishability or natural voice**.

**Portability disclosure:** GitHub CI build at the first exploratory HEAD yielded float64 raw source SHA256 `724412c2...`; a later CI host produced `4d075fd8...`, while the exact frozen generator/source implementation, 3-task plan and baseline *quantized pressure* identity remained accepted. This repeats the known NumPy SIMD byte-level source portability issue recorded in Experiment028. The first run's full source SHA cannot be asserted universally across host architectures. Each within-run three-body condition uses the **same** source bytes; record implementation, environment and raw SHA separately, and do not mistake source-byte reproducibility across SIMD machines for a physical invariant.

## Creator listening feedback triggers REVISE / MORE_DATA (2026-10-21)
The creator listened to the three previous CC-B1 research WAVs and reported that the variants sounded indistinguishable. The review is **one informal, non-blind, uncontrolled playback report**, not a preregistered ABX, listening population result, nor evidence the physics failed. It is a meaningful **failure to demonstrate an audible new character difference for this creator**. Previous software gate proved relative raw Pa L2 changes ~3.34% and ~3.15%, but raw L2 is neither dB sound-pressure difference nor auditory detectability; absolute residual vectors are approximately −29.53dB/−30.03dB relative to the baseline *signal norm*.

An independent post-hoc Wolfram [all 16 sites, exact same ideal 16-tube transfer matrix and frozen three-task end-state](../../../experiments/cc_b1_spatial_probe/wolfram/spatial_sensitivity.wl) found these 5Hz-grid F2 mode spans for one site changed ×0.90 versus ×1.10: section0 15Hz (0.71%), section2 55Hz (~2.62%), section4 65Hz (~3.10%), section5 40Hz (~1.90%). Section11 generated the largest coarse-grid F1 span, 10Hz, but no guarantee of audibility. [All-site data](../../../experiments/cc_b1_spatial_probe/wolfram/spatial_sensitivity.json). Local acoustic sensitivity varies by section and by formant; selection of sites2/4 was **made after looking at scan data** and must never count as independent confirmation.

In the prior experiment the entire sound source used 100Hz F0 (harmonics spaced 100Hz) and duration 0.5s. Small resonance movements may be poorly reflected by discrete harmonic amplitudes or masked by other aspects of the timbre, but no specific masking cause has been diagnosed from listener-labeled trials. Human perception research: Kewley-Port & Watson (1994), [formant-frequency discrimination of synthesized vowels](https://pubmed.ncbi.nlm.nih.gov/8120259/), reported ~14Hz threshold in an F1 (<800Hz) region under trained/minimal-uncertainty conditions and increased thresholds in F2; Smith et al. (2004), [vowel formant discrimination in high-fidelity naturalistic speech](https://pubmed.ncbi.nlm.nih.gov/15376687/), observed ~0.37 Bark average in modest sentences, which should **not** be directly imposed as a criterion on this buzzer-like signal. Separate Core [Experiment025](../../../experiments/025_smooth_source_spectrum_vowel_cue/RESULTS.md) already documented human report that accurate closed-set phonetic cues still sounded buzzer-like.

**Revised exploratory next test**: [7-condition full physical spatial-run](../../../experiments/cc_b1_spatial_probe/README.md) on a stacked new Draft PR; same exact source/task and all other geometry, site0/2/4 ×0.9/1.1 plus null; check actual 102 acoustic calls, raw pressure and hashes, 0.25Hz-grid peak comparison to coarse Wolfram, common-gain WAV. This is a proof-of-physical-variation study, **not a preregistered sensitivity test or a passed auditory Gate**. Independently predefine and then run *future* blind creator ABX with null and a real positive control and capture response before revealing assignment. No Studio Code/Gate promotion.

## Completed post-hoc seven-body physical rerun (actual machine evidence)
2026-10-21 [GitHub Actions 39591507980](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39591507980) **PASS** at code/design HEAD `2ccb1f7ee2650a31d35d513eb791d11e60f81ebb`: 2/2 dedicated tests passed (including real seven-condition physical execution), standalone rerun passed, and 7/7 adopted CC-A2 regression passed. Seven freshly computed 48kHz/0.5s raw Pa arrays plus seven single-gain PCM16 preview WAVs + decision.json archived as [15-file artifact 12342252192](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39591507980/artifacts/12342252192); artifact ZIP SHA256 `d6a8c9d91f9553776baf32b19bdfd4a056eb23f8bdc7c9d88e5f4e4edfd90fd5`.

Core observed after exact frozen three-task motion, fixed same `lf_fixed` source within the 7-condition run and **102 acoustic calls per condition**:

| Zero-based local changed section | rest area ratio | F1 end (Hz) | F2 end (Hz) | relative raw Pa L2 distance to null |
|---:|---:|---:|---:|---:|
| null | 1.00 | 275.00 | 2101.75 | 0 |
| 0 | 0.90 | 275.25 | 2108.50 | 0.03340 |
| 0 | 1.10 | 274.50 | 2095.00 | 0.03150 |
| 2 | 0.90 | 277.75 | 2130.25 | 0.06603 |
| 2 | 1.10 | 272.25 | 2075.00 | 0.06381 |
| 4 | 0.90 | 276.00 | 2066.00 | 0.02989 |
| 4 | 1.10 | 273.75 | 2132.00 | 0.03078 |

**Important counterexample to naive peak-based ranking:** at section4, F2 span across the two ratios is ~66Hz (more than section2's ~55Hz), but its raw waveform distance to null is only ~3%, versus ~6.4–6.6% for section2. Neither single peak displacement nor global L2 distance is a valid human voice discriminability measure. The listening state remains **NOT VALIDATED**; this CI can't tell whether the creator can hear any new sounds. All FFT/harmonic amplitudes and subjective cues need future controlled testing. The exact baseline quantized raw Pa SHA matched the adopted oracle `dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e`. No signal transformation was introduced upstream of physical acoustics.

**Decision remains REVISE/MORE_DATA**, not GO. Spatial sites were chosen post-hoc; this run is exploratory screening, not an unseen independent scientific validation or natural voice demo.

### Verification model boundary: resonance oracle is not the radiated audible transfer
The new Wolfram location scan uses **input impedance `|M12/M22|` under ideal terminal pressure-release**. It is an independent **resonance-frequency location** approximation only. The actual 0.5s Core signal passes through `Experiment029 CountingTransfer -> Experiment009 far_field_pressure_transfer`, whose implementation uses a small explicit *resistive* terminal load and an approximate free-field monopole pressure observation (`U_out` radiation). Therefore high agreement of resonance **frequency** does not assert agreement of amplitudes, phase response, mouth-radiation physics, harmonic envelope contrast or auditory distinguishability. Future work should compute frequency-dependent *actual output-transfer* differences at source harmonics and over the transition, and a genuine loudness/perceptual evaluation. Source: `experiments/009_fixed_tract_waveform/run.py` and `experiments/029_task_field_embodied_infeasibility/run.py` currently adopted on Core main.
