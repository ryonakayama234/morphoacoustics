# VQ-1 / M5 Gate1 — EXPERIMENT preregistration

**2026-10-30 BEFORE numeric/source code.** This work operationalizes the frozen design [#241](https://github.com/ryonakayama234/morphoacoustics/pull/241) and Figure2B protocol [#220](https://github.com/ryonakayama234/morphoacoustics/pull/220).

## Questions and falsifiable hypotheses
- H-IMAGE: an original figure image traceably identified as Fulcher/Scherer/Powell 2011 Fig2B can be obtained; *absent bytes -> HOLD and no pixel measurements*.
- H-CASE: source case is d=0.02cm and 10cmH2O; wrong panel, model scale, conversion or tap0 sign -> REFUSE.
- H-CAL: ≥2 distinct independently annotated x/y ticks define calibrated intervals with nonzero uncertainty, correct axis direction/unit and no invented affine x/tap spacing. Degenerate ticks -> REFUSE.
- H-DUAL: two independent reads of a **visible** point agree by bounded interval overlap. Copying one reader into a second ID, incompatible/occluded/ambiguous marker -> PARTIAL/HOLD, not numeric pass.
- H-AXIAL: if qualified tap 6 & 11 data on one same flow category exist, test `D11>D6` by nonoverlapping conservative intervals; otherwise INDETERMINATE. For tap11 vs13, if available test `D13<D11`; do not infer values from prose.
- H-SIDE: FW/NFW are attachment categories, not anatomical sides; overlapping NFW cannot be copied from FW. Such missing side does not affect an FW-only partial if clearly reported.
- H-LIMIT: success in pixel calibration is not observed wall force; S2 S3 G1-D voice must always be HOLD/NO_GO. No model-generated Figure4 fit is allowed as observed Figure2B marker.

## Tests before any empirical claim
1. Explicit normal no-image input generates machine JSON `SOURCE_IMAGE_NOT_ACQUIRED`, observed count 0, status HOLD and exit success for **honest HOLD** (the pipeline executed).
2. Analytic synthetic figure pixel controls test axis conversion, pixel centroid uncertainty and independent-reader intersection. These synthetic trials have `synthetic_control` source kind and cannot generate science GO.
3. Negative controls: missing/changed original SHA, wrong case/DOI/panel, invalid unit, zero-width axis, y-axis inversion misdeclaration, anonymous/copied analyst IDs, non-finite/boolean pixels, impossible tap, nonvisible marker with numeric location, mismatched wall class, inconsistent reads, missing coordinate map, Figure4 curve labels and no pressure unit.
4. Shared calibration error must not be double-counted as independent tap noise; do not claim Gaussian 95% or predetermined percentage PASS.
5. CI must archive JSON even on RED tests or exceptions; include exact code SHA; archive step is `always()`, with explicit absent-source provenance and STOP.
6. No production Core, no UI/SMC/ASMR, no acoustic waveform, no G1-D promotion.

## Acceptance
PASS for **software logic** is not physical source acquisition. A scientific `S1_SOURCE_QUALIFIED` status is **not emitted by program**: it requires independent original-source and read audit plus external acceptance. The legitimate expected outcome without original figure bytes is 0 source-qualified measurements and `SOURCE_IMAGE_NOT_ACQUIRED`. Full 8-tap FW candidate requires all original taps6..13, source coordinates, independent digitizers and traceable manuscript figure with material uncertainty, followed by independent manual scientific review. Missing points yield PARTIAL/HOLD; never interpolation. If H-IMAGE cannot be satisfied, record an explicit external-source acquisition dependency rather than inventing data.

Initial source publication [PMC3078031](https://pmc.ncbi.nlm.nih.gov/articles/PMC3078031/). Published case details in #220, prior empty experimental inventory #218. Studio Workspace V2 remains frozen.