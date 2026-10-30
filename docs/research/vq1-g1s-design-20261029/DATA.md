# VQ-1 / G1-S — Measurement contract FINAL DECISION (DATA)

**Version:** 2026-10-29 v1.0, **design-only research-local schema**. No public Core API, canonical Character data, Studio schema or stored Take changes. All numerical physiological fields begin **absent**, never with placeholder measurements.

## A. Observation versus inference

| Entity (owner) | Required fields and dimension | Meaning / invariant |
| --- | --- | --- |
| `CaseKey` (source) | publication DOI/figure/panel; model=M5 rigid uniform; physical gap [m]; drive value + **exact pressure endpoints** [Pa]; source scaling; flow state; session ID | All points in a profile come from the **same** condition; Figure 2B anchor is d=0.02 cm, reported transglottal 10 cmH2O; physical tap positions must be verified at original model scale |
| `SourceAsset` (source) | immutable original-figure locator, page, canonical content SHA256, rights/availability, retrieval date, original figure resolution | No SHA is invented when the figure bytes have not been acquired |
| `AxisCalibration` (metrology) | read ID, horizontal/vertical pixel anchors and printed source tick values/units, coordinate direction, source scale, transformation + resolution bounds | Dimensional and sign verification; pressure drop `D=p0-p_i` not `p_i` |
| `PressureMarker` (metrology) | tap ID and audited axial coordinate, published FW/NFW/ambiguous class, image location or explicit occlusion, two **independent** digitizer reads, digitization bounds, published error description | A marker is not a continuous pressure field. Do not infer hidden NFW from visible FW or equate FW/NFW with fixed left/right physical walls |
| `PressureObservation` (atlas) | `CaseKey`; tap/side; `D_pa` interval; `z_m` interval; linked reads; source-qualification status | Can be SOURCE_QUALIFIED independently of every force computation |
| `ReferenceEvidence` (boundary) | tap0 and tissue-backside pressure reference and reported endpoints/units; linked calibrations and shared measurement/derivation IDs; bounded or joint error model | Need `DeltaP_0,back=p0-p_back`; measured transglottal `DeltaP` does not alone prove this reference |
| `GeometryEvidence` (independent model) | versioned rigid wetted surface, actual left/right physical wall IDs, region/normal/area [m²], tap support footprints, source and scale, 2D/3D assumption and uncertainty | Must be supported **independently** of pressure values; a tap is not an area element |
| `CoordinateDefinition` (mechanics) | `q_id`, q unit **m**, axis, physical wall mapping, virtual displacement `phi_q(x)`, normalization and support | `q_gap` and `q_center` are distinct; published FW/NFW alone do not supply physical wall identity |
| `PressureToSurfaceMap` (inference) | rule/version, per-patch supporting observed tap IDs, interpolation/extrapolation flags, validation bounds, covered/unsupported surface and area fraction | An assignment of one measured point to a broad area is a **model assumption**, not observed data |
| `ForceEstimate` (conditional inference) | `Q_q` [N], interval, pressure-error decomposition, geometry/mapping sensitivity, source/coverage state, exact source/algorithm SHA | Can say CONDITIONAL_ON_*; cannot claim verified vocal-fold force without evidence |
| `ScienceReceipt` (research) | immutable IDs/hashes, exact commit SHA, prereg version, observed-vs-synthetic field flag, gating status by level, missingness reasons, raw failure, no-audio assertion | Append-only, machine-readable even on test failure |

## B. Source-specific namespace

- `tap_id` is a physical location, including source tap0 (tracheal reference), 6 (glottal entrance), 11 (end of straight region), 13 (glottal exit); source Fig2 and exact coordinates must be audited, not linearly filled.
- `source_attachment_class` enum: `FW` (jet-adhered flow wall), `NFW` (jet-separated nonflow wall), `AMBIGUOUS` (overlap/not independently resolved), `UNCLASSIFIED`. This is **not** physical wall `left/right`. A separate `physical_wall_id` is unavailable unless a traceable geometry/flow-case map exists.
- `marker_observation_state`: `VISIBLE`, `OCCLUDED`, `AMBIGUOUS`, `ABSENT_BY_SOURCE`. Only VISIBLE independently calibrated markers become point values. Do not average FW/NFW before retaining originals; the paper averaged sides for certain coefficients, which does not retroactively reconstruct either pressure point.
- Original source Figure 2B for 0.02 cm has largely overlapping FW/NFW marks. Its high side-resolution may be unidentifiable. Different d cases (e.g. 0.16 cm Figure 2C) are a separate **challenge case**, never mixed with the 0.02 cm anchor.

## C. Unit and semantics audit

Use SI in computed fields: cm -> 0.01 m; cm² -> 1e-4 m²; cm³/s -> 1e-6 m³/s; Pa as pressure; pressure ordinate in cmH2O must preserve the publication's adopted conversion (and uncertainty). Distinguish physical life-size from apparatus scale; for equal similarity scaling by factor `s`, surface scales `s²`, force scales `s²` **only at identical pressure field**; no scale transfer without the model similarity assumptions.

