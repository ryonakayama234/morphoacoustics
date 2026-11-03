# VF-1B2 / C1-Open — EXPERIMENT v3, prospective decision protocol

**DESIGN ONLY; no C1-Open simulation has been run.** Research success = bounded moving-wall through-flow mathematics, *not human phonation or natural voice*. At A3 all chosen numerical values/thresholds and code hashes must be frozen **before executable C1 source or outcome inspection**. Candidate values below are PROPOSED engineering controls and not evidence of passing results.

## Hypotheses / falsifiers
| ID | Intervention/observable | Falsification / result ceiling |
| --- | --- | --- |
| H0 (static equilibrium) | fixed/nonuniform area, equal reservoir thermodynamic state, tissue rest | spurious pressure gradient/flow/active motion rejects numerical method |
| H1 (volume/mass) | moving wall, sealed or open ends; `Delta V_j=sum g_ji Delta x_i`, `Delta m=-integral boundary mdot` | omission of swept volume or shifted face flux must fail independent observer |
| H2 (momentum) | positive stationary area gradient and known pressure; `p dA/dz` source | constant-pressure stationary state must not accelerate; spatial pressure-gradient reference must converge |
| H3 (opposed wall work) | lower/upper force under analytic `p_g(z)=b+a z/L` | `F_L=ell L(b+a/3)`, `F_U=ell L(b+2a/3)`; uniform pressure yields `F_L=F_U`; sign/swap/duplication mutants fail |
| H4 (full energy) | open mean flow plus moving wall, evaluate `Delta H + integral(Phi_R-Phi_L + damping)dt` | omit kinetic/enthalpy flux, ambient work, or duplicate wall work => independent G1 FAIL |
| H5 (causal coupling) | same reservoirs/state, compare passive moving wall vs locked wall and vary one tissue parameter | differences must be traceable beyond solver uncertainty; null is legitimate; not a voice identity claim |
| H6 (bounded domain/refusal) | contact, reverse flow, nonpositive rho/p, nonconvergence, over-Mach | failure typed and raw retained; no success audio/Take |
| H7 (reference limit) | uniform sealed gas analytic reference vs general spatial sealed model | only reduced one-cell/uniform-pressure limit is C1-R0-compatible; do not demand equality of distributed axial dynamics |
| H8 (scope) | no imposed periodic source, steady/nonperiodic reservoirs | any vibration is **not** automatically G3 self-oscillation; quantify separately later |

## Preregistered test matrix candidate (G0/G1 numerical controls)
- Reuse C1-R0 *reference dimensions* `L_g=10 mm`, `ell=10 mm`, `h0=0.20 mm` half-gap, `gamma=1.4`, `P_ext=P_atm=101325 Pa`, 2DOF reference masses/stiffness/damping where legal; no new anatomical validity claim.
- Static analytic controls: constant-area and variable-area equilibrium, pressure gradient `p_g=b+a z/L`, equal/zero pressure difference, rigid steady subsonic isentropic nozzle, small-amplitude acoustic propagation and wall-motion manufactured reference with no contact.
- Dynamic controls: reservoir `Delta p=0,10,50 Pa` **engineering proposal only**, nonperiodic start and shut-off, changing tissue initial displacement or one material parameter at a time. Keep model low-Mach `Ma<0.1`, positive gas energy/density, verified `h>h_floor` with proposed `h_floor=0.10 mm`; do not claim high-pressure physiological validity. Disallow reverse/choked/unsupported regimes.
- Convergence: N=8/16/32 and CFL-compatible time refinements; candidate `dt<=0.4*Delta z/(c+|u|)` for initial boundary/flux verification, but an implicit integrator still requires a separate accuracy test. Do not automatically reuse 24/48/96 kHz audio times for sub-mm acoustic cell stepping. Initial observable duration sufficient to cover multiple fluid crossing times; tissue dynamics can be run for 6 ms after numerical feasibility audit. Declare run length before outcomes.
- Negative mutations: reverse sign of wall pressure force, drop moving-volume term, omit `p dA/dz`, replace total enthalpy with pU, double count outside-pressure work, tamper one interior velocity/pressure/flux, shorten trace, forge initial state, change archived source hash. Each *independent* audit must reject the falsified receipt.
- External G2 reference: PR #262 is rigid low-Re only, PR #278 sealed only, Fulcher/Scherer M5 fixed-glottis data only. Geometry/pressure tap uncertainty and rights must qualify before extrapolation to high-drive separation. If unavailable: `G2_REFERENCE_UNAVAILABLE` and no high-drive biology claim.

## Proposed mathematical gate definitions (to freeze/justify at A3, not retro-fit)
For mass `R_M=(M_N-M_0)+integral(mdot_R-mdot_L)dt`; normalize by `M_0+integral(|mdot_L|+|mdot_R|)dt`.
For total energy `R_E=(H_N-H_0)+integral(Phi_E,R-Phi_E,L + v^T D v)dt`; publish signed J and normalized `|R_E|/W_scale`, where `W_scale` is preregistered from independently computable boundary, wall and mechanical work magnitudes and a numerical cancellation floor; report **both**, never energy relative-error alone.
For momentum `R_P=Delta sum_j(q_j)+integral(face_momentum_R-face_momentum_L - geometric_pA_z)dt`; normalize by comparable physical impulse scale. Physics observer must be independent from numerical update functions.
Candidate G1 criteria: mass relative <=1e-9, energy normalized <=1e-5 *with an independently bounded absolute error* and no growth under refinement, momentum relative <=1e-6; smooth control errors decrease for spatial/time refinements; positivity/Mach/interface residual gates all pass; all declared mutants rejected. **These numerical tolerances are not yet a frozen scientific protocol**: confirm realistic roundoff floors from analytic/synthetic arithmetic *before* implementation, document any pre-code adjustment. A stringent relative threshold cannot replace independent physical reference or smooth-grid convergence.

## Decision sequence
A0 source ancestry review (#259/#278, Core main, SFI research, Studio V2 slots) → A1 independent continuous/discrete force-energy derivation and dimensional proof → A2 boundary characteristic method and conditional EOS/model selection → **A3 pre-code fixture/threshold/refusal freeze** → B fixed-wall and moving-area independent controls → C actual two-way C1 dynamics, save and audit raw states → D exact-head review, negative tests and LIMITED/REVISE/HOLD conclusion.
**Hard STOP at A1/A2/A3 if derivation, boundary conditions or independent test thresholds cannot be justified.**
**G1_PASS_MATH_ONLY** after C1 cannot imply G2 physiological validity, G3 sustainable phonation, G4 usable Studio voice. C2 mean/acoustic bridge, contact, separation, radiation, neural enhancements, SMC/ASMR and all Studio UI changes remain out of scope.

Evidence files (future implementation): `SYSTEM`, `DATA`, `EXPERIMENT`, `RESULTS`, `AUDIT` updated together per completed work step. Preserve prior failed experiments and C1-R0 original data; append corrections, do not rewrite prior verdicts.
