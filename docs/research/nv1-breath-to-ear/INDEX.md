# NV1-EAR / Core — research design index

Status: **DESIGN-ONLY / PLANNED / NOT IMPLEMENTED / NOT ADOPTED** (2026-10-21).

Owner issue: [Core #133](https://github.com/ryonakayama234/morphoacoustics/issues/133); paired creator flow: [Studio #22](https://github.com/ryonakayama234/morphoacoustics-studio/issues/22).
Ancestors: [nonvocal #53](https://github.com/ryonakayama234/morphoacoustics/issues/53), [aspiration #30](https://github.com/ryonakayama234/morphoacoustics/issues/30), [listener Draft #83](https://github.com/ryonakayama234/morphoacoustics/pull/83), [EL-G0 #114](https://github.com/ryonakayama234/morphoacoustics/pull/114), [EL-G0a #129](https://github.com/ryonakayama234/morphoacoustics/pull/129).

Canonical query routing:
- [SYSTEM.md](SYSTEM.md): Gesture vs source vs receiver; typed body graph; boundary and future breathy phonation.
- [DATA.md](DATA.md): research-only requests, traces, manifest, SI, provenance, invalid cases.
- [EXPERIMENT.md](EXPERIMENT.md): executable work packages and audition matrix.
- [PREREGISTRATION.md](PREREGISTRATION.md): **proposed pre-code design freeze** with model, controls, expected analytic oracles and pass/fail gates. Amend with a dated addendum before any code if an assumption must change.
- [RESULTS.md](RESULTS.md): append-only evidence/decisions, currently no NV1 execution.

Branch base (checked on 2026-10-21): PR #129 head `f232592738befa5a0bd0a279318365e7a74c83fc`. This design PR is stacked upon PR #129 *but does not imply approval of its unresolved SOFA receiver-coordinate/reference-plane audit*.

**Research objective:** The creator can perform at least two bounded, physically distinct exhalations and hear newly generated reproducible 48 kHz stereo breath-like audio; traces show the respiratory control -> flow -> stochastic acoustic equivalent source -> propagation/receiver chain. For the Studio, the exact Core code SHA must be pinned.

**Non-goals:** production CreatureSpec/GestureScore/Performance Contract changes; full organ-graph authoring, phonemes, glottal fold oscillator, realistic /ha/ or /fu/, near-contact 1 cm, wet/contact physics, calibrated SOFA B Pa/SPL, perceived ASMR superiority, automatic adoption or main merge. Prior chat demonstration WAVs are *not* scientific results of this source model.

Research adoption, API adoption and main integration are **three separate future decisions**.
