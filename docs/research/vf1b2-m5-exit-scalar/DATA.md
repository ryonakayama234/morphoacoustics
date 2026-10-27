# VF-1B2 / M5 scalar recovery DATA
Date: 2026-10-27. Source: Fulcher, Scherer, Powell (2011), *JASA* 129, 1548–1553, DOI `10.1121/1.3514424`, [PMC3078031](https://pmc.ncbi.nlm.nih.gov/articles/PMC3078031/), **Table I: flow rows**, **Table II: exit coefficients**. Material is a direct published numeric-table transcription, NOT figure digitization.

## Data contract (life-size equivalents published in source)
- All pressure conditions are in `cm H2O` {1,3,5,10,15,25}; convert to Pa with `98.0665 Pa/(cm H2O)` as a declared SI conventional conversion, not an instrument uncertainty estimate.
- Glottal diameters `d_cm`: {0.005,0.0075,0.01,0.02,0.04,0.08,0.16,0.32}; `Q_cm3_s` comes from Table I first row; `k_ex` (dimensionless) from Table II. **Blank cells stay blank**. There are exactly **35 published complete condition pairs**. The M5 experiment used a 7.5x scale; the paper expresses reported Q/pressures in life-size equivalents, and the above equations use that convention. Density `0.00121 g/cm^3 = 1.21 kg/m^3`, fold AP length `1.2 cm`, vocal tract cross-section `2.4 cm^2`.
- Printed numeric precision of Table I/II is limited; reconstructing `p16-p11` adds algebraic/roundoff uncertainty. No paper-based `sigma` for individual reconstructed pressure differences is claimed. No raw `p11`, `p16`, tap coordinates apart from paper geometry, inlet profile, tap-to-wall forces, FW/NFW samples or turbulence inferred.
- Table I `Q` and Table II `k_ex` are **not independent datasets** because Table II derives `k_ex` using measured Q. Never count the algebraically reconstructed pressure difference as an extra external validation observation.
- The source averaged jet-side measurements for the coefficients; do not recover a FW/NFW spatial pressure curve by reversing that average.

## Exact source and integrity
Store columns `d_cm,pressure_cmH2O,flow_cm3_s,kex_experimental` in source-ordered CSV, 35 data records. Keep an explicit literal per-row comparison in tests and pin the audited Git blob SHA of the CSV after it is transcribed. A source hash identifies the reviewed table transcription, **not** authenticity of the article itself. A cited full table must be checked by independent reviewer against the original article.

## Scope distinction
Gate `SCALAR_SOURCE_VERIFIED` means integrity and units of published aggregate data, **not** `PRESSURE_TAP_REGISTERED`, `G2_PRESSURE_PROFILE_PASS`, `G3_FSI_PASS` or `G4_VOICE_PASS`. Fig.2B `d=.02 cm` remains separately planned in [Draft #218](https://github.com/ryonakayama234/morphoacoustics/pull/218).
