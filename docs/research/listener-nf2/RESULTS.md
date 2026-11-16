# EL-NF2 — append-only evidence ledger

## 2026-10-30 D0 design freeze
Design and prespecified coordinate split recorded before implementation and measured heldout scoring. Initial state: **NO EMPIRICAL EL-NF2 RESULT / RESEARCH_ONLY / NOT_ADOPTED**. Dataset source and relevant predecessor PR #252 are known; predecessor measured results are **not** new NF2 evidence.

## Pending
- G0 exact original SOFA integrity + coordinate/routing audit.
- G2 independently implemented synthetic algorithm, refusal/mutation tests.
- G3 real unknown-direction and jointly hidden direction/distance result, exact-head Actions artifact, separate arithmetic audit.
- G4 human blind listening (not inferred from CI).
- G5 distinct independent acoustic/code reviewer; formal adoption requires separate decision.


## 2026-10-30 D1–D3: first frozen real SOFA direction×distance holdout

**Exactly-before chronology:** prereg frozen at `9915d101cdbba273b7c69813098d4e14a364abb7` before code and measurement. First measured experiment after all code and synthetic tests was [GitHub Actions 41050468955](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41050468955), [immutable evidence artifact 12974606905](https://github.com/ryonakayama234/morphoacoustics/actions/runs/41050468955/artifacts/12974606905) (30-day GitHub retention). Exact PR head at original run: `7a3020f7abfc82d3c79872f57ec29ff177987787`; GitHub Actions PR merge SHA `cba8fb70f6842aea82bf2adc27fedc723eacc11d`. **CI: SUCCESS, independent-from-predictor arithmetic audit: SUCCESS; scientific gate G3: REVISE_OR_REJECT.** Successful runner does not imply model passes.

Dataset source: genuine original `NF_LIB_HRTF_measured.sofa`, original MD5 `4ba9cc348801a6805265c7168b5b3227`; observed SHA-256 `1dd95d4d11f9d92764d039786ed3a010e1780ce8bdf414233bbd3e46f5709640`; 48kHz, 2400 raw samples, `Data.Delay` 0. Source measured 0.2–0.5m. `ReceiverPosition` spherical with unit `metre`: anatomical/acoustic plane **still UNVERIFIED**.

Frozen coordinate grouping: 29 train, 10 validation, 10 final directions, entirely disjoint direction groups. Final: 10/10 directions support within the stated 45-degree nearest-direction bound. 10 final direction clusters × 4 target radii × 3 models = **120 paired final model records**; validation also 120; audit total **240** rows.

### Final heldout measured ILD error (median of four bands, dB)

| Metric | B0 nearest | B1 direct HRIR | C1 arrival separated |
|---|---:|---:|---:|
| Pooled 0.2/0.3/0.4/0.5m | 2.384543 | 2.751612 | **1.921281** |
| S1: unseen direction at endpoints | **1.689906** | 2.637767 | 1.977311 |
| S2: unseen direction and interior radius | 2.622648 | 2.805930 | **1.663565** |
| Pooled median ITD absolute error, microseconds | 112.474 | **72.206** | 74.088 |
| P95 four-band ILD error, dB | 9.728 | 9.530 | **8.458** |
| Normalized per-ear spectral shape median RMSE, dB | **2.382** | 4.692 | 2.581 |

C1 final pooled ILD median reduces B1 error by **30.18%**, and both S1 and S2 medians improve vs B1. C1 is slightly worse ITD than B1 (+1.882 microseconds), within preregistered non-inferiority allowance. **But** paired direction-cluster bootstrap 2000 resamples B1−C1 median ILD improvement 95% interval **[-0.087808, 1.418374] dB**, crossing zero; frozen G3 therefore fails. Do not publish this as a successful generalizing receiver.

### Validation split / transfer caution

Validation directions show B0 **1.193149** dB, B1 **2.543739** dB, C1 **2.210226** dB pooled median ILD error. Validation C1 vs B1 paired 95% interval **[-0.676412, 1.177555] dB**, crossing zero; C1 vs B0 is substantially worse. The discrepancy between final and validation spatial directions warns of local geometry sensitivity / underpowered single-head direction clusters, not broad proof. Generalization cannot be inferred solely from final pooled point estimate.

### Interpretation / evidence limitations

- H1 time-alignment candidate has *numerical point-estimate advantages vs raw HRIR interpolation* on the final direction split, especially joint direction/radius S2, but fails statistical support gate; **H1 remains unconfirmed, not accepted.**
- H2 broadly claims joint spatial generalization beyond elementary alternatives. B0 outperforms C1 on S1 and validation, so **H2 is not established**.
- H3 bilateral relation: no explicit learned joint-ear regularization was implemented; ILD/ITD were measured, **H3 not tested as a separate interventional hypothesis**.
- H4 uncertainty calibration not implemented; 45-degree guard only certifies domain refusal, **not reliability of predictions**. Test this separately.
- H5 motion synthesis intentionally excluded (no dynamic proof).
- Each-direction sample size 10 final clusters; 196 measurements are from one head, not 196 independent heads.
- Source delay peak uses the strongest HRIR sample as proxy, not necessarily physically first-arriving wave. C1 peak selection and angular IDW can introduce spatial bias.
- The prespecified "convex local angular cap" language is not fully enforced by the current implementation; **only radial bounds and 45-degree nearest-direction guard are implemented**. Thus the claimed geometric support is an engineering guard, not a proven interpolation-hull certificate. A future domain classifier needs a separate preregistered gate. Explicitly report this shortfall rather than silently changing success criteria.
- Per-ear spectral shape is **mean-centered against each measured response as a diagnostic metric only**; it is not a fitted source or absolute pressure calibration.
- This run is a **negative scientific result with a valid measured-data and software-evidence artifact**. Do not tune on the final test split or weaken the frozen bootstrap threshold. Any successor improvement must be a new experiment with newly frozen independent evaluation, preferably a distinct measured dataset.

### Independent validation status
Author-authored `audit.py` independently re-aggregates stored errors and detects forged summaries/CI/leakage; this is NOT a distinct scientist or independent raw-HRIR reanalysis. G4 blind human report **PENDING**, G5 distinct independent reviewer **PENDING**, adoption **NOT_ADOPTED**.
