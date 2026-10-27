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

## Recorded dataset and scientific CI evidence — 2026-10-27
Measured rows: 12/12 from Scherer et al. 2010 M6 **experimental** columns. Input `m6_table2_experimental.csv` fixed SHA256 `febecab692b5eb78d2e73520d27556c368de5cff4691ff02c20baab64556b6d0`. Scientific head `d7213d70ceb49b66a12cf2be58a2c8761154fe1a`, [dedicated CI #40432872175](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40432872175): 20/20 tests passed, 12 comparison rows, and 20th-century paper data kept separate from toy computed flow. Earlier implementation head `1696937` was also 16/16 green in [CI #40432635526](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40432635526); follow-up strengthened verdict and metadata poison checks.

| Δp Pa | measured M6 convergent/uniform | measured M6 divergent/uniform | worst-case M6 divergent/uniform ratio from approximate ±6 cm³/s accuracy | toy divergent/uniform |
|---:|---:|---:|---:|---:|
| 294 | 1.00861 | 1.08685 | [1.03899, 1.13702] | 1.20000 |
| 491 | 1.03330 | 1.10021 | [1.06307, 1.13871] | 1.20000 |
| 981 | 1.02323 | 1.09293 | [1.06697, 1.11954] | 1.20000 |
| 1472 | 1.03770 | 1.07539 | [1.05446, 1.09676] | 1.20000 |

These are *descriptive* flow-rate ratios, not an independently matched M6 pressure-tap experiment. Because the ±6 figure is an estimated measurement accuracy rather than a statistically defined standard uncertainty, do not derive a confidence interval, p value, or formal physical accuracy PASS. The toy's arbitrary twofold area ramp is not the real 10° three-dimensional sinusoidal M6 contour.

Archivable raw evidence is the GitHub Actions artifact `vf1b2b-m6-flow-reference-evidence` containing test log, test-status JSON, 12-row comparison CSV and independent result JSON. After this append-only documentation update, the exact final branch head needs another Actions check. Core main/Studio/Takes were not changed.
