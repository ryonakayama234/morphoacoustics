# VF-1B2 Pressure Atlas — Gate 1 EXPERIMENT preregistration

Status: DESIGN ONLY, frozen before numeric figure extraction. Date: 2026-10-27.
No implementation, measured-point CSV, figure-digitization script, model fitting, wave synthesis, moving-wall FSI or Studio changes in this proposal.

## The exact question
Can a source-identifiable, uncertainty-qualified and *independently readable* experimental pressure-drop profile D_i=p0-p_i at M5 taps 6..13 be reconstructed for **one preselected** rigid uniform case (Fulcher/Scherer/Powell 2011, Figure 2B, d=0.02cm life-size, transglottal pressure 10cmH2O)? If yes, what observed axial pressure-loss/recovery features does it resolve, WITHOUT treating either the paper's own fitted reconstruction or a toy model as independent measured data?

## Predeclared scientific hypotheses (falsifiable and distinct)

H-REF (source measurability): Actual Figure 2B *measurement markers*, their tap attribution/side, axis values and source-provided geometry can be traced back to the original publication and independently digitized. Reject qualification if points are missing/occluded, if there is no valid axis calibration, or if independent reads cannot reconcile within recorded uncertainty intervals. A useful partial dataset is a documented PARTIAL result; do not invent the rest.

H-AXIAL (descriptive, not a solver GO): For this narrow uniform-glottis condition the paper describes a near-uniform pressure decrease within its straight section (taps 6–11); in the recorded drop convention D_i=p0-p_i, the tentative directional prediction is D_11 > D_6. Test with conservative read/measurement intervals: supports when lower(D11)>upper(D6); contradicts when upper(D11)<lower(D6); otherwise unresolved. **Near-linearity** is summarized by tapwise slope and residuals against a descriptive line, not certified against post-hoc chosen threshold.

H-RECOVERY (descriptive): The article reports pressure recovery approaching the rounded exit in d=0.02cm. In drop convention the proposed directional comparison is D_13 < D_11, evaluated with the same interval separation logic. Absence of resolvable recovery means NO_SUPPORT or INDETERMINATE, not an excuse to change tap labels or smooth the curve.

H-SIDE (measurement distinction): At d=0.02cm FW and NFW values may be very close and graphically overlap, as the article expressly notes. Predict **possible side-identity non-identifiability in Figure 2B**, not proven equality. Do not combine walls unless both are independently identifiable and a later separately declared averaging purpose justifies it. A distinct, resolvable NFW profile would falsify the overlap assumption, which is acceptable.

H-CAUSAL-LIMIT (negative control): Even if the four source hypotheses are supported, measured STATIC wall pressure does not establish moving-wall tissue work or self-excited voice. An algorithm that upgrades Gate1 source success to G2/G3/G4 must FAIL independent review.

## Case selection and exclusion frozen NOW
- Primary: M5 uniform **Fig 2B**, d=0.02cm, 10cmH2O; pressure-drop samples attributed to taps 6–13 on the FW side. NFW side independently recorded only where the symbol is actually distinguishable, otherwise ambiguous. Tap0 is the pressure reference. Bring tap16 only as a contextual downstream boundary if its original marker is verifiable.
- Table I same-case checks: Q=64.7cm3/s and k_ent=1.378. Do not interpolate Q from another condition or repurpose k_ent as a fit parameter.
- Secondary NON-EXTRACTION sanity checks: Figure2A narrow d=0.005cm and Figure2C d=0.16cm are different phenomena; M6 3D pressure/flow is a separate reference. No claim of multi-diameter validation from one-case Gate1.
- Exclude all Figure4 computed model curves, Eq4–6 interpolated points, and samples from other P/d panels as measured primary observations. Refuse case substitution unless a new documented preregistration is explicitly approved BEFORE looking at candidate outputs.

