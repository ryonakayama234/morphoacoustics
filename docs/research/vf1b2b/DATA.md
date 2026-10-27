# VF-1B2b DATA — immutable published flow measurements and narrow comparison receipt

**Preregistered before experiment source. NOT a public character/organ/interface schema.** All data are 2010 M6 experiment **measured** flow, not the article's CFD results. Reference [Table 2](https://pmc.ncbi.nlm.nih.gov/articles/PMC2933258/), DOI 10.1121/1.3455838. Paper explicitly states estimated flow-meter accuracy approximately **±6 cm³/s** in real-life equivalents. Preserve this as an accuracy interval only; do not call it 1σ or a confidence interval.

## Frozen 12 experimental Table 2 entries
```text
Δp (kPa)    convergent 10°   uniform 0°   divergent 10°   [Q: cm³/s, real-life]
0.294           257.8          255.6          277.8
0.491           344.4          333.3          366.7
0.981           488.9          477.8          522.2
1.472           611.1          588.9          633.3
```
Unit conversion: 1 kPa=1000 Pa; 1 cm³/s=1e-6 m³/s; 0.122 cm²=1.22e-5 m²; 6 cm³/s=6e-6 m³/s. Published entries for 1.962/2.453 kPa are deliberately not part of this four-pressure experiment and must not be inferred from CFD.

## Experiment-local immutable types
- `M6Reference`: source DOI, article table, `shape`, `delta_p_pa`, `q_measured_m3_s`, `flow_accuracy_abs_m3_s`, `area_min_m2`, experimental `scale=real_life_equivalent`; original table textual fixture and sha256; NO fabricated wall tap arrays.
- `ProxyAssumptions`: `rho_kg_m3=1.21` declared assumption, `cd=0.7` declared non-calibrated inherited #216 default; `Amin=1.22e-5 m²` normalization only; parallel `(A0,AL)=(A,A)`, convergent `(2A,A)`, divergent `(A,2A)`, `separation_area_ratio=1.2`; the twofold endpoint assumption is NOT measured M6 geometry.
- `ComparisonReceipt`: source/implementation sha256, exact commit SHA, M6 12-entry SI table and measured interval, predicted toy Q, residuals and common-ΔP ratio comparisons, worst-case ratio accuracy interval `(q_shape-6)/(q_uniform+6)` to `(q_shape+6)/(q_uniform-6)` for positive measured Q in cm³/s, `geometry_match=false` with precise reasons, explicit `pressure_tap_data_available=false`, disjoint G0/G1/G2/G3/G4 verdicts and failing controls. No numeric pressure-measurement claim.

## Evidence and trust
- SCIENCE fixtures from publication, conversion, model prediction, and output receipts must be separately traceable; don't treat an output SHA as proof of independent input authenticity.
- Calculated toy outputs must never overwrite measured entries; comparison cannot fit Cd or separation criterion to reference values.
- Test failure, missing known-source fixture, unresolved external pressure-geometry mapping, or unavailable CI/reviewer stays visible and prevents promotion. Negative controls must fail upon tampered units, swapped shape, wrong sign, data corruption, forged geometry-match flag, and missing fixture.
- Studio's existing `PANEL_REGISTRY.json` is an approved design reference, not a dataset to edit. UI does not acquire physical source-of-truth.
