# CC-B1 — Local Rest-Geometry Edit / research index
**Status 2026-10-21: PROPOSED / DESIGN-ONLY / UNRATIFIED; NOT IMPLEMENTED; NOT SCIENTIFICALLY ADOPTED.**
Owners: [Core #141](https://github.com/ryonakayama234/morphoacoustics/issues/141), [Studio #25](https://github.com/ryonakayama234/morphoacoustics-studio/issues/25), [Creator Epic #12](https://github.com/ryonakayama234/morphoacoustics-studio/issues/12).

## Documents (update together in every future implementation/review PR)
- [SYSTEM.md](./SYSTEM.md) — physics ownership, current vs future organ nodes and connections, Core↔Studio boundary.
- [DATA.md](./DATA.md) — immutable body revision proposal, SI units, exact provenance, refusal semantics.
- [EXPERIMENT.md](./EXPERIMENT.md) — analytical preflight, future prospective gates, measurement/evidence ledger.

## Authoritative baselines
- [Experiment018](../../../experiments/018_local_area_morphology_sensitivity/RESULTS.md): only **10-section static** rest-area sensitivity, not CC-B1 live capability.
- [Experiments027](../../../experiments/027_task_field_vowel_transition/RESULTS.md), [028](../../../experiments/028_task_field_morphology_transfer/RESULTS.md): limited 3-task /a/-like→/i/-like and axial transfer.
- [CC-A2 physical live](../cc-a2-two-body-live.md): 16-section **two exact presets** / real fresh Take.
- [Experiment025](../../../experiments/025_smooth_source_spectrum_vowel_cue/RESULTS.md): closed-set vowel cue does **not** prove voice-likeness.
- [Organ graph architecture](../organ-graph-program.md), [OG-4 bounded API](../og4-branch3-api-v1.md): separate passive graph capability.
- [OG-AUD1 #130](https://github.com/ryonakayama234/morphoacoustics/issues/130): ongoing unadopted **non-radiated pressure-monitor** E2E; do not import into speech pathway.
- SMC-1 / ASMR are independent: [#139](https://github.com/ryonakayama234/morphoacoustics/issues/139), [#133](https://github.com/ryonakayama234/morphoacoustics/issues/133).

No code has been run or merged for CC-B1. This draft documents a **proposed** capability and does not freeze Gate A or authorize widening the live contract.

## 2026-10-22 fixed prospective NEW Core-run protocol
[Gate A dated protocol](GATE_A_FREEZE_20261022.md) and paired [Wolfram source](gate_a_site08_oracle.wl) / [frozen data](gate_a_site08_oracle.json) lock zero-based section8 ×{0.90,1.00,1.10} before any new physical pressure run. **FROZEN_INTERNAL / INDEPENDENT_RATIFICATION_PENDING**, not scientific approval or main adoption. Gate B must branch from this exact freeze commit and preserve exploratory earlier studies.

## 2026-10-22 actual NEW Core physical experiment branch
[Gate B site08 runner](../../../experiments/cc_b1_gate_b_site08/run.py) + [tests](../../../tests/test_cc_b1_gate_b_site08.py) + dedicated workflow. Branches **from immutable Gate A freeze commit**; no reuse of exploratory site0/2/4 waveform as this observation. Still a *machine hypothesis pending real CI*, not independent ratification. Complete source/hash records and refusal ledger go to EXPERIMENT after exact-head workflow inspection.

## 2026-10-22 actual Gate B evidence
New standalone physical evidence [Actions run 39692576705](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39692576705) and archived 4×raw Pa + 3×WAV. Full exact source SHA, frozen numerical comparison and unresolved independence in [EXPERIMENT.md](EXPERIMENT.md#2026-10-22--actual-new-physical-site08-result-first-exact-evidence-head). Objective machine pass, not scientific ratification or Studio delivery. B code subsequently hardened to pin oracle Git blob and frozen commit ancestry, requiring fresh final-HEAD CI.
