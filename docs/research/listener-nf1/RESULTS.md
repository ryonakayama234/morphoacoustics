# EL-NF1 — append-only evidence ledger

## 2026-10-30 G1 preregistration
The preregistration was committed as `c41ad05b1d8215574aad61d12728630032c97c81` **before** experiment implementation, measured-data evaluation, or outcome selection. Original dataset is external and source-indexed. The preregistration does not claim any empirical result.

## 2026-10-30 G2 software implementation
Implementation and synthetic tests were added separately to the research branch. Synthetic oracle tests and mutation/rejection tests can demonstrate processing correctness, **not measured-head performance**. Until real SOFA CI evidence is examined and independently checked, G0 and G3 are PENDING. Any validated measured results must be appended below with exact GitHub Actions run, SHA-256, statistic table, holdout count and disposition.

## G4 / G5
Human blind headphone reports: PENDING. Independent physical/acoustic/code review: PENDING. Production/Studio adoption: NOT_ADOPTED.

## 2026-10-30 — G0/G3 first genuine measured SOFA evaluation (historical exact-head run)

- Evidence execution: [GitHub Actions run 40986155089](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40986155089), commit `6ece1efce87fd9e005194492f716bce08cc8dddf` before the subsequent evidence-auditor additions, conclusion **SUCCESS**. [Download artifact 12947540780](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40986155089/artifacts/12947540780) (30-day retention); artifact was actually retrieved and inspected.
- Dataset is *real original* `NF_LIB_HRTF_measured.sofa` (no LFE), MD5 `4ba9cc348801a6805265c7168b5b3227` verified. Dataset SHA-256: `1dd95d4d11f9d92764d039786ed3a010e1780ce8bdf414233bbd3e46f5709640`. SOFA `SimpleFreeFieldHRIR` v1.0, 48,000 Hz, raw IR 2,400 samples, effective `Data.Delay=0` samples; source spherical `degree, degree, metre`. ReceiverPosition reported spherical / `metre` **ambiguous**; no calibrated absolute pressure or anatomical observation plane claim.
- Matched 49 source directions in all 4 radii; evaluated 49×2 hidden-distance folds×3 models = **294 records**. Primary 4-band pooled median absolute ILD errors: **B 0.8320600 dB**, **C0 0.7541991 dB**, **C1 0.5047246 dB**. Relative C1 vs B improvement **39.34%**, C1 vs C0 **33.08%**.
- Fold F30: B **1.3775654 dB**, C0 **1.3668505 dB**, C1 **0.8670119 dB**; fold F40: B **0.5275479 dB**, C0 **0.4482590 dB**, C1 **0.2968292 dB**.
- Median absolute ITD errors: B **6.2248 µs**, C0 **3.0346 µs**, C1 **2.8371 µs**. Preregistered paired cluster-bootstrap 95% CI of median ILD improvement B−C1: **[0.1772875, 0.4154118] dB**, 2,000 direction-resamples, seed 20261030.
- **G3 quantitative outcome: GO_LIMITED_NUMERICAL_CANDIDATE** under the *frozen* engineering criteria; this is **NOT** release or G5 approval. The archived evidence fields were independently recomputed using an evidence-only arithmetic auditor; the auditor has since been added to code and CI. It does not independently re-run physical measurements or corroborate open/blocked receiver plane.

## Pending claim limits and validation
- The evidence describes relative left/right *artificial-head* responses **only within 20–50cm** and the data's four radial measurement planes. The result does not demonstrate naturalness, human externalization/ASMR, personalized HRTF, 1cm/contact acoustics, calibrated Pa, eardrum pressure or source–ear coupling.
- Need exact-head rerun with `audit.py` and all 12 synthetic/mutation tests **after auditor changes**; the earlier first measured run is retained, not passed off as the latest audit run.
- G4 human blind headphone listening: **PENDING**. G5 independent scientific/code reviewer and explicit adoption decision: **PENDING**. **No main merge**.
