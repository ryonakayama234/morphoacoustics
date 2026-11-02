# D1 — Prospective 24-case independent transfer audit (2026-11-02 JST)

**Status at this commit: EXPERIMENT REGISTERED BEFORE THIS ADDENDUM'S SOLVER/ORACLE EXECUTION; NO NEW NUMERICAL RESULTS YET.**

## Antecedents and noninterference
- The [original immutable 18-point Gate A](https://github.com/ryonakayama234/morphoacoustics/pull/158) and independent WolframScript oracle are unchanged, including all thresholds; [Gate B implementation PR #233](https://github.com/ryonakayama234/morphoacoustics/pull/233) already passes initial 18 and is deliberately reused, not rewritten.
- [Design PR #228](https://github.com/ryonakayama234/morphoacoustics/pull/228) remains independent. This follow-up B2 is **stacked on #233 research head** to measure incremental changes, not merged into main.
- Governing [Issue #274](https://github.com/ryonakayama234/morphoacoustics/issues/274). Only numerical synthetic tube certification; human ear, nearfield, HRTF, subjective ASMR and public ASMR package / Studio adoption expressly excluded.

## Computational measurands
At SOURCE_EQUIVALENT ps,Zs; CANAL_ENTRANCE p0,U0; TERMINAL_SIDE pL,UL, using peak phasors exp(+iωt), +U towards termination, SI Pa/m³s/Pa·s·m^-3/W. Fundamental complex p/U and transfer H_t=pL/ps, source loading H_drive=p0/ps, tube H_canal=pL/p0; mean positive-harmonic power P=.5 Re(p conj(U)), Psource resistor=.5 Zs |U0|². Power residuals: Psource−Pentrance−Psource_resistor and Pentrance−Pterminal; no measured signals.

## Prospective B2 grid — 24 cases exactly
- **A ∈ {4e-5, 8e-5} m² × L ∈ {0.015, 0.035, 0.045} m × f ∈ {750, 2200, 5100, 7900} Hz** (lexicographic A,L,f row order).
- Air density rho=1.21 kg/m³, sound speed 343 m/s, source open-circuit ps=1+0i Pa, Zs=13834333.333333334 Pa·s/m³, terminal Zt=27668666.666666668 Pa·s/m³. These *absolute* resistances stay fixed when geometry changes.
- All 24 fixtures are different from the original 18. 7900 Hz is a numerical test point **not evidence of a 7900-Hz human-ear model**.
- This is a *prospective, nonblinded* synthetic condition challenge, not measured-data cross-validation. The physics and inputs are public, so it cannot establish real-world/generalization validity.

## Independent computational reference
Use the traveling-wave/scattering representation independently of Core's ABCD matrix implementation:
Zc=rho*c/A, r=Zs/Zc, Gamma=(Zt−Zc)/(Zt+Zc), q=exp(−i2πfL/c).
pL=ps q(1+Gamma)/[(1+r)+(1−r)Gamma q²].
Then UL=pL/Zt; p0=pL[cos(kL)+i Zc sin(kL)/Zt];
U0=pL[i sin(kL)/Zc+cos(kL)/Zt].
These last two are exact physical endpoint relationships; use independently evaluated complex exponentials and independently calculated source/power balances. The frozen B2 numeric oracle will be generated **only after this D1 commit** and stored with provenance and hash; do not claim independent laboratory reference or unseen ground truth. No Wolfram execution is promised for B2 (18-case Gate A retains its Wolfram oracle).

## Numerical acceptance and falsification (predeclared)
1. Row count 24, exact sorted grid and original source/load identity. Every real and imaginary component of p0,pL absolute difference ≤1e−11 Pa; every U0,UL component scaled by Zc absolute difference ≤1e−11 Pa. Compare source, entrance, terminal and source-resistor mean powers by tolerance max(1e−13 W, 1e−10 × max(|P_ref|, |P_candidate|, 1e−12 W)).
2. For each case, source boundary |ps−p0−Zs U0| ≤1e−11 Pa, termination |pL−Zt UL| ≤1e−11 Pa, both residual balances ≤ max(1e−13 W,1e−10 max(Psource,Pterminal,1e−12 W)), passivity P≥−1e−13 W.
3. Independent transfer factorization: for every nonzero input, compare Htotal=pL/ps, Hdrive=p0/ps, Hcanal=pL/p0 against independently recomputed ratios ≤1e−11; not only the identity Htotal=Hdrive×Hcanal.
4. Complex source scaling and phase equivariance: scale ps by 0.5, 2, and exp(i0.63) at representative rows; ports scale by factor, active powers scale |factor|², passive structure (Zc, gamma) remains identical. Tolerance 1e−11 Pa for pressures; Zc-scaled flow ≤1e−11 Pa; power with formula in item 1.
5. Mutations of oracle pressure/flow/power and of source/load units/identity must be detected. Nonfinite oracle scalar must fail closed; no NaN bypass. Every new reference must have independently pinned SHA256 and explicit schema.
6. CI Python 3.11/3.12, unchanged original 18-case tests plus new tests and Core UniformTube regression. GitHub Actions completed with verified run, exact head SHA. CI failure => STOP, not a declaration of numerical readiness.

## Decision gate
PASS may yield **FROZEN_NUMERICAL_REFERENCE / LIMITED_SYNTHETIC_ONLY** after evidence audit and independent code review. Scientific independent human/physical review remains distinct. Any measured-data credibility, ear morphology, nonlinear, viscothermal, contact, HRTF, timbre, perceptual ASMR, public API, or Studio adoption requires separate gates. No merge.