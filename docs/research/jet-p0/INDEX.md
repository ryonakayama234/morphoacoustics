# JET-P0 — Index (research only, 2026-10-23)

**Status:** PR candidate / NOT_ADOPTED. Owner: Core research. No main merge or new public API. Parent [Core #30](https://github.com/ryonakayama234/morphoacoustics/issues/30). Complements, does not replace, [Studio #28 / Draft #29](https://github.com/ryonakayama234/morphoacoustics-studio/pull/29).

## Why
[Experiment 025](../../../experiments/025_smooth_source_spectrum_vowel_cue/RESULTS.md) established high closed-set vowel discriminability alongside buzzer-like, non-voice perception. [Experiment 013](../../../experiments/013_parametric_source_prosody/RESULTS.md) showed that naïve 2% white inlet noise strongly dominates >2 kHz *after* the current radiation surrogate. More organ/material complexity alone is not an established voice-quality fix. Test a candidate causal source mechanism instead.

## Searchable context
- [SYSTEM.md](SYSTEM.md): Core ↔ Studio path, physical authority and limitations
- [DATA.md](DATA.md): physical inputs, artifact schema and inference/observation separation
- [EXPERIMENT.md](EXPERIMENT.md): frozen hypotheses, interventions, nulls, quantitative / listening gates, evidence log
- [run.py](../../../experiments/047_glottal_jet_closure/run.py): experimental source and opt-in *existing* Core static-tract render
- [tests](../../../tests/test_experiment_047_jet_source.py): mathematical invariants

## Decisions
Do not alter adopted LF/SV-1, organ graph, Character/Performance contracts, main's CC-A2, or SMC/ASMR branches. Do not expose a "breathy character" preset until source physics, acoustic output, and human voice-likeness gates are separately assessed. Any neural closure must satisfy the already documented causal boundary.

## Post-run scientific outcome (2026-10-23)
- **Gate B failed**, not source adoption. Evidence and detailed numbers: [FAILURE_AUDIT_20261023.md](FAILURE_AUDIT_20261023.md).
- Broader creator/physics sequencing: [VOICE_LAB_ROADMAP.md](VOICE_LAB_ROADMAP.md). Selected next concrete Core task: [SA-1 #168](https://github.com/ryonakayama234/morphoacoustics/issues/168).