Raw observable:
`D_i = p0-p_i`, `D_i-D_k = p_k-p_i`, valid without backside pressure if both are on same common datum.

Conditional pressure contrast:
`P_i = (p0-p_back)-D_i`. If `p_back` absent, **do not** set it to atmosphere or to exit-tap pressure by convenience.

Conditional generalized load for q in metres:
`Q_q = sum_j P_j w_j`, `w_j = A_j(n_f,j dot phi_q,j)` [m²], so `Q_q` has unit N.

Uncertainty of `Q_q` must account for correlated `DeltaP_0,back` and D errors (the same sensor/reference can enter both). A conservative distribution-free pressure-only bound using separately valid absolute component bounds:
For **independently justified uniform shared** `R=p0-p_back` across all patches, `u_Q,p <= abs(sum_j w_j)*u_Rshared + sum_j abs(w_j)*u_Dj`.
For a **patch-varying** `R_j` with separately valid absolute bounds, use the safe fallback `u_Q,p <= sum_j abs(w_j)*(u_Rj + u_Dj)`; this bound does NOT permit cancellation of unknown backside fluctuations between opposite walls. An explicitly sourced decomposition `R_j=R_common+delta_j` permits `abs(sum_j w_j)*u_Rcommon + sum_j abs(w_j)*(u_delta_j+u_Dj)`. Where primitive calibration errors are shared between R and D, interval/covariance propagation over the actual primitive sensors is preferred; absent that, the component-wise bound is conservative, possibly loose.
For example with translation weights `w_left=-0.01 m²`, `w_right=+0.01 m²`, independent backside uncertainty `u_Rleft=u_Rright=5 Pa`, and exact D, the uncertainty bound is `0.1 N`, **not zero**, despite `sum(w)=0`. The original formula applies ONLY to a qualified common reference.
This is a **worst-case component bound**, not a 95% confidence interval; it may be loose if primitive sensor errors cancel. Where primitive calibration/observations permit, propagate their shared covariance or shared interval variables exactly; never assume independent tap errors. Geometry/map/coordinate errors must be reported **separately** or included through defensible interval/sensitivity analysis. Total uncertainty must NOT be represented by `u_Q,p` alone.

For missing spatial surface regions: report `Q_q,observed-supported` only for proven supported subset; never call it whole-fold `Q_q`. If the unmeasured region has no justified pressure interval, the **whole-surface force is NOT IDENTIFIABLE**. An arbitrary interpolation with 0 reported error is disallowed.

## D. Status lattice (no silent promotion)

1. `S0_SOURCE_UNQUALIFIED`: original figure/point provenance or units not independently audited.
2. `S1_PRESSURE_ATLAS_QUALIFIED` (or `S1_PARTIAL`): source case, tap, side class, calibration and finite observed intervals audited. **No force implied.**
3. `S2_CONTRAST_IDENTIFIABLE` (or `S2_HOLD_REFERENCE`): source-qualified D plus independently established backside pressure/reference and its correlations.
4. `S3_FORCE_CONDITIONAL` (or `S3_HOLD_GEOMETRY`, `S3_HOLD_COVERAGE`, `S3_HOLD_COORDINATE`): defined q, known surface support and uncertainty-labeled mapping.
5. `S4_STATIC_FORCE_VALIDATED`: reserved for genuinely independent force or physically equivalent validation with matching geometry/BC. **Not attainable from algebra or the present source material alone.**
6. `G1_D_HOLD`; `VOICE_NO_GO`: invariant for this design work and the current static rigid M5 source.

Each status carries `evidence_refs`, `unmet_requirements`, `observed_fraction`, `hypotheses_checked`, `sha` and `is_synthetic`. No `GO` fields on synthetic fixtures.

## E. Relationship to existing code, no retroactive reinterpretation

Draft [#239](https://github.com/ryonakayama234/morphoacoustics/pull/239) `PressureDrop(tap_id,wall,D,u,source_kind)`, `SurfacePatch(area,projection)`, `PressureReference(p0,pext)` remain **experiment-local synthetic algebra**. The `wall=FW/NFW` field does not provide anatomical left/right identity. The `projection` field does not carry a unit-specific physical coordinate. Therefore its tests can verify algebra, sign manipulations, gauge shifts and failure receipts, but not `q_gap` physiology or a measured M5 force. Do not silently upgrade its `observed_marker` string to an evidence qualification token. The future executable work package must design a separately versioned input with enforceable provenance rather than mutating that Draft into production.

References: [M5 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC3078031/); [Core source protocol #220](https://github.com/ryonakayama234/morphoacoustics/pull/220); [Core data scalar #222](https://github.com/ryonakayama234/morphoacoustics/pull/222); [Studio V2 ADR](https://github.com/ryonakayama234/morphoacoustics-studio/blob/main/docs/product/STUDIO_WORKSPACE_V2_DECISION.md).