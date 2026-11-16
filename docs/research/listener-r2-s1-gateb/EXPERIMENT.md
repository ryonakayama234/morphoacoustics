# EXPERIMENT — refined pre-implementation hypotheses and falsification map

**2026-10-27 | prospective Gate B design addendum; frozen Gate A unchanged.**
Original preregistration is [Gate A EXPERIMENT at PR #158 HEAD](https://github.com/ryonakayama234/morphoacoustics/blob/489111e19ffa18b21c4c4cadba8ef19f84e11bb4/docs/research/listener-r2-s1/EXPERIMENT.md). Its 18 rows, oracle, already-declared tolerances and previously observed analytic predictions are not modified. This addendum is reviewable **before implementation**; additional secondary metrics are proposals, not retrospectively asserted preregistered outcomes.

## Scientific question and causal estimand
Under one fixed **synthetic** equivalent source (ps, absolute Zs) and fixed absolute terminal resistance Zt, does changing static uniform tube geometry (A,L) change **computed** entrance/terminal complex port values and active power exactly as predicted by passive 1D plane-wave acoustics? More specifically, can the observed terminal effect be audited as source loading (H_drive) × tube response (H_canal), rather than confused with loudness, hearing or speaker-source generation?

Paired contrasts: Delta_A pL(f,L)=pL(A2,L,f)-pL(A1,L,f) (complex Pa); Delta_L pL(f,A)=pL(A,L2,f)-pL(A,L1,f). Secondary contrasts use |pL| ratios only where denominators are nonzero and relative phase arg(pL_2 * conj(pL_1)), modulo 2pi. These are *model interventions*, not measured morphology effects. No participant or head-related transfer data.

## Hypothesis + explicit falsifier matrix
| ID | Intervention | Null / competing explanation | Observable and failure |
|---|---|---|---|
| H_B1 numerical equivalence (primary, frozen) | All 18 A×L×f with ps,Zs,Zt fixed | independent traveling-wave Wolfram outputs | p0,pL real+imag and powers must meet Gate A component tolerances; any row outside is FAIL |
| H_B2 matched-source null (primary, frozen) | A=3e-5, Zs=Zc, vary L/f | false "longer canal always weakens sound" | |pL/ps|=2/3 independent of L, phase changes; wrong gain trend is FAIL |
| H_B3 absolute-load area contrast (primary, frozen) | A=6e-5 vs 3e-5 at L=.025,f=3000, same absolute Zs,Zt | wrong model silently uses Zt=R Zc | predicted |pL| approx 0.4492470594476995 vs 0.6666666666666666 Pa; mismatch is FAIL |
| H_B4 passive power (primary, frozen) | all 18 positive harmonics | missing series source loss or spurious tube gain/loss | both r_source and r_tube must meet existing Gate A power limits, active powers nonnegative |
| H_B5 ideal-source/normalized-load controls (primary, frozen) | Zs=0; separately set Zt=R*Zc while prescribing total p0 | falsely claims these are the primary finite-source, absolute-load intervention | p0=ps in ideal source; normalized and absolute conditions explicitly unequal when appropriate |
| H_B6 transfer attribution (new diagnostic proposal) | compare H_drive,H_canal,H_total across paired A changes | mistakenly assigns entire effect to canal alone | complex identity H_total=H_drive*H_canal; retain raw p0/pL and show both factors |
| H_B7 phase reference (new diagnostic proposal) | matched-source, same f and A, change L | gain-only "receiver" with no travel phase | relative phase = -2pi*f*DeltaL/c modulo 2pi, where transfer is defined |
| H_B8 refusal/robustness (new diagnostic proposal) | invalid or well-formed unsupported inputs, zero drive, deliberate injected sign/unit mutations | silent coercion, NaN serialization, wrong error class | exact typed refusal; zero-drive powers zero and transfer ratios undefined with reason |

## Immutable primary numerical gates
Gate A specifies pL/p0 complex real/imag absolute error <=1e-11 Pa for each component in 18 frozen rows; power-oracle comparison max(1e-13 W, 1e-10*power-scale); energy residual <=max(1e-13 W,1e-10*max(Pdrive,Pterminal,1e-12 W)); passive power >=-1e-13 W; matching-null |pL/ps| 2/3 to 1e-11. Treat these as the **existing registered acceptance**; the diagnostic additions H_B6-B8 must get explicit pre-implementation reviewer agreement on tolerance/method before they become implementation gates. Do not silently promote or soften any original threshold.

## Proposed test/negative-control grouping (not executed)
1. **Oracle exactness**: load all 18 frozen Wolfram records by ordered row identity and column names (not copied magic numbers); check physical units and full complex components, not just magnitudes. Regenerating with Wolfram separately checks fixture transcription, but solver comparison MUST use immutable frozen reference.
2. **Independent invariants**: transfer matrix determinant=1; 2 power balances; Gamma_in=GammaL*exp(-2ikL); source-matched phase; limits Zs=0 and strictly positive load. Retain precision/unit-specific residuals.
3. **Mutation rejection**: inverse phasor sign; reversed U orientation; swap pressure/volume flow; wrong source sign; set p0=ps with finite Zs; recompute "fixed" Zt with area; omit source resistor loss; compare source drive power to terminal as if equal; claim 0Hz AC power.
4. **Domain/robustness**: NaN/inf, booleans treated as numbers, unit-less input, negative/zero geometry, negative resistance, well-formed reactive loads outside scope, above-fidelity frequency, zero ps, numerical overflow. Classify INVALID vs UNSUPPORTED vs NUMERICALLY_UNRESOLVED; never INFEASIBLE.
5. **Reproducibility**: Python 3.11/3.12 isolated CI, root UniformTube regressions, exact source/oracle/blob and generated-results hashes, deterministic repeat. A green CI is not an independent physical review.

## Confounds and interpretive STOP rules
- Area changes Zc, normalized source/load ratios and all port transfer factors simultaneously. Do not call it an isolated "ear canal material effect", or assert identical external incident field.
- Numeric compliance does not identify the best physiological ear geometry or realistic middle-ear load; the 8 kHz engineering scope is not validated hearing accuracy.
- Do not use user-rated ASMR pleasure, perceived wetness, spatial externalization, acoustic WAV dBFS or HRTF without their own preregistered methods.
- A mathematical benchmark based on the same theoretical law is useful software verification, NOT independent empirical validation.

## Decision levels, after separate authorization
DESIGN_READY = reviewer accepts coherent falsifiable study and scope (NOT code approval by this PR).
GATE_B_GO_LIMITED_NUMERICAL = after actual solver, unmodified primary prereg, negative controls, exact-head CI, evidence and independent audit; still not API/product adoption.
GATE_B_REVISE / FAIL / INDETERMINATE = preserve failing evidence, explain physical or numeric cause; no silent post-hoc gate shifts.
GATE_C = separately register calibration/measurement and external-field questions.
GATE_D = independent perceptual/Studio trial and API versioning later.
