# VF-1B2 C1-R0 — RESULTS (2026-11-02, local Python 3.11+? environment recorded separately)
**Scope**: Actual newly computed closed / spatially uniform isentropic gas–two-tissue mathematical benchmark. NOT through-flow moving-wall finite-volume C1, NOT phonation, NO acoustic Take, NO human voice. The scientific protocol HEAD **before source code** was `7a3d051d0041f79c319a4ac98d48c38ad0bd43ec`. The source code lives only on a main-based research branch; existing Core/main/Studio unchanged.

The local runner used Python standard library only; the final same-byte solver/audit/test/run Git blob SHAs were checked against the GitHub copies. Exact-head Actions verdict is a separate check; see Draft PR discussion for CI state.

## Measured, no performance engineering
Baseline: Lg=10mm, depth=10mm, half-gap=0.2mm; gamma=1.4, P0/Pext=101325 Pa; mL=mU=1e-4kg, kL=150,kU=220,kc=40N/m, dL=.02,dU=.03 N s/m; xL=3 micrometers,xU=-1 micrometer, v=0. Isentropic closed gas, initial perturbation only. Duration 6ms; RK4 dt=4/2/1 microseconds. Full per-step trace archived by runner.

| control | dt [us] | H0 [J] | H_end [J] | dissipation integrated [J] | signed closure [J] | normalized signed residual magnitude |
|---|---:|---:|---:|---:|---:|---:|
| damped | 4 | 7.174999048589086e-8 | 1.5979286564065374e-8 | 5.576975290405859e-8 | -9.510177668953208e-13 | 1.3254604780502818e-5 |
| damped | 2 | same | 1.597965606541909e-8 | 5.577028667249971e-8 | -4.7747972058699743e-14 | 6.654770507333942e-7 |
| damped | 1 | same | 1.5979664553547377e-8 | 5.577031819530411e-8 | -7.737039378463791e-15 | 1.0783331574079061e-7 |
| lossless | 1 | same | 7.174998837354702e-8 | 0 | -2.1123438399338974e-15 | 2.9440336167699913e-8 |
| zero-displacement/velocity null | 4 | 0 | 0 | 0 | 0 | 0 |

Final value convergence, |dt4-dt2|/|dt2-dt1| for two displacement coordinates: **18.8463, 18.8938**; two velocity coordinates: **15.8004, 15.8033**. This exceeds predeclared factor >=8 in all resolved coordinates. Empirical ratio is near fourth-order, but this is only one 6ms closed fixture; no claim of convergence of a spatial fluid solver.

Independent midpoint force-gradient *analytic oracle only*, b=100Pa, a=120Pa: exact F_L=0.014N, F_U=0.018N, diff=-0.004N. At N=8/16/32, each force max absolute quadrature error = 3.125e-5 / 7.8125e-6 / 1.953125e-6 N (4x improvement per refinement). The numerically computed F_L-F_U is -0.0039375 / -0.003984375 / -0.00399609375 N respectively; NOT exactly -0.004 at finite N.

Negative tests: null remains static; altered saved pressure/density detected by independent raw trace audit; negative damping refused; contact initial geometry refused; invalid dt refused. No invented F0, external periodic waveform, audio or closed-glottis source.

## Evidence identity
A reproducible generator `python experiments/057_vf1b2_c1r0_sealed/run.py OUTPUT_DIR` materializes 5 full raw JSON traces, SHA256 per file and a receipt. Local damped_1us trace SHA256: `06fd90fdebaad7a1def78a93e1b934886624afd9b8a86db1bbec84e100ddd0af`. This SHA records one execution environment, not universal bitwise deterministic output across Python/CPU implementations. Other original local trace SHA hashes are in the runner receipt and Actions archives.
Final same-byte Git blob identities: `solver.py=1976fbff1f80d686626287e298fdaa56c5ac05a0`; `audit.py=71ccfd77ee3a7c3f31e35a56ca22336a61ea794a`; `test_r0.py=96d376a0d8e59ae2bf6f18e3e22c3d1189a2fbf8`; `run.py=bfa59731f2d83c350e806466d8e3386e11a65822`.

## Interpretations and release gates
- **PASS_LIMITED**: C1-R0 closed uniform-pressure mathematical gas/tissue coupling conserves mass and has independently audited absolute/external-pressure energy in the preregistered regime. Six standardized test methods locally pass.
- **NOT IMPLEMENTED**: spatially varying moving-wall fluid pressure, momentum and nonzero through-flow, high-Re loss/separation, physiological pressure reference, body-to-tract acoustic coupling C2, sustained self-excitation, radiation and Studio audio.
- **HOLD**: full C1 numerical FV model requires its *own* A1/A2/A3 based on independently qualified reservoir equations and dissipation. Biological G2, phonation G3 and creative G4 remain NO_GO/NOT_EVALUATED.
- **No baseline pollution**: OD-3 remains fixed; no merge to main or schema/UI changes. Research-only data is not a playable character model.

## Scientific caveat
The sealed gas has equal uniform aerodynamic forces on both tissue coordinates. As predicted, it cannot supply antisymmetric aerodynamic excitation and it does not generate an outward oscillatory volume flow. Tissue displacement here is a transient initiated by a prescribed non-periodic initial condition; even an oscillation plot is NOT proof of autonomously voiced sound. This limited success should be interpreted as **a conserved coupled reference case**, not an improved voice.
