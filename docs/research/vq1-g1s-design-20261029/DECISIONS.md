# VQ-1 / G1-S — Final decisions, trade-offs and evidence ledger (DECISIONS)

**Final architecture decision (2026-10-29, v1.0; design-only):** execute **measured static wall-pressure atlas qualification first**, then an independently gated geometry/reference/kinematic identifiability audit. Mathematical synthetic verification was useful but is NOT sufficient for measured force or dynamic phonation. This document freezes decisions for the next research task, not Studio UI changes or a production merge.

## The decisive correction to the older draft

Core Draft [#239](https://github.com/ryonakayama234/morphoacoustics/pull/239) uses `sum_j (p0-D_j-pext)A_j projection_j`; its synthetic controls are valid conditional algebra. **What it does not identify:** the virtual motion coordinate associated with `projection`, permanent physical wall identity behind the FW/NFW flow categories, actual surface coverage, tissue backside pressure, uncertainty from wet geometry or dynamic work. Consequently:
- `q_gap` opening: symmetric pressure loads **add**.
- `q_center` translation: symmetric pressure loads **cancel**.
- An algebra test of cancellation is not a measured opening-force test.
- The paper's Figure 2B pressure symbols do not determine a full continuous wetted-surface load.
- The study is rigid/static; it has no self-excitation, time-dependent tissue mechanics or valid F0 result.

Retain #239 as a Draft, verified limited synthetic baseline, and **do not silently rewrite its science or promote it by rewording results**.

## Why this sequence, rather than alternate approaches?

| Candidate | Strength | Why not first |
| --- | --- | --- |
| **A. Direct M5 Figure 2B source atlas and pressure identifiability** — SELECTED | Closest independently published physical observable; maximal discrimination between observed D, missing side, and inferred P | Requires painstaking metrology and may truthfully end PARTIAL |
| B. Extend #239 synthetic quadrature into a force engine | Quick CI and software demonstrations | Physically underidentified: lacks coordinates, actual area, true physical-wall identity, back pressure; green arithmetic could mask scientific ambiguity |
| C. Connect G0-P p/U directly to tissue force | Reuses validated acoustic port | G0 pressure is supraglottal acoustic inlet, not intraglottal spatial wall field; confuses domains and creates false causal force |
| D. Build a dynamic oscillator / FSI immediately | Shortest nominal route to an audible note | No calibrated pressure model, validated moving-wall energy, independent tissue model or naturalness; arbitrary instability cannot be labelled voice |
| E. Improve Studio UI or postprocess generated audio | Immediate creator-facing visibility | Visual layout is expressly frozen; audio beautifier masks physically impossible articulation and cannot certify morphology-conditioned voice |

The next deliverable must **produce evidence** rather than just infrastructure: a source-qualified, uncertainty-bearing set of M5 axial pressure-drop samples **or** a precise report that symbols/reference/geometry cannot resolve the target, with all missing evidence enumerated.

## Exact module ownership and change boundaries

- Core measurement work: new **design-approved, separate experiment-only** source-atlas provenance pipeline, with source-figure audit and independent reads; preserve source docs [#218](https://github.com/ryonakayama234/morphoacoustics/pull/218) and [#220](https://github.com/ryonakayama234/morphoacoustics/pull/220); do not import unmerged branch experiments blindly.
- Core acoustic G0-P [#238](https://github.com/ryonakayama234/morphoacoustics/pull/238): stays research-only p/U, no artificial conversion into p_wall.
- Core SFI/VF and future moving wall: separate G1-D validation and explicitly held until proper measured dynamic inputs and energy testing.
- Studio: [accepted frozen V2](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md); no UI edits or added panels. Future Character organ material, Motion gestures, Scene propagation and immutable Take only through later approved domain contracts.
- Neural: permissible future motor/inverse/physically constrained closure/evaluation, not replacing a missing pressure field with plausible speech or audio repair.

## Proof obligations before declaring results

```text
CASE and SOURCE FILE fully identified?
   no -> S0 HOLD
   yes
       |
Two independent reads; calibrated pressure D and correct tap/side?
   no -> S1 PARTIAL/HOLD, no guessed curve
   yes -> S1 SOURCE-QUALIFIED ATLAS (this alone is useful)
       |
True backside/common gauge relation independently measured?
   no -> S2 HOLD, pressure contrast not absolute
   yes
       |
Physical wall, wetted area, normal, q, mapping and unknown-area bounds?
   no -> S3 HOLD, full-surface force not identifiable
   yes -> S3 CONDITIONAL generalized pressure load + uncertainty
       |
Independent matched-geometry force validation?
   no -> S4 HOLD (no measured force certification)
   yes -> S4 STATIC ONLY
       |
Moving walls, synchronized pressure/velocity and cycle work validation?
   no -> G1-D HOLD, voice NO-GO
```

## Reproducibility and numerical policy

Keep original raw points, status and figure provenance separate from derived observations. Preserve source-supplied error rather than invent a narrow confidence band. Two digitizer reads do not eliminate systematic printed-figure errors. Use unit checks and controlled gauge transforms. No preference for curves that resemble a desired timbre. Do not equate physical validity, audible quality, or UI readiness.

## Current verified facts (2026-10-29)

- GitHub Core `main`: `727b11ecf103f5c087cfcb820bdec11f883e7c03`.
- Existing G1-S synthetic Draft [#239](https://github.com/ryonakayama234/morphoacoustics/pull/239) HEAD `11dd289ef72e1c1b65de5bac95391239e8b6e2fe`: exact-head [dedicated CI success](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40710433629), [main tests success](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40710433768), final Codex review reported **no major issues**. Earlier P2 fail-to-archive receipt was repaired, with test regression. PASS means only the experiment's synthetic algebra/receipt scope.
- M5 primary [Fulcher et al. JASA 2011, DOI 10.1121/1.3514424](https://pmc.ncbi.nlm.nih.gov/articles/PMC3078031/) explicitly documents static rigid M5 pressure distribution, flow-wall vs nonflow-wall and overlapping markers at 0.02 cm; this is not a direct validated surface integral.
- Contemporary background: [2024 overview](https://pmc.ncbi.nlm.nih.gov/articles/PMC11348498/) on self-oscillating synthetic vocal fold models; [2025 meeting abstract](https://doi.org/10.1121/10.0041540) and [2026 Japanese meeting record](https://jglobal.jst.go.jp/en/detail?JGLOBAL_ID=202602236415458121) on dynamic M5-like pressure. These are pointers for a **separate** dynamic research design, not a grant to use numerical values unseen here.

## Explicit decision limits

This v1 is a **completed, reviewable design decision**: exact target, independent measurable outcomes, coordinate physics, data ownership, numerical oracle, refusal gates, creator-interface boundary and preferred next task are all frozen in SYSTEM/DATA/EXPERIMENT/DECISIONS. Yet it cannot honestly make the original M5's unknown backside, detailed wetted geometry or hidden FW/NFW symbols appear. If those are not recoverable, the right outcome is pressure-only S1/PARTIAL and a separate targeted measurement source—not speculative extrapolation.

**GitHub action taken by this branch:** only new Markdown design documents; no experimental execution, no code, no Studio, no merge.