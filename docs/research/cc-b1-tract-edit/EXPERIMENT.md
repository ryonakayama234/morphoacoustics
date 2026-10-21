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

## 2026-10-22 NEW Core-run prespecification BEFORE measurement
The [dated Gate A freeze](GATE_A_FREEZE_20261022.md) selects mid-tract index8, ratios 0.9/1.0/1.1, unchanged LF+GestureScore, 48kHz 0.5s, 102 calls, identical-task source SHA and endpoint task-field ratio checks. Pre-run Wolfram **ABCD and impedance recurrence** agree at 5Hz resolution for all three first rest and final resonances; values in [frozen JSON](gate_a_site08_oracle.json). Peak tolerance 7.5Hz; nonbaseline raw L2 >1e-8; baseline null/repeat both match legacy quantized SHA; invalid controls fail closed. No B data exists at this Gate A protocol commit. Internal freeze IS NOT independent science acceptance; earlier #143/#144 site exploration not relabeled confirmatory. Completion of B remains conditional on later independent audit and cannot imply perceptual audibility.

## 2026-10-22 implementation note — new Core Gate B site08 experiment
Implement new isolated runner `experiments/cc_b1_gate_b_site08/run.py`, matched unit/negative tests, exact-head physical CI with independent baseline physical replay + CC-A2 regression and raw .npy/.wav artifacts. Conditions and numerical criteria copied only from earlier frozen Gate A commit `ca8bf64c...` — not tuned to later measured Core pressure. If CI passes, record specific physical values and hashes in a further append-only experimental receipt; if it fails, preserve failure and fix cause without silently rewriting primary hypotheses. **Not an independently ratified science gate, no audited perceptual test.**

## 2026-10-22 — Actual NEW physical site08 result (first exact evidence HEAD)
- **Protocol frozen before execution:** `ca8bf64c8525a9cf59cb1332c4819763a0f9197e` (PR #149, independent science review still pending).
- **Executed Core B code HEAD:** `1be4433038fa0347f3d0bde9a5f8a97f5a765693` — [successful GitHub Actions run 39692576705](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39692576705), [raw Pa and WAV artifact 12388864048](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39692576705/artifacts/12388864048). Research-only PASS is **not science ratification**.
- **Model:** 16×10mm lossless prescribed LF / three-task, site8 0.90, 1.00, 1.10; SAME source SHA `724412c20feddd9e00112cc362bac56bd8aa428670c5dcb789461df858b512fc`, SAME task SHA `17148dea27e59abfb626b149beebcc7893d4ff9ba04ce4cf3af9ad408ce8a7bf`; NumPy 2.4.6, 48kHz×24k SI Pa each, each one physical evaluation 102 acoustic calls, four total including independent second baseline, + replayed physical tests.
- **Measured independent Core frequency peaks** (Hz) vs prespecified independent Wolfram 5-Hz-grid oracle:

| site8 ratio | Core rest peaks (Hz) | Core terminal peaks (Hz) | max rest difference | max terminal difference | raw relative L2 vs base |
|---|---|---|---:|---:|---:|
| 0.90 | 721.5,1291.5,2906.75 | 275.25,2109,3149 | 3.50 Hz | 4.00 Hz | 0.013811261347325118 |
| 1.00 | 720.25,1288.5,2918.25 | 275,2101.75,3164.75 | 3.25 Hz | 4.75 Hz | 0.0 |
| 1.10 | 718.5,1285.5,2925.5 | 274.5,2094.25,3177.25 | 3.50 Hz | 2.25 Hz | 0.01491442523042479 |

- 18/18 predesignated peak residuals ≤7.5Hz; 2/2 changed raw SI Pa >1e-8 relative L2. Exact repeat baseline final `quantized_waveform_sha256=dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e` matches adopted audited M0 and independently rerun baseline. Original and repeat f64 SHA both `86661ece1cd7a5f451b8185bad5b9578ad5ec0ccbc6da1ef5296137be79adcda` **on this one CI platform**; cross-platform f64 identity is not claimed. Three pair-shared-gain PCM16 WAVs generated from original Pa, listening normalization gain `166.21938856014953` (not SPL). All five GitHub workflows `tests`, dedicated B, SV1, OG3, OG4 reported SUCCESS for first evidence HEAD.
- SHA256 quantized per ratio: `0.90=a5f34b795b886f67f88716be53ebf50dd68731e5b4bd03f2c189a1a17a752aa1`, `1.00=dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e`, `1.10=9f359add71f68ce66a2306d7b5dd66a658b3676d54f66369269eadc71c2c8db6`.
- **Audit hardening in next exact HEAD:** B runner now pins Gate A JSON Git blob `046a26a7baf31003244e05088a2b5d19bc7af416` and checks freeze commit ancestry so valid-looking edited oracle cannot change numerical expectations; corresponding negative test and full-git-history checkout added. Further exact HEAD CI required after this ledger change; preserve first evidence commit receipt separately.
- **Qualified conclusion:** `RESEARCH_MACHINE_PASS_PENDING_INDEPENDENT_AUDIT`. Site08 previously appeared in a theoretical all-16 scan; this is a new Core *waveform* test, not a blind-site discovery. No human ABX, sound-naturalness, pressure-calibrated SPL, real anatomy FSI, Studio integration or production API acceptance. Physics/contract independent reviewer is NOT yet recorded; Gate A independent ratification and Gate B scientific sign-off remain HOLD.

