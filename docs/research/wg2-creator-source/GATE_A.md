# WG2-CREATOR-SOURCE / preregistration (2026-10-25 JST)
## Goal
Bridge accepted source and real CC-A2 M0/M1 body binding to the already-adopted WG2 static causal waveguide preview. This is the immutable, independently verifiable Core evidence source for [Studio #30](https://github.com/ryonakayama234/morphoacoustics-studio/issues/30), not an artistic quality adoption.

## Baseline identity
- Core starting source HEAD: `2b747b8e54cd302b8693f9d013f3980273bae080` (#192 merged, #187 adopted).
- Reuse *exact* verified CC-A2 prepared registry through existing `tools/cc_a2_live.py` and `_load_frozen_adapter`; validate historical Experiment028/029 source oracles and prepared morphology; `v3b-axial-M0@1` and `v3b-axial-M1@1` only.
- Reuse accepted Experiment042 SV-1's continuous Rd1, 100Hz 48k **prescribed** LF volume flow for 0.25/0.50 second, with **one source program** passed through a **fresh** WG-2 physical solver per request. No completed X2a or SV1 WAV may be read as the output, and no claim of self-oscillating vocal folds.
- This static /a/-like rest state differs from CC-A2's existing dynamic `あい` gesture; it must be explicitly labeled a static sustained /a/-like *monitor*.

## Wire and evidence
- Opt-in command `tools/wg2_creator_take.py`, bounded JSON request body id/revision/character id/duration, separate source/tract/mouth-port from UI controls.
- Required files: source float64 NPY, native mouth-pressure float64 NPY, native flow float64 NPY, observed 48k mouth-pressure float64 NPY, 48k mono PCM16 WAV, manifest with exact body binding/preparation digest, source/observer versions, numerical ledger, clock, hashes and source git commit.
- Each run recomputes from physical inputs. Output archive is new and exclusive, write/sync payload before final `manifest.json` completion marker, no merge with historical artifacts. Reuse audited SV1 publication helper and add independent tamper verification in receiving Studio service.
- M0 clock = 68600 Hz, M1 clock = 62363.636... Hz, 16×n2 only (accepted WG2 observer); 0.25s and 0.50s durations.
- Invalid body/revision/character/duration returns UNSUPPORTED, not generic WAV or alternative body. Source and body mismatches fail before audio and no successful marker.
- Freeze Gate A now; do not claim voice quality, calibrated microphone, dynamic wall motion, production TTS, or native Studio Take until real end-to-end and listening.

## Gate B acceptance
Exact new-head GHA full Python suite, physically executed M0/M1 produce distinct finite raw pressure, zero correct first-arrival, energy residual and pinned source SHA. Files/manifest recheck, deterministic same-body two runs, wrong body/revision refusal. Independent `@codex review` of exact HEAD with no unresolved P1/P2. Studio adapter has its **own** Node tests, real HTTP E2E, restart/reload and independent review before merge.
