# Experiment 031 — F0-only source intervention (preregistered)

**Registration date:** 2026-10-11. **Status:** preregistered research only; not implemented/adopted at registration. Tracking: Core [#71](https://github.com/ryonakayama234/morphoacoustics/issues/71); creator gate: Studio [#17](https://github.com/ryonakayama234/morphoacoustics-studio/issues/17). This registration is committed **before** the implementation, test results, physical listening, or condition reveal.

## Motivation and claim boundary

Experiment 030, LF Rd=1.0 vs 1.4, physically regenerated source and pressure but the 2026-10-09 condition-masked N=1 hearing result found only a possibly slightly milder sound with **small/uncertain distinction**. That source-shape variant is **not adopted**. For a new, independent manipulation, test whether changing only LF periodic excitation **F0** gives a traceable acoustical contrast and a useful *audible* contrast for a creator. F0 influences pitch; it is **not** a solution for buzziness, breathiness, vocal emotion, perceived gender or naturalness.

This experiment changes **F0=100 Hz to F0=120 Hz**, nothing else, at the adopted Experiment 029 frozen physical /a/→/i/-like timeline. F0 here specifies prescribed periodic source excitation, **not** self-oscillating vocal-fold dynamics, tissue FSI or a claimed human phonation mechanism.

## Registered conditions / nuisance controls

| | S0 | F1 |
|---|---|---|
| F0 | 100 Hz | 120 Hz |
| LF shape | frozen Rd=1.0 | identical Rd=1.0 |
| body | V3c PreparedMorphology M_plus | same object and geometry |
| task/gesture | same frozen 3-task /a/→/i/-like | same |
| simulation | Experiment 029 evaluate_condition; 102 actual transfer calls | same path, independently executed |
| fixed | 48,000 Hz; 0.5 s; 24,000 samples; deterministic envelope; peak flow normalization; seed0-like fixed state | same |

- Source period counts predicted from Wolfram: **50 and 60 periods** in 0.5 seconds, at **480 / 400 samples** per nominal cycle, respectively. The full-clip Fourier grid spacing is 2 Hz; a 0.10-s window resolves 10 Hz bins. Those are arithmetic expectations, not validation.
- Identical physical geometry endpoint and feasibility required. The source *flow waveform* differs, as must the independently regenerated *pressure waveform*, but one cannot infer a pleasing timbre difference from distinct hashes alone.
- S0 is reconstructed using the source function and must be **bitwise equal** to the adopted `lf_fixed` Experiment 013 reference. S0 pressure must match Experiment 029's portable 1e-9 Pa quantized SHA-256 oracle **dc14c78bcc6d4a19c11fe2a01ba84b1394802b66626f4dfa27cc582c741e714e**.
- Reuse only the frozen Experiment 029 acoustic renderer, source envelope, normalization, body and gesture timeline. Do not alter `limited_live.py`, the audited Core reference, Studio v0 request schema, or claim this is a general live-voice F0 control.
- Source LF parameter tuple (`rd,ra,rk,rg,tp,te,ta,alpha,balance`) must remain equal across conditions. F0 array must be strictly 100/120 Hz, respectively; no playback pitch-shift, EQ, spectral tilt tuning, formant shift, speed-up, phase-vocoder or global effort control.

## Preregistered hypotheses and non-success outcomes

- **H1 (physical):** Changing the F0 *source generator input* only, with identical phonatory LF shape/body/task/solver, yields auditable different source and pressure waveforms. Require two feasible runs, 102 actual transfer calls each, same geometry endpoint, 24,000 finite samples, distinct full-precision output and 1e-9 Pa quantized pressure hashes.
- **H2 (auditory; separate):** A human listener can reliably tell the two newly regenerated conditions apart in a blinded, loudness-checked comparison, without reducing /a/→/i/-like identification or continuity. First N=1 preference and identification are exploratory and **not** population evidence or sufficient adoption; if no reliable preference/discrimination, record **INCONCLUSIVE/REJECTED**, do not auto-adopt.
- **H3 (quality; exploratory):** It is not known whether the altered F0 is more pleasant, less harsh, brighter, or more character-appropriate. No direction-of-improvement prediction is asserted. Negative and null results are preserved.

## Measurement and acceptance plan (before outcomes)

1. Refuse non-audited environment: `numpy==2.4.6`, frozen Experiment 029 and transitive source import, exact S0 source equivalence and quantized S0 pressure signature.
2. Record configured source F0, nominal integrated cycles, LF shape parameters, unchanged peak source volume-velocity, playback envelope, all source/pressure float64 and quantized digests, body endpoint, per-condition acoustic transfer-call count and actual WAV/NPY SHA-256. For sanity, report 0.1-second Hann source/pressure spectral regions `a_like=0.12–0.22 s`, `i_like=0.32–0.42 s`, bins `80–600, 600–1500, 1500–3000, 3000–6000, 6000–10000 Hz`, label apparent pitch separately from spectral envelope.
3. Produce exactly **two fresh, independently calculated 48-kHz mono 16-bit PCM WAVs** at equal scalar playback RMS to within **0.005 dB**, with peak <= 0.85. Store original pressure in Pa; linear playback scaling is **not** physical vocal effort, SPL or perceptual loudness equality. No filtering or pitch shifting of finished WAV.
4. Use a **masked A/B packet** with randomized/counterbalanced order and separate answer key. Lock transcription, continuity, harshness/buzziness, perceived pitch, perceived loudness, enjoyment/preference and trial ID **before** reveal. Listening must be by the creator; CI and spectral diagnostics cannot substitute.
5. Separate independent scientific/code review must inspect the sole-change claim and frozen baseline. Do **not** expose a production preset or Studio #17 until an explicit Core adoption decision exists.

## Release status vocabulary

`NUMERIC_PASS`: controlled physical calculation and evidence checks passed. `HUMAN_PENDING`: no adequate listener data yet. `ADOPT/REJECT/INCONCLUSIVE`: explicit reviewed research decisions; `NUMERIC_PASS` **never implies** `ADOPT`.

## Background

- Fant et al. (1994), LF source parameters: https://www.isca-archive.org/icslp_1994/fant94_icslp.html
- [Core Experiment 029](../../experiments/029_task_field_embodied_infeasibility/README.md) — frozen V3c prepared-body and V3 acoustic evaluation basis.
- [Core Experiment 030 draft](https://github.com/ryonakayama234/morphoacoustics/pull/73) — different causal intervention, never silently promoted here.
