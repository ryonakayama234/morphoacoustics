# EL-NF5 G0-A2 — original integrity / measurand qualification

**2026-11-01 JST | Issue #269 | RESEARCH_ONLY | LIMITED_ORIGINAL_METADATA_INSPECTION | FINAL_ACOUSTIC_TRUTH_SEALED | NOT_ADOPTED | NO_AUTO_MERGE**

## Read order and source of truth
1. [SYSTEM](SYSTEM.md) — causal boundaries, allowed observation and dataflow diagram.
2. [MEASURANDS](MEASURANDS.md) — Q1–Q6, epistemic statuses, evidence requirements, claim ceilings.
3. [DATA](DATA.md) — K1 primary evidence, published gains, checksum provenance and reference uncertainties.
4. [EXPERIMENT](EXPERIMENT.md) — restricted runner, negative controls and gates.
5. [RESULTS](RESULTS.md) — executed facts, blocked claims; append only.
6. [DECISIONS](DECISIONS.md) — authorization and STOP/GO receipt; append only.
7. [G0A2_RECEIPT.json](G0A2_RECEIPT.json) — machine-readable states (null != zero; NOT_RUN != PASS).

Parents: [D0 #263](https://github.com/ryonakayama234/morphoacoustics/issues/263), [PR #264](https://github.com/ryonakayama234/morphoacoustics/pull/264) at 483f708140899fb16f11eff49d3dde4171e0512c; [G0-A #265](https://github.com/ryonakayama234/morphoacoustics/issues/265), [PR #266](https://github.com/ryonakayama234/morphoacoustics/pull/266) at 169586af338c98e575e32d7796fcf20d4f37a150. Historical negative [NF4 #261](https://github.com/ryonakayama234/morphoacoustics/pull/261). Workspace [PR #155](https://github.com/ryonakayama234/morphoacoustics/pull/155), root `asmr/ARCHITECTURE.md`, [PR #83](https://github.com/ryonakayama234/morphoacoustics/pull/83), [#53](https://github.com/ryonakayama234/morphoacoustics/issues/53).

This task does not train a predictor. A future NF5 predictive surrogate would use **regularized spatial regression** with measured-fit, model-selection, calibration, and sealed final roles; **no neural epochs**. No baseline/threshold/split is changed here.

**Owner authorization** is the 2026-11-01 request to execute G0-A2 with technical discretion, distinct from the earlier G0-A metadata-only milestone. The authorization does NOT extend to opening `Data.IR`, `Data.Delay` numeric values, G0-B, G1–G5, model training, a production API, Core, SMC, Studio, or main.
