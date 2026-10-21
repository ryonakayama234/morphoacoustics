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

## 2026-10-21 experimental implementation branch (separate, not adopted)
- [Exploratory executable pilot](../../../experiments/cc_b1_rest_area_pilot/README.md): exact 16×10mm reference, section-0 rest area ×0.90/1.00/1.10, same audited task/source; 3 new raw pressure traces on execution. Standalone branch, no public API/Studio changes.
- [Independent 16-tube Wolfram code](../../../experiments/cc_b1_rest_area_pilot/wolfram/cc_b1_exploratory_16section.wl), [precomputed exploratory peaks](../../../experiments/cc_b1_rest_area_pilot/wolfram/cc_b1_exploratory_16section.json). Gate A independent signoff and prospective Gate B still pending.

## First actual machine evidence
[Successful exploratory physical CI at exact code/document HEAD c8a42720f54c9a20f2ce1fb8bed08c6185c06853](https://github.com/ryonakayama234/morphoacoustics/actions/runs/39580500879) executed 3 real 0.5s 48kHz pressure arrays, 3/3 CC-B1 tests and 7/7 CC-A2 regressions. New preview-WAV followup is **not included in that historical run** and requires a new exact-HEAD CI.
