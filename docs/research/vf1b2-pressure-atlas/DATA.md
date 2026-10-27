# VF-1B2 Pressure Atlas / DATA — traceability and missing-information ledger
Status: research-only evidence inventory; **NO NUMERIC TAP CURVES CLAIMED**.
The data below describe scientific sources, not a production Character/OrganGraph/Take API.

## Three independent references
1. **M5 uniform-glottis reference** — Fulcher, Scherer & Powell (2011), *Pressure distributions in a static physical model of the uniform glottis: Entrance and exit coefficients*, JASA 129, 1548–1553, DOI [10.1121/1.3514424](https://doi.org/10.1121/1.3514424), [PMC3078031](https://pmc.ncbi.nlm.nih.gov/articles/PMC3078031/). Published axial tap entrance at tap 6, `z=0.211 cm`; exit at tap 13, `z=0.511 cm`. Figure 2 plots pressure distributions for several apertures. Published statements describe measurements averaged over four repeats and experimental uncertainty below 1% **for taps 6–14**, represented as upper-limit error bars, **not** a universal 1σ. The figures, not a verified numeric tap CSV, are presently identified. Model is 7.5× enlarged; pressure/flow scaling must be tracked before using reported life-size equivalents.
2. **M6 3D nonrectangular reference** — Scherer et al. (2010), DOI [10.1121/1.3455838](https://doi.org/10.1121/1.3455838), [PMC2933258](https://pmc.ncbi.nlm.nih.gov/articles/PMC2933258/). Three **AXIAL upstream–downstream** lines of fourteen pressure taps each, at distinct anterior–posterior quarter/middle/three-quarter positions; the 3D glottal contour varies transversely with AP position. Original 'cross-width lines' was incorrect. M6 tap 0 is a **downstream** pressure monitor, whereas M5 tap 0 denotes the upstream tracheal reference. Published Table 2 has 12 experimental **flow** values already checked in [Draft #217](https://github.com/ryonakayama234/morphoacoustics/pull/217) but NOT numerical wall-pressure profiles, and the approximately ±6 cm³/s *flow-meter accuracy* must NOT be assigned to pressure taps.
3. **M5 hemilarynx flow-attachment branch reference** — Fulcher et al., *Pressure distributions in a static physical model of the hemilarynx: measurements and computations*, [PMC4804921](https://pmc.ncbi.nlm.nih.gov/articles/PMC4804921/), [PubMed 18538986](https://pubmed.ncbi.nlm.nih.gov/18538986/). Figure 3 contains flow-wall (FW) and non-flow-wall (NFW) state-conditioned axial pressure measurements and a reported approximately 1% experimental pressure uncertainty upper limit in that experiment. The study used pressure taps on one physical wall and changed jet attachment to obtain different pressure branches; this is **not** simultaneous measurement with independent taps on both walls. **Do not pool** FW/NFW branches or treat CFD curves as measurements.

## Proposed experiment-local source record
```text
ReferenceSource
  source_id / DOI / figure or table / URL / acquisition-date / original-file hash
  model_id                 M5_uniform | M5_hemilarynx | M6_nonrectangular
  tap_axis                 axial | axial_rows_at_three_ap_positions (must be explicit)
  wall_side                physical surface identity separate from jet attachment (FW/NFW)
  physical_model_scale     paper-documented scaling and units
  pressure_reference       tap 0 / absolute / outlet / differential (declared)
  geometry                 aperture, included angle, width, wall contour, entrances
  boundary_conditions      inlet, outlet, pressure/flow operating point
  observations             {tap_id, x_axial_m, ap_s_m_if_M6, wall_id, jet_state,
                           p_raw, pressure_reference, p_pa, uncertainty, source}
  measurement_uncertainty  interpretation and interval (never invent 1σ)
  digitization             figure ID, axis calibration anchors, pixel resolution/error
  acquisition_status       figure_only | machine_readable_original | digitized_audited
```

## Required uncertainty hygiene
Keep **instrument / repeated-measurement uncertainty**, **figure digitization error**, **axis/position calibration error**, **geometric discrepancy**, and **model truncation error** separate. Do not collapse unrelated accuracy bounds to a Gaussian SD. A numeric pressure curve must preserve tap labels, location units and source figure; a plotted interpolation is not a new experimental measurement. Source/model geometry mismatch forces comparison ineligible even if numerical values are present.

## Erratum and corrected technical specification
The pre-correction Gate-0 catalog mistakenly hardcoded M6 `transverse` as the tap axis. Original article Methods / Fig. 3 instead describe **three axial 14-tap rows**, located at AP fractions 1/4, 1/2, 3/4; their axial x positions coincide. This correction is documented and further specified in [Design Refinement v2](DESIGN_REFINEMENT_V2.md). The earlier green tests cannot be interpreted as validating the original geometric reading. M5 tap 0 is upstream; M6 tap 0 is downstream. The two numbered references must never be joined by tap ID alone.

## Evidence right now
M5 axial coordinate anchors (two named taps) and published uncertainty description are retrievable. M6 measured flow data exists in Draft #217. **No complete verified numeric p(tap) file, full tap locations, pressure curve or auditable digitization budget is claimed by this Atlas.** No pressure-to-force interface has been established. Any G2 numerical validation therefore remains INDETERMINATE.