## Workflow in scientific order (future action, not yet performed)
1. **Original-source audit:** inspect the publication's original Figure 1B and 2B, determine actual plotted pressure reference, axis limits/units and visible FW/NFW symbols. Archive legally permissible original bytes with hash, figure provenance, access and version. Confirm P=10cmH2O curve exists and is measurable. If no adequate image, stop: SOURCE_ONLY.
2. **Tap and wall metrology:** map exact original tap numbers, source-referenced axial positions with units and coordinate uncertainties. Existing text anchors: z6=0.211cm, z11=0.413cm, z13=0.511cm. Do NOT fill unreported coordinates by equal spacing or give the fixed FW label anatomical laterality.
3. **Axis calibration before points:** independently register >=2 legible nondegenerate tick anchors per x/y axis, source resolution, plot transform/scale and marker width; validate sign and life-size conversion. Calibrate without seeing the model prediction or imposing an assumed linear p(z).
4. **Two independent reads:** first and second passes must have independent marker selections and frozen raw pixel coordinates, distinct methods or analysts, recorded legends, ambiguity and plot calibration. Second pass never copies first pass points. Missing/overlap produces explicit AMBIGUOUS; no value-synthesis from connecting lines.
5. **Uncertainty ledger before comparison:** paper measurement upper limit for taps 6–14, axis-tick/line/marker/pixel resolution, tap registration and rig-to-life scaling remain separate; instrument bound is not one sigma. Interval arithmetic must preserve shared axis calibration rather than claiming independent point errors. Quantitative disagreement between two reads exceeding their precomputed conservative bounds => HOLD with raw alternatives retained, no retrospective loosening.
6. **Reference export and source review:** export all attributable taps 6–13 for the selected primary FW profile, with measured drop D, source coordinate and uncertainty. A profile is SOURCE_QUALIFIED_FOR_COMPARISON only if all eight required taps are valid/reconciled, axial mapping and units are verifiable, and an independent source/figure audit agrees. If some overlap is unresolved report PARTIAL/INDETERMINATE, never force full pass.
7. **Feature analysis only:** compute interval-based direction of D11-D6 and D13-D11, plus descriptive deviations from an affine straight-section trend and side-label identifiability. Mark this as descriptive observation, not an airflow closure experiment. Preserve negative cases and exact input hashes.

## Predeclared admissibility gates
- G1-SRC: DOI, figure/panel, original marker layer, condition (d,P) and acquisition hash/source metadata validated.
- G1-CAL: original plotted coordinates, valid axes, pressure-drop sign and life-size-vs-rig conversion recorded.
- G1-TAP: actual tap6..13 source geometry and side identity; no interpolated anatomical tap coordinates or imposed symmetry. Full 8-point FW coverage required for complete-profile claim.
- G1-UNC: instrumental/digitization/axis/tap uncertainty **separately** specified; two independent reads and explicit reconciliation criterion (interval overlap) before feature results.
- G1-AUD: fresh independent source-evidence review, scientific provenance and exact tested commit; only then SOURCE_QUALIFIED_FOR_COMPARISON. In all other circumstances HOLD/PARTIAL, with exact reasons.
- G2 remains INDETERMINATE: there is **no** independently registered *matched* aerodynamic model or pressure prediction in this study.
- G3 = NOT_APPLICABLE_NO_MOVING_WALL. G4 = VOICE_NO_GO. No audio listening is meaningful in this research gate.

The numeric uncertainty magnitudes CANNOT truthfully be fixed from prose alone: image resolution, calibration ticks and marker widths have not been read yet. Freeze the **formula and method now**; instantiate documented numerical bounds from source pixel metrology BEFORE any model output, never from the success of a desired physical claim. If source quality is too poor to derive those bounds, label G1-UNC insufficient. No fabricated 1% standard deviation or arbitrary 2% 'pass' rule.

## Adversarial test plan
- An Eq4–6 calculated curve substituted for filled measurement circles MUST fail G1-SRC.
- P=15 or d=0.16 data relabeled P=10/d=0.02 MUST fail condition binding.
- p_i-p0 sign instead of D_i=p0-p_i MUST fail convention and reversal-feature test.
- Treating model-scale rig pressure as life-size P without 7.5^2 conversion MUST fail G1-CAL.
- M6 transverse taps relabeled as M5 axial taps MUST fail geometric identity.
- Assigning identical FW/NFW when one is occluded MUST fail G1-TAP.
- Invented regular tap spacing or missing physical location uncertainty MUST fail G1-TAP.
- Missing/changed source bytes, forged figure hash or unacknowledged recrop MUST fail G1-SRC.
- Two incompatible digitization reads MUST fail G1-UNC rather than selecting a favorable analyst.
- A fitted model exactly matching the reconstructed p(z) MUST still leave G2 INDETERMINATE absent frozen independent geometry/model tests.
- An upgrade to acoustic / wall-force / self-oscillation / Studio claims MUST fail H-CAUSAL-LIMIT.

## Post-Gate1 next proposal (separately approved)
Geometry-matched rigid-flow model experiment: freeze anatomical wall shape/rounded edges, pressure/flow boundary, viscous/separation hypotheses, numerical discretization and coefficients BEFORE comparing predictions against held-out measured pressure. Account for side-specific FW/NFW and NFW ambiguity rather than averaging away 3D effects. Only after a valid G2 profile benchmark consider non-double-counted 1D moving-wall continuity/momentum and energy-conjugate ports as an entirely different G3 study. Physically justified **voice quality** then needs an actual radiation/receiver measurement and creator audition, not a pressure-plot success.
