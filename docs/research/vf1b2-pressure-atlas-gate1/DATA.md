# VF-1B2 Pressure Atlas — Gate 1 DATA specification (proposed, experiment-local)

Date: 2026-10-27 | Status: DOCUMENTATION ONLY. Not a Core/Studio/OrganGraph production API.
These record shapes are intended as future **research file formats**, not adopted schema or an instruction to fill uncertain values by interpolation.

## Fixed research observation

primary_case_id: M5_UNIFORM_FIG2B_D002CM_DP10CMH2O
Source: Fulcher, Scherer, Powell, JASA (2011), DOI 10.1121/1.3514424, PMC3078031.
Figure 2B: measured pressure **drop** for a uniform M5 static larynx with minimal glottal diameter d=0.02 cm, transglottal drive 10 cmH2O.
Table I: volume flow Q=64.7 cm3/s, entrance loss coefficient 1.378 for the same d and pressure. These table quantities are contextual measurements/derived coefficients, not substitutes for plotted per-tap pressure values.

Life-size equivalents:
- d=0.0002 m.
- pressure difference nominal = 10 cmH2O; using standard 98.0665 Pa/(cmH2O) gives 980.665 Pa. Keep the original unit and conversion constant in provenance.
- Q=64.7 cm3/s = 6.47e-5 m3/s.
- z6 = 0.211 cm = 0.00211 m; z11 = 0.413 cm = 0.00413 m; z13 = 0.511 cm = 0.00511 m, **only these coordinates already verified from text**.
- model enlargement 7.5x. DO NOT combine rig scale and life-size pressure/flow axes; paper says rig pressure 1/7.5^2 and rig flow 7.5x life-size. Figure axis must be source-verified.
- D_i = p0 - p_i, where p0 is measured tracheal tap pressure. Store the plotted D first. Any reconstructed p_i=p0-D_i is a derived value requiring a separately known reference p0, NOT a measured absolute wall pressure. Likewise downstream p16 is a distinct measured pressure, not automatically atmospheric zero.

## Data-flow and ownership diagram

~~~mermaid
flowchart TB
  A["Published Figure/Table and text (read-only)"] --> B["SourceArtifact: DOI, fig id, source URLs, original bytes and digest"]
  B --> C["ConditionSnapshot: model/scale, pressure drive, diameter, flow, source convention"]
  B --> D["FigureCalibration: axis anchors, transforms, original image resolution"]
  D --> E["ReadSession A: observed plotted marker centroids + attribution"]
  D --> F["ReadSession B: independent centroids + attribution"]
  C --> G["TapIdentityMap: 0 reference; 6..13 target; FW/NFW separate"]
  E --> H["Raw observations with pixel/axis bounds"]
  F --> H
  G --> H
  H --> I["MeasuredPressureReference: physical positions, D Pa intervals, unresolved markers"]
  I --> J["SourceAuditReceipt: pass / partial / HOLD; input hashes + exact commit"]
  J -. "ONLY future, after geometry matching" .-> K["Rigid-flow candidate pressure model"]
~~~

## Proposed research records (NOT frozen runtime types)

