# VM-1D EXPERIMENT — protocol and record
**Gate A fixed before code** at issue #205. This file separates *prospective thresholds* from subsequent results.

## Protocol
1. Validate frozen byte-accurate experiment-028 Git blob and M0 16-area length; derive M1 as 11mm sections, same frozen /a/ area vector. Assert physical positivity and SI.
2. Calculate the 16×2-port lossless transfer independently of the adopted time-domain waveguide. Apply the same continuous B0 load in all cases.
3. First calibrate against closed-form uniform matched-tube propagation for `f=[100,600,2500] Hz`, positive passive `R_s/Zc=[0.1,1,10]`. Verify determinant and exact power.
4. For each frozen body, run prescribed `Uin=1e-6 m³/s` and finite `pdrive=1 Pa` × three `Rs` cases. Record full complex transfer/actual flow/power. Compute within-condition mouth pressure 600/100 ratios. Report signed delta dB to ideal-flow **without suggesting matched listening conditions**.
5. Failure injection: negative resistance, zero pressure, nonfinite pressure or geometry, arithmetic power manipulation. A failing negative control means scientific FAIL, not a missing result.
6. JSON stdout/result: physical assumptions, hashes and explicit G0/G1/G2/G3/G4 statuses. Artifact retention should be an auditable CI failure path; no acoustic recordings created.

## Preregistered gates
Independent complex relative oracle <=1e-10; duct determinant absolute error <=1e-10; relative source + duct power errors <=1e-9 (subject to nonzero normalization); all negative controls rejected; body digest matched. Numerical identity and flow positivity required. **No preregistered expected sign of 600/100 response change**. >0.1 dB absolute change is a research sensitivity threshold, not a physics validation or perceptual threshold.

## Result / evidence update 2026-10-26 (postimplementation, not part of preregistration)

**Precode freeze**: Gate A `689ea71e`; SYSTEM `f6d2ce3d`; DATA `993074e0`; EXPERIMENT `4a64716b`. Exact current source branch before this record update: `66b23f1c940751f49959820097c2b5812523eaf1`.

Initial [science run #40250606162](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40250606162) **FAILED** after scientific pytest passed: `numpy.bool_` in the independent uniform oracle was not JSON serializable, causing both research report emission and artifact upload to fail. The failed run and missing evidence are not reclassified. Fix `42e46a2` cast numerical flags to Python bool, added serializability fallback for bad reports, added strict JSON regression `b7e545f`; rerun [#40250760516](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40250760516) PASSED with an uploaded JSON artifact.

Latest measured [science CI #40250921492](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40250921492) PASSED the **six VM-1D tests, JSON write, artifact upload** at branch source `66b23f1` with executed Actions PR-merge checkout `ce7d124cabc0dcb96ac8c3704d04bf7473cb73ce`. Full result stored as a workflow artifact. Actual stdout corroborated:

| Frozen body | ideal prescribed Uin, H600/H100 | finite Rs=0.1Zc,in | Rs=1Zc,in | Rs=10Zc,in |
|---|---:|---:|---:|---:|
| M0, 16×10mm | +34.686927 dB | +10.538360 dB | +25.943086 dB | +34.272801 dB |
| M1, 16×11mm | +55.188975 dB | +12.538814 dB | +27.956318 dB | +45.074789 dB |

**Sensitivity verdict:** for both geometries, all three positive-resistance pressure-source models differ by >0.1 dB from the ideal prescribed-volume-flow ratio. Thus the narrow H0 is **falsified in this declared model**; inlet source impedance can strongly alter frequency selectivity, even though the fixed tract and B0 law are unchanged. Do not interpret ideal flow vs 1Pa pressure-drive as same-level audio A/B: these are different boundary-condition transfer functions.

- Independent analytic uniform matched-tube relative complex error: `5.66105e-16`; maximum `|AD−BC−1| = 2.88658e-15`; maximum relative acoustic power mismatch: `2.78752e-15`. These are floating-point numerical identities inside the modeled assumptions, not physical or biological uncertainty.
- Seven negative controls PASS, including negative resistance and forged source-power ledger. Reported source/port powers are SI, `p_mouth` is **not** `p_ear`.
- Limitations: idealized fixed pressure reservoir+positive series resistance is **not** a phonating larynx; frozen rigid 1D tract, continuous B0 is neither real lip radiation nor calibrated wall loss; no tissue self-oscillation, named receiver, waveform or creature-quality audio. Physical model mismatch remains **unquantified**.
- Gate classification: **G0/G1 bounded numerical PASS; G2 INDETERMINATE (no independent biological source reference); G3 NOT_RUN; G4 VOICE_NO_GO_UNCHANGED**. Do not declare S1/S2 complete, publish a graph ABI, merge main, or edit Studio.
- **Independent audit corrections:** The first Codex review of earlier head `c35bcee` found P1 JSON failure (fixed) and a further **P2 power-gate masking failure**: normalizing duct power mismatch against huge upstream source-resistor loss can falsely accept a distorted duct pressure. Fixed at `9000a853` by separating `duct_relative_residual=|Pin−Pmouth|/max(|Pin|,|Pmouth|,...)` from source-power relative mismatch; exact counterexample `p_mouth×1.0000001` under `M0,100Hz,Rs/Zcin=10` is rejected by new regression `3b15bc72`. This is a scientific measurement-gate correction, not a model-law or audio modification.

[Repaired dedicated CI #40251207899](https://github.com/ryonakayama234/morphoacoustics/actions/runs/40251207899) **PASS** on 7 scientific tests plus JSON/report artifact; executed GitHub PR merge checkout `429e66aebbafbaaab5b3bdb3b531d77f68d52726`, branch source `3b15bc72`. New worst strict relative power residual `1.40127e-13` (separate local normalizers); matrix determinant error `3.55271e-15`, uniform oracle complex relative error `4.88737e-16`. Ratios in the table remain unchanged within floating-point precision. Historical prior first-pass figures above must be read as pre-power-gate-fix numerical diagnostics, not the definitive negative-control result.

**Independent @codex re-review of the repaired exact final head remains required** before bounded technical disposition; no main/product adoption. 
