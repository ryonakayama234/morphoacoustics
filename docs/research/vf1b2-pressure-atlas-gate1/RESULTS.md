# VF-1B2 Pressure Atlas — Gate 1 RESULTS and non-result ledger

Date: 2026-10-27. Status: DESIGN PREPARED, experiment **NOT STARTED**.
This ledger is intentionally NOT a CSV of pressure measurements and NOT an experimental numeric success.

## Verified input facts (source reading, not our experiment)
- Fulcher, Scherer & Powell (2011), DOI 10.1121/1.3514424, PMC3078031 describes Figure 2B uniform M5 measured static pressure profiles for d=0.02 cm, with multiple transglottal pressures.
- We preselect the published **10 cmH2O life-size equivalent** condition for future source digitization. Paper Table I at d=0.02 cm/10 cmH2O reports Q=64.7 cm3/s, entrance loss k_ent=1.447. At 15 cmH2O the table instead lists k_ent=1.378. Correct column association was audited against the displayed original Table I during this design, and prior initial erroneous 1.378 draft texts were corrected before this PR.
- Paper tap 6 z=0.211 cm; tap 11 z=0.413 cm; tap 13 z=0.511 cm (life-size). Figures contain measured point symbols; the Figure 4 calculated pressure reconstruction must not be imported as measured observations.
- For specified taps 6–14 the authors describe pressure-measurement uncertainty less than 1% as an **upper bound**, not one sigma; future digitization uncertainty remains unknown and not yet quantified.
- The paper describes partly overlapping FW/NFW markers for d=0.02 cm; figure-specific source verification must decide which can be independently read.

## Executed tasks in THIS PR
- Read scientific references and previous Core/Studio Gate0 product boundaries.
- Chose one falsifiable operating point and separated the targets D11>D6 / D13<D11, axis/uncertainty audit, and SIDE ambiguity.
- Preregistered SYSTEM / DATA / EXPERIMENT and DECISIONS without introducing algorithms or measured-point samples.
- Preserved Core main and frozen Studio V2 without UI/API edits.

## Absolutely not accomplished
- Original figure full-resolution acquisition/archival SHA256: NOT RUN.
- Pixel axis calibration / marker digitization: NOT RUN.
- Measured tapwise pressure numbers (p0-p_i): **0 recovered by this PR**.
- Independent second figure-reading, quantitative uncertainties, or full tap 6..13 coordinate map: NOT RUN.
- Source-qualified Gate1 pressure dataset: NOT ESTABLISHED.
- G2 geometry-matched aerodynamics / G3 moving-wall energy / G4 audible biological voice: NOT ESTABLISHED, NOT APPLICABLE, NO-GO respectively.
- Tests specific to future figure digitization: no implementation; do not infer scientific test success from documentation CI.

## Gate0 external dependency only
[Draft #218](https://github.com/ryonakayama234/morphoacoustics/pull/218) previously created an experiment-local source ledger and strict source qualification checks, with dedicated exact-head [CI #40455264627](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40455264627) and [Codex exact-head review](https://github.com/ryonakayama234/morphoacoustics/pull/218#issuecomment-6434551910). It is unmerged. No Gate0 experiment code is imported in the Gate1 design branch.

## Future append-only experiment reporting requirements
Record original image/figure source file hash, all raw pixel reads, individual reviewer attribution, calibration transforms/axis tick coordinates, uncertainty ranges, resolved/unresolved marker counts, negative test failures, exact-head CI and review, and honest gate status. Preserve initial RED and all HOLD conditions; use separate commits for source observations and result interpretation. Any future accepted pressure dataset requires an independently audited interpretation of the publication and cannot inherit G2 PASS from Gate1 success.
