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

## Result
NOT RUN at preregistration commit. Later update must include actual CI run, implementation SHA, full result JSON summary, error bars/limitations (model mismatch unquantified) and independent reviewer disposition. Do not label S1 complete, S2 started, real vowel, or creator voice GO.
