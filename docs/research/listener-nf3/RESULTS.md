# EL-NF3 — RESULTS / append-only evidence ledger

## 2026-10-30 D0: preregistration frozen, prior to any implementation
- GitHub issue #256; isolated research branch `research/asmr-el-nf3-geometry-guard`.
- Frozen research protocol commit `df6addb58296e9945569ff3473aa65039ef959cb`.
- Public source metadata identified: Li et al 2023 KEMAR Zenodo 7626148; reported 83,448 measured positions 0.20–1.10m; published measured file MD5 `8e286f7f2ffa67973bb0eb2e37c158e2`.
- Original measured file **NOT YET VERIFIED / NOT SCORED**, actual SHA-256 unknown; license status **UNVERIFIED**. Open/blocked ear physical plane and reference signal **NOT VERIFIED**.
- No EL-NF3 numerical outcome, no production adoption and no Studio feature.
- Previous EL-NF2 #255 result: numerically promising but failed prespecified confidence gate, and **must not count as NF3 evidence**.

## Pending
G0 original file audit and license; G1 synthetic & implementation reproducibility; G3 new physically measured unseen-area evaluation and independent-arithmetic audit; G4 optional blind audition; G5 reviewer distinct from author.

**Never fill in real measured scores from test fixtures, planned experiments, or a successful CI job.** Append dated results including actual dataset SHA-256, Git commit, split hash, independent blocks, all model rows, failures/refusals and final prereg verdict.


## 2026-10-30 D1–D3: original measured KEMAR negative/inconclusive spatial coverage result

**Real original SOFA acquired and published MD5 verified.** Successful GitHub Actions [measured run 41058197316](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41058197316), [evidence artifact 12978281733](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41058197316/artifacts/12978281733) (30-day GitHub retention). Source original `KEMAR_NFHRIRmea_1cm.sofa` (Zenodo 7626148), published MD5 `8e286f7f2ffa67973bb0eb2e37c158e2` MATCH; actual source SHA-256 `0bda73c4c80233502421adf7c8c2aafddfbe00a6a734cbdd3160bbb9001bbf88`. 83,448 binaural HRIR positions, 48kHz, 256 samples; radii 0.20–1.10m, elevations -25..35°, azimuth 0..355°, 144 independent angular-block labels. Dataset data remain on runner only, NOT in repo/artifact.

Coordinate-only roles from frozen split hash `f6dd7ce2ea5b1bcbfa5ce0b9671122d1ce9ab2d1ab27b5fa253212c0b8e3e5bd`: train 16,341 positions; model selection 7,746; calibration 7,775; final 16,797; 5° buffer 34,789. This is a **highly conservative split**; nearby measurements intentionally do not leak into final fitting. Primary evaluation picked only one target per final block and prereg radial location, **155** final query records (S1/S2), not 16,797 independent tests.

### Pre-final model-selection signals (NOT G3 proof)

| Method | Model-selection pooled median four-band ILD error (dB) |
|---|---:|
| B0 nearest Cartesian sample | 0.96759125 |
| B1 raw Cartesian IDW | 1.06479906 |
| B2 3D Delaunay barycentric | **0.78276672** |
| C1 peak-arrival-separated | 3.06461232 |
| C2 local angular/radial geometry + onset separation | 0.70056783 |

Selection-only best *eligible baseline* B2 was frozen before final metrics; C2's lower selection point estimate does NOT validate generalization.

### Frozen final spatial-block result

- **C2 geometric prediction coverage: 0 / 155 = 0.0%.**
- **C2 accepted/calibrated coverage: 0 / 155 = 0.0%.**
- The prespecified G3 minimum is 80% coverage and >=8 independent supported blocks in each S1/S2 fold; neither holds.
- Therefore final paired B2 vs C2 ILD, ITD, spectral error and bootstrap CI are **NOT ESTIMABLE**, and must be represented as `null`, not as zero error, infinite improvement, or numerical success.
- **G3 NUMERICAL VERDICT = INDETERMINATE; SCIENCE_ADOPTION = NOT_ADOPTED.** The zero coverage is an actual negative **applicability observation** under the frozen geometry guards. It is NOT evidence of superior or inferior C2 sound prediction on accepted new locations (there were none).
- Independent-from-predictor arithmetic/evidence auditor PASS, but this is still author-authored arithmetic verification, not G5 independent science review.
- Actual receiver measurement physical plane and source normalization remain **UNVERIFIED**; the KEMAR Zenodo visible record did not establish a specific distribution/reuse license. Hence no absolute ear-drum Pa, source-load coupling or Studio runtime authorization.

### Software/CI chronology and failure transparency

- Early synthetic+real full-run attempts triggered a valid software bug: when all final positions were rejected, a model's undefined `inf` median leaked to JSON output and stopped evidence writing. **Do not call the earlier failure a scientific metric.**
- Replaced absent paired metrics with JSON `null` without changing frozen geometry, heldout selection, model weights, G3 thresholds or source data. Added synthetic end-to-end regression to ensure the refusal-only state can generate auditable evidence.
- Final [synthetic CI 41058196865](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41058196865) success on Python 3.11/3.12; original measured G0–G3 runner + independent arithmetic audit [41058197316](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41058197316) **SUCCESS**; scientific inference remains **INDETERMINATE**.

**Follow-up:** Analyze refusal reasons using the frozen evidence artifact (angular simplex, shell topology, boundary/axis checks), perform prospective measurement topology and reference-plane review, and open a **new preregistered successor** only if a distinctly justified model/support domain can be proposed. Never relax C2's 25° support rule against this already opened final holdout and reuse it as a fresh blind test. The present branch is a reproducible negative scientific record and must remain Draft; no production adoption.


### D3a: evidence-only posthoc refusal analysis, 2026-10-30

Using the **already frozen** original G3 artifact, a separate GitHub Actions evidence-only reviewer [run 41059171559](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41059171559) downloaded only the stored JSON, not the acoustic dataset, and counted `final_rows[*].models[*].reason`. This is a posthoc **descriptive diagnosis**, not a fresh test or permission to revise v1.1.

| Predictor | Accepted geometrically | Unsupported |
|---|---:|---|
| B0 | 155 / 155 | 0 |
| B1 | 155 / 155 | 0 |
| B2 | 127 / 155 | 28 outside 3D Cartesian convex hull |
| C1 | 155 / 155 | 0 |
| C2 | **0 / 155** | **144 angular simplex span >25°; 11 outside angular convex hull** |

- S1: 102 queries; all 102 C2 refusals were `Angular simplex exceeds 25 degrees`.
- S2: 53 queries; 42 C2 refusals from angular span, 11 from outside angular convex hull.
- Under the frozen 20°×10° independent angular-block holdout plus a 5° data exclusion buffer, C2's strict triangulation guard does not support new locations. This is an **applicability-design incompatibility**; no accepted final HRIR exists to assess actual C2 acoustic prediction accuracy.
- B2 itself loses coverage for 28 targets and the baseline selection stage did not create a universally supported model; B0/B1/C1 remain available at all 155 positions but without the same geometric guarantee. Do not infer those algorithms are scientifically reliable merely because they return output.
- **Next study hypothesis (NOT tested here):** geometry guard and spatial-block holdout geometry were mutually incompatible; to improve support without extrapolation requires a newly justified interpolation topology, new prespecified domain/withheld design, and truly fresh blind acoustic evidence. **Do not tune the 25° cap using the current final data.**

No code, source IR, heldout masks, or G3 decision thresholds were changed for this analysis. G3 remains `INDETERMINATE`, C2 `NOT_ADOPTED`.
