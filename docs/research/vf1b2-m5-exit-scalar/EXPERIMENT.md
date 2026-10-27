# VF-1B2 / M5 scalar recovery EXPERIMENT — preregistration
Date: 2026-10-27. **Committed before any experiment source or table transcription**. Parent Issue #215; scientific v2 plan in Draft #218. Reproducibility requires same-source literal verification, exact-head CI and independent audit. No retrospective threshold changes.

## Hypotheses (predeclared)
- **H-SIGN**: in Table II, all five available `d=.005cm` coefficients (3,5,10,15,25cmH2O) are strictly NEGATIVE, whereas all five available `d=.02cm` coefficients are strictly POSITIVE. Falsified by literal source values differing from this pattern. A coefficient negative means `p16-p11<0` by the paper's definition, **not** impossible real fluid behavior. This is a published-reference check, not a solver prediction.
- **H-DRIVE**: for `d=.02cm` the five increasing-pressure conditions (3→25 cmH2O) show strictly decreasing `k_ex`. Formula IM at constant diameter has `d(k_ex_IM)/d(Delta p_T)=0`, so it cannot exactly represent that measured pressure dependence. Falsification: printed Table II has an identical constant series or the formula actually contains pressure dependence.
- **H-GEOMETRY**: for **the same measured 5 cmH2O condition**, M5 coefficients at `d=.02cm` versus `d=.16cm` decrease as diameter grows; untuned IM Eq.3 increases with diameter in this area-ratio regime. Require opposite signs of the two changes. This is a qualitative disqualification of the specific IM abrupt-exit formula in M5's smoothly rounded geometry; no fitting/no model-selection rescue.
- **H-RECONSTRUCTION**: algebraic inverse `p16-p11=k_ex rho Q^2/(2 A11^2)` yields a signed *derived* pressure difference; forward-recover `k_ex` within floating-point roundoff; at pressure-diameter cases with equal sign as `k_ex`. Proven only for algebraic and unit consistency, not raw measurement accuracy.

## Locked measurements, selection, and reporting
Primary condition `d=.02cm` at 3,5,10,15,25cmH2O; narrow control `d=.005cm` same 5; geometry intervention at `Delta p_T=5cmH2O, d=.16cm`. **All** 35 table pairs archived to prevent cherry picking. Complete matrix reports `N=35`, number of negative/positive coefficients, k-experiment/k-IM, differences, max abs errors (raw coefficients and dimensionless), derived `p16-p11` Pa, and absent cells count (48 possible-35=13). IM Eq3 denominator and geometric areas are set only from source (not estimated by matching observed values).

## Safeguards and failure states
- G0: nonfinite/zero/negative d,Q,Delta p or impossible duplicate conditions; sign reversal; source CSV hash; omission of a row, added phantom blank-cell record, or shifted d/p/Q are tamper/fail.
- G1: compute in SI, check kg/m3 and cm3/s conversions; analytic sign and forward/reverse identity; independent literal known-paper anchors and IM formula anchor; reject accidental units errors.
- **Result claim**: compare a published scalar coefficient table against a published untuned geometry-only formula; DO NOT claim independent confirmation of a p(tap) field. G2 is `INDETERMINATE_NO_AUDITED_NUMERIC_TAP_PROFILE`. Moving tissue G3 HOLD, creator sound G4 NO-GO.
- If no direct source table can be authoritatively transcribed or CI/integrity checks fail, stop with a RED failure trace rather than manufacturing pressure samples. Any follow-on G2 must verify actual tap positions and per-tap numeric pressures with an independent acquisition/uncertainty budget.
- Software passes ≠ physical model passes; original source reviewer needed before closing independent science gate.
