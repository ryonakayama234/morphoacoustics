# EXPERIMENT — D0 prospective protocol / immutable science gate

**Date:** 2026-11-04 JST. **Ordering:** freeze this protocol in its own commit **before new RP1 evaluator and tests**. Never retroactively change acceptance criteria. Label any design amendments prospectively with separate commits.

## E0 — static analytic oracle (H2)
Work in unitless **normalized** acoustic pressure/impedance (not physical Pa or human ear).
A=(ps=1,Zs=0); B=(ps=2,Zs=1), initial ZL=1, counterfactual ZL=2.
Evaluate pL=ps*ZL/(Zs+ZL). Expected observations baseline A=B=1, changed A=1 and B=4/3, gap=1/3. Use exact rational reference, no fitted parameters; result and source equation available directly in HYPOTHESES. Compare floating evaluator to exact rational with abs tolerance <=1e-14 (unitless).
Required negative/mutation: incorrectly infer uniquely Zs=0 from pL=1 baseline must be rejected as UNIDENTIFIABLE, not reported as successful prediction.

## E1 — type/operation matrix (H1)
| Evidence kind | INSPECT_METADATA | PREDICT_CHANGED_LOAD | Reproduce or distribute |
| --- | --- | --- | --- |
| MEASURED_PRESSURE_TRANSFER, declared fixed termination | inspect valid | UNIDENTIFIABLE | UNSUPPORTED / rights separately checked |
| MEASURED_PRESSURE_TRANSFER, unknown plane | inspect with missingness | UNIDENTIFIABLE | UNSUPPORTED |
| SYNTHETIC_REFERENCE_PORT, all fields coherent | inspect valid | Gate B candidate, no Gate A solve | UNSUPPORTED |
| SYNTHETIC_REFERENCE_PORT, missing Zs | INVALID if malformed record / UNIDENTIFIABLE for observed pressure-only replacement | no solve | UNSUPPORTED |
| CALIBRATED_ACOUSTIC_PORT, declared metadata | inspect only | UNSUPPORTED until separately authorized Gate C | UNSUPPORTED |
| UNQUALIFIED_OBSERVATION | inspect reason | UNIDENTIFIABLE | UNSUPPORTED |

At least 14 adversarial fixtures: unknown reference plane, mismatch between requested and actual plane, missing Zs, wrong pressure_kind, fixed-total-pressure mislabeled incident, absolute/normalized impedance confusion, nonfinite scalar, negative Zs, zero Zt, wrong phasor, wrong flow sign, unsupported 3D field, invalid union kind, distribution with unchecked rights. Every failure must carry category and field/reason; accidental accepted cases count as FAIL.

## E2 — synthetic port computation (H3; requires separately committed Gate B code)
Use existing Core UniformTube, rho=1.21kg/m³, sound speed 343m/s, ps=1+0j Pa peak, fixed absolute Zs=13834333.333333334 Pa·s/m³, Zt=27668666.666666668 Pa·s/m³.
Prospective 2x2x4 grid: A={4e-5,8e-5}m², L={0.025,0.035}m, f={750,2200,5100,7900}Hz (16 conditions). These are a **new metamorphic check set** but not an independent empirical holdout.
- New code computes full complex p0,U0,pL,UL. Independent traveling-wave oracle: Gamma=(Zt-Zc)/(Zt+Zc), q=exp(-ikL), pL/ps=q*(1+Gamma)/[(1+Zs/Zc)+(1-Zs/Zc)*Gamma*q²], plus independent wave reconstruction of p0 and U0, no production-source solver import.
- Compare each complex pressure component abs <=1e-11 Pa; volume-flow component multiplied by Zc abs <=1e-11 Pa; power <=max(1e-13W,1e-10*max(power scale,1e-12W)).
- Boundary/source/tube residuals normalized by meaningful pressure or power scales <=1e-10; power passive >= -1e-13W.
- Verify original 18-case Wolfram and B2 24-case evidence *only via independently pinned and authenticated references* if accessible, never quietly copy unmerged branch code or claim reproduction from metadata alone.

## E3 — reference-plane metamorphic invariance (H4)
For each of 16 E2 conditions, compare Core T(L) against T(L1)*T(L2) with L1=0.4L, L2=0.6L, identical area and medium. Normalize off-diagonal T by Zc: T01/Zc and T10*Zc; compare each dimensionless component abs <=1e-11. When source/load solved at both representations, end-port complex pressure and scaled volume flow differences <=1e-11 Pa. Deliberately reverse the flow sign or treat a pressure-only intermediate plane as a complete port: must be caught by contract/negative test. Reordering identical-area uniform segments is not by itself a meaningful mutation: do not use it as an adversarial result.

## Audit constraints
- Test pass counts must not be guessed. Results start NOT_RUN and must include actual CI HEAD, Python versions and failed-attempt record.
- Fix mutated \`zip\` length/truncation weakness known from PR #275: explicit strict row type, width and all-field equality before component comparisons.
- Go/no-go Gate A: E0 and E1 pass, meaningful refusal mutations exercised, docs prereg SHA visible, independent code review outstanding -> GO_LIMITED_QUALIFICATION_RESEARCH.
- Gate B may be reported as GO_LIMITED_NUMERICAL only after E2/E3 and existing Core regressions pass on a pinned HEAD plus independent review; self-generated tests alone are never human physiological validation.
- Gate C measured data, time domain, HRTF de-embedding, KU100/NF5 acoustic \`Data.IR\`, 1cm/contact, rights re-use, ASMR perception and product API NOT authorized.
