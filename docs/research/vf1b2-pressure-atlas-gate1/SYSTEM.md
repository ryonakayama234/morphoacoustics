# VF-1B2 Pressure Atlas — Gate 1 SYSTEM (design-only preregistration)

Date: 2026-10-27 | Status: PROPOSED / NOT EXECUTED / NOT ADOPTED
Parent: Core Issue #215; preceding independent source-qualification Draft #218 (final reviewed head dd2a94598f1a048aabb547dca18367916990bb88).
Branch base: Core main e05e3274ad69bfb9202816049f6661a18ba39ec0, not stacked on unmerged #218/#217/#216/#214.
Purpose: transform ONE measured M5 static glottis figure condition into an auditable scientific reference for a LATER separate solver comparison, without letting the literature-sourced measurements become fitted model outputs.

## Primary target / original publication

Fulcher, Scherer and Powell (2011), JASA 129:1548–1553, DOI 10.1121/1.3514424, PMC3078031.
Figure 2B: M5 UNIFORM static glottis, d=0.02 cm (life-size equivalent), transglottal pressure 10 cm H2O (life-size equivalent). Figure 2B contains the relevant plotted pressure distribution; Table I gives the same operating-point volume flow Q=64.7 cm^3/s and reported entrance loss coefficient 1.447. Those published table values are same-study crosschecks, NOT independent measurements of the shape of Figure 2B and NOT a model-validation holdout.
- Taps 6 and 13 are the glottal entrance and exit at axial life-size positions z=0.211 and 0.511 cm; the paper also reports tap 11 at 0.413 cm. Further tap coordinates require verified Figure 1B geometry. No synthetic uniformly spaced tap map.
- Paper reports a 7.5x model enlargement. Physical-rig pressure scales as (1/7.5)^2 of life-size, and model flows as 7.5 times life-size; record the actual units/scale of each source axis before conversion.
- The figure presents pressure DROP relative to tracheal tap 0, not an absolute pressure or the sign of tissue force. Define D_i=p_0-p_i; a positive D means local wall pressure below the tracheal reference. Preserve source conventions and the distinct flow-wall (FW) and nonflow-wall (NFW) experimental marks. A partially or fully overlapped NFW point is MISSING/AMBIGUOUS, not FW, a copy or a zero.
- Static wall means no wall displacement or tissue power measurement. Flow regime, adhesion and recovery are attributes of this measurement apparatus, not assertions of universal in-vivo behavior.

## Three separated system paths

~~~mermaid
flowchart TD
  S["Original measured Figure 2B and published instrument method"] --> O["Source archive: immutable source identity, DOI, figure, acquisition/hash"]
  O --> F["Frozen case M5: d=0.02cm, pressure=10cmH2O, tap 0 reference, tap 6-13"]
  F --> L["Figure calibration: axis, scale, sign, mark shape, wall label"]
  L --> R["Two independently read measurement-point sets"]
  R --> U["Uncertainty: instrument vs pixel/axis/tap registration; no forced Gaussian"]
  U --> Q{"Gate 1 scientific source qualification"}
  Q -- "insufficient/ambiguous" --> H["HOLD: preserve raw readings and reasons"]
  Q -- "independently reconciled" --> T["Immutable measured p(tap) reference + source-audit receipt"]
  T -. "only after NEW approval and matching geometry" .-> V["Future independent rigid-flow model test, G2"]
  V -. "not implied" .-> E["Future moving-wall energy-conjugate FSI, G3"]
~~~

### Crucial non-circularity
Independent measured marker extraction is an observation. Fulcher et al. Eqs. 4–6 and Figure 4 are fitted/explanatory reconstructions using measured Q, entrance/exit coefficients and interpolation; they may be analyzed as historical comparators but must NEVER be relabeled as Figure 2B measured points. A candidate model must freeze its equations, geometry, inlet/outlet boundary and coefficients before comparing its predicted p(tap) to this reference. No parameter adjustment against the selected curve may then count as independent G2 validation.

## Dependency and data ownership

~~~mermaid
flowchart LR
  A["Study archive / scientific source"] --> B["Experiment 048 Gate0 inventory (Draft #218)"]
  B -. "conditional provenance dependency; no imports while Draft" .-> C["Gate1 figure-metrology data (this design)"]
  C -. "future eligible source" .-> D["Separately preregistered matched fluid comparison"]
  D -. "must pass physics and energy audits" .-> E["Core candidate phonator"]
  E -. "only when validated" .-> F["Studio Performance -> immutable Take"]
~~~

- Gate 1 is an experiment-local reference **producer**, NOT a pressure solver, joint organ model, or component of a self-oscillator. Code will be placed under a separately reviewed experiment directory ONLY after this design decision.
- Core src/morphoacoustics and src/morphoacoustics_graph retain sole authority over actual domain semantics, physical ports and supported solver capability; neither is changed here. The current graph candidate does not imply validated 3D laryngeal execution.
- Studio product contract: approved V2 ADR at morphoacoustics-studio/docs/product/STUDIO_WORKSPACE_V2_DECISION.md. character.canvas owns the Character/organ graph, motion.canvas the Script/Direction/MotionScore, scene.canvas Speaker/Listener, take.transport immutable audible Takes; research.drawer is the only future display of this source-qualification receipt. No Studio edit, extra panel, new UI slot, Performance Contract, Take or source effect.
- SMC and ASMR are optional independent tracks; there is no direct import or integration in Gate1. Neural models do not touch measured source data and cannot reconcile disagreements by altering p(tap).

## Scientific boundary and STOP
Source reference eligibility is not G2 aerodynamic model validation. G2 pressure model, G3 moving-wall pressure work and G4 creator-voice quality remain INDETERMINATE/NOT_APPLICABLE/NO_GO. Even a beautiful digitized pressure profile cannot by itself produce physically justified vocal-fold forces, tissue power, self-sustaining oscillation, a voiced WAV or a Studio audition.
