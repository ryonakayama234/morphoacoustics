# VF-1B2 / M5 scalar pressure recovery — RESULTS

2026-10-27. **Result: published-scalar non-transferability finding; NOT spatial tap-pressure validation.**

## Chronology and evidence
- Core [Draft PR #222](https://github.com/ryonakayama234/morphoacoustics/pull/222) based directly on main e05e3274; independent of [Draft #218](https://github.com/ryonakayama234/morphoacoustics/pull/218).
- SYSTEM, DATA and EXPERIMENT preregistered in three commits (086ec5f6, 3d4e601d, f7c91123) **before any experiment data and code**.
- Source: [Fulcher, Scherer & Powell (2011), DOI 10.1121/1.3514424](https://pmc.ncbi.nlm.nih.gov/articles/PMC3078031/). Table I reports Q; Table II contains k-exit coefficients experimentally **derived from pressure differences and Q**, not independent raw tap pressures. 35 published complete pairs, 13 blank condition cells retained. Exact source Git blob SHA 026f91bb98380254d111bf8e84e24a23818eed6e.
- [Exact-HEAD GitHub CI run #40498091376](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40498091376) for source 30d8071cc5a4fe9f372012836cd31d21fe236a3b: **SUCCESS, 18/18 unit/negative tests, exact checkout asserted, JSON evidence artifact ID 12731202545**. These results apply strictly to that code commit; subsequent doc commits need independent CI confirmation. Independent original-source reviewer pending.

## Full-matrix result (paper-derived reference vs original untuned IM Eq.3)

| Condition | Published experimental k-exit | Untuned IM abrupt-exit k-exit |
| --- | ---: | ---: |
| d=0.02 cm, transglottal pressure 5 cmH2O | +0.219 | +0.0198 |
| d=0.16 cm, transglottal pressure 5 cmH2O | +0.055 | +0.1472 |

**Geometry intervention:** larger d changes published k from 0.219 to 0.055 (decrease), but IM from 0.0198 to 0.1472 (increase): direction reversed. **Pressure intervention:** at d=0.02 cm and pressure 3, 5, 10, 15 and 25 cmH2O, published k is 0.275, 0.219, 0.167, 0.146 and 0.111, whereas IM is constant at 0.0198. At d=0.005 cm, all five published k values are negative, as defined by p16 - p11 below zero. IM predicts positive for all 35 source geometries.

**All 35 cases:** IM-minus-published coefficient absolute mean 0.24026044642857144, maximum 1.320471875; **7 mismatched signs**. These are dimensionless coefficient discrepancies, **not** normalized per-tap pressure errors or uncertainty-calibrated significance.

## Algebraic reconstruction; no invented pressure data
Paper Eq.2 defines k = 2 A11² (p16-p11)/(rho Q²). Using paper density 1.21 kg/m³, glottal length 1.2 cm and d=0.02 cm gives A11=2.4e-6 m². At 5cmH2O the published Q=41.6cm³/s and k=0.219 imply p16-p11 approximately **39.8 Pa**; total transglottal pressure converts to 490.3325 Pa. This reconstructed pressure difference uses the SAME published Q and experimentally-derived k, so it is **not an extra independently measured p(tap) observation**. Original FW/NFW distributions were averaged when the authors calculated the coefficients.

## Interpretation and stopping rule
- H-SIGN, H-DRIVE, H-GEOMETRY are supported for this published fixed-wall M5 experiment. H-RECONSTRUCTION holds only as an SI/algebraic identity.
- The paper's rounded M5 exit and the Ishizaka–Matsudaira sudden-expansion assumption differ; this test rejects **unconditional formula transfer to this geometry**, not conservation laws or every 1D model.
- **G0** source-table integrity software checks passed, independent human/source audit pending.
- **G1** declared scalar SI and algebra software checks passed.
- **G2** INDETERMINATE: no audited full numeric pressure-tap field or eligible geometry-matched flow model.
- **G3** HOLD: no moving-wall pressure-to-force/power ledger.
- **G4** VOICE NO-GO: no creator-audible or Character/Studio validation.

The **stop reason** is structural: 35 aggregate coefficient values cannot reconstruct 14 or more signed, positioned wall-pressure samples and their spatial uncertainty. Do not drive tissue force or adopt an aerodynamic pressure law from a scalar fit. No Core production/OrganGraph/Studio/SMC/ASMR edits.

**Evidence-driven next decision:** (1) preferred independently acquire M5 Fig.2B d=0.02 cm full tap locations/condition-specific pressures/reference/FW-NFW and digitization error; (2) if impossible, use separate published geometry-specific scalar challenges without extrapolating to forces; (3) independently derive a conservative moving-wall two-port power identity on paper only, but do not simulate until G2. Draft PR must remain unmerged pending independent audit.