1. SourceArtifact: paper DOI, bibliographic fields, PMCID, figure number/panel, acquisition URI/time, original file sha256 and license/access note, **source_kind = measured_marker | computed_curve | textual_number | table_value**. Computed curves cannot enter measured_marker arrays. Where original full figure cannot be lawfully retrieved/archived, record a stable original URI and acquire/verify later; no invented hash.
2. ConditionSnapshot: immutable case ID, apparatus=M5_uniform_rigid, d_life_m, dp_life_pa, q_life_m3_s, model_scale=7.5, original_pressure_unit, origin pressure tap=0, declared pressure_drop_positive=p0_minus_pi, sampling/steady conditions, pressure/flow input source locations and independent hash of text/table transcription.
3. FigureCalibration: original figure/panel hash, width_px, height_px, axis labels+units and explicit axis inversion, tick-anchor tuples (pixel, physical value) with >=2 verified nondegenerate anchors for BOTH axes, image crop transform, physical/life-size metadata, uncertainty estimates for pixel axis position/linewidth/marker width. Any nonlinear axis must be explicitly supported, otherwise HOLD. No hidden cropping or rotation.
4. TapIdentityMap: each actual named tap with (tap_id, physical z_m if documented, coordinate source, location uncertainty, wall label FW/NFW/UNRESOLVED, plotted symbol/legend). Text-verified z6/z11/z13 MUST NOT be used to generate fictional equal-spacing coordinates for the other taps; obtain Figure 1B or independent paper references.
5. DigitizationSession: analyst/process identifier, session version and no reuse of other analyst's output, selected measured-marker layer, original raw pixel centroids, marker-box bounds, ambiguous overlap evidence, axis calibration ID, the corresponding tap/side identification, notes and timestamps. Never replace source markers with Figure 4 predicted curves, drawn connecting lines or fitted Eq.4–6 values.
6. RawPressurePoint: (case_id, tap_id, wall_side, source_plot_marker_id, pixel_x/y, uncertainty_pixel_x/y, source figure id, measured/derived tag, read session id). Missing/occluded marks are MISSING or AMBIGUOUS with reason: NO numeric zero/NaN placeholder exported as valid measured data.
7. MeasuredPressureReference: per point, source-view z_m and interval, measured pressure DROP D_pa and interval derived from original axis, original plotted unit/value if recovered, independent read agreement or discrepancy, instrument uncertainty status/denominator from paper. Separate instrument, repeated-measure, digitization, coordinate-map, scale and model-form terms; preserve common-mode/correlated axis-calibration terms without assuming independence.
8. QualificationReceipt: input artifact digests, figure-id, case-id, source HEAD/test HEAD, accepted/rejected/ambiguous point counts, unresolved wall markers and tap coordinates, each subgate verdict, explanation, no-model-comparison G2 and no-audio G4. Receipt is immutable, never an editable Character property or Take.

## Observation identities and known traps
- Tap 0 is the tracheal pressure reference, not a generic plotted intraglottal sample. Tap 16 may act as a downstream pressure observation. Main analysis target is **actual Figure 2B measured markers at taps 6–13**, not arbitrary uniformly spaced samples along a fitted line.
- FW means jet-attached wall and NFW means jet-detached wall for the measured case; not a permanent left or right anatomical ID. At d=0.02 cm the paper notes that many NFW open triangles are hidden by FW filled circles. If two markers are indistinguishable, retain ONE resolved marker plus AMBIGUOUS status of the other; no unproven equality or arithmetic wall averaging.
- The experimental apparatus has rounded entrance/exit geometry. A uniform minimal aperture is NOT automatically a geometrically matched 1D linear-ramp Bernoulli toy (PR #216/#217). Geometry match is separately assessed for any future model and may be FAILED/UNKNOWN.
- The paper's less-than-1% uncertainty statement applies to specified **taps 6–14**, and is described as an upper limit. It is not stated as one standard deviation and its physical denominator/interpretation must be checked before converting to Pa. Likewise pixel digitization is an independent nonzero uncertainty, not covered by the paper's 1%.
- Q and entrance loss coefficient at the same operating point are an internal consistency check, not pressure-per-tap measurements and not an independent pressure-model validation set.

## Truth states
SOURCE_ONLY -> FIGURE_ACQUIRED -> CALIBRATED -> PARTIAL_DIGITIZATION -> DUAL_READ_RECONCILED -> SOURCE_QUALIFIED_FOR_COMPARISON (conditional, independently signed off).
Alternative states: AMBIGUOUS_MARKERS / INVALID_AXIS / MISSING_TAP_MAP / MISMATCHED_CASE / INSUFFICIENT_UNCERTAINTY / NO_INDEPENDENT_READ / HOLD.
No state is named PHYSICS_VALIDATED. Keeping the source honest is more important than forcing a complete data table.
