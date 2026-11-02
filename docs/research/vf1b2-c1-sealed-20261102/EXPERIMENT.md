# VF-1B2 C1-R0 — preregistered hypotheses, fixed controls and thresholds
FROZEN research-local protocol before source code/outputs. It is not the full C1 A3 freeze; it qualifies ONLY the sealed spatially uniform isentropic control. Any changed threshold after results requires a separately dated amendment and a newly withheld run.

## Hypotheses / falsifiers
H0 physically sealed: true mass M_g constant and p_abs=P0(V0/V)^gamma. Null mismatch and trace tampering MUST fail.
H1 wall power: with pressure uniform, F_L=F_U=g(p_abs-Pext); exact gas power -p_abs dV/dt, external pressure Pext dV/dt, passive mechanics and total H balance. With damping=0, H(t) constant to numerical error; with damping>0, H(t)+int Dv²dt constant.
H2 nonperiodic control: no external periodic A, F0 or prescribed oscillation. Initial tissue displacement only; no inflow/outflow. Zero initial displacement/velocity and P0=Pext produces identically static state.
H3 convergence: RK4 steps dt=4e-6, 2e-6, 1e-6 seconds for 0.006 seconds, fixed parameters, compare final x and v componentwise in declared SI. Finer difference <= coarser difference/8 for every component whose coarse error > separately defined absolute numerical floor (1e-14 m, 1e-9 m/s); otherwise report too-small-to-estimate, not asserted 4th order.
H4 force gradient analytic separate from sealed solver: p_g=b+a*z/L with b=100 Pa, a=120 Pa. Midpoint quadrature N=8,16,32; exact difference -ell L a/3; for N doubled, maximum individual force error decreases approximately by 4 (allow ratio >=3 if error exceeds 1e-14 N; otherwise considered analytically resolved). A sign reversal of a must reverse force difference.
H5 negative evidence: no sustained self-phonation, no acoustic output, no human speech or pressure-gradient-driven oscillation is claimed, even if oscillations occur as a transient from the initial perturbation.

## Frozen numeric fixture — illustrative math, not physiologic calibration
L_g=.010 m; ell=.010 m; h0=.00020 m; gamma=1.4; P0=Pext=101325 Pa (abs); rho0=1.2 kg/m3.
m_L=m_U=0.0001 kg; k_L=150 N/m; k_U=220 N/m; k_c=40 N/m. initial x_L=+3e-6 m, x_U=-1e-6 m, v=[0,0].
damped run d_L=.02,d_U=.03 N*s/m; lossless run d=[0,0]; null x=v=[0,0] with damping.
duration 0.006 seconds. All intermediate RK4 states must keep positive gap at z=0,L; no smoothing/clipping.

## Engineering gates (independent observer)
- Physical trace p-law maximum abs relative error <= 2e-12 (recomputed from x,V by separate observer). Gas mass maximum abs drift <= 1e-16 kg (direct calculation from rho V, not inferred from stored mass).
- Passive/no-damping: |H_end-H_init| <= 3e-10 J AND normalized ratio <= 5e-4 against E_scale=max(|H_init|, 1e-8 J), for finest dt. With damping: |H_end+Loss-H_init| <= 3e-10 J absolute AND <=5e-4 against same scale for finest dt, independent trapezoidal loss observer.
- The null trajectory maximum |x| <=1e-14m, |v|<=1e-9m/s; exact source p=P0. Numerically force/value mutations in one raw trace must fail tolerance without re-running solver. Corrupt finite-volume claim: model intentionally has NO spatial flow field or inlet/outlet power.
- If energy floors not justified by observed floating-point scales OR chosen step grid fails convergence, mark NUMERICALLY_UNRESOLVED rather than changing prereg thresholds. Software/test PASS alone does not establish physiological source G2 or self-oscillation G3.

## Work sequence and STOP
A0: exact source/lineage inventory and analytical derivation, documented here before code. A1/A2 for full C1 remain pending independent EOS, reservoir and separation model review. Then implement separate sealed-control solver + separately coded observer + tests; run actual fixture/negative conditions; publish RESULTS and verification. All artifacts must preserve failures and exact code SHA. If no pressure/energy closure, stop, do not add postprocessing. Never merge this research to production based on math-only success.

## Post-hoc reviewer-required adversarial controls (NOT ORIGINAL PREREG THRESHOLDS)
Added after original experiment and independent Codex findings, without changing physical equations or frozen original conservation thresholds: (1) one interior signed velocity negated (energy/dissipation squares unchanged) must fail a distinct position–velocity check, (2) NaN timestamps must be refused, (3) nonfinite/negative fixture state must be refused. Independent velocity reconstruction uses fourth-order five-point finite differences; a *remedial engineering witness* threshold `5e-7*(dt/4e-6)^4 + 1e-10 m/s` was calibrated to guard the currently observed grid. This tolerance was **not prospectively established** and must NOT be cited as an independently held-out numerical proof. New future dynamics require a separately frozen derivative residual tolerance and independent validation.

## Third reviewer post-hoc correction (not prospective physics gate)
Independent review found that a stationary copy of the non-equilibrium initial state passed earlier energy+position/velocity checks despite the force law predicting strong nonzero acceleration. Added a separately derived mechanical equation residual at each tick, including signed pressure force/spring/damping, using a fourth-order velocity derivative and a *post-hoc engineering tolerance* `0.025*(dt/4e-6)^4+1e-6 m/s²`. This is not a frozen prospective numerical cutoff and cannot be represented as external biological validation. Added an explicitly frozen-all-state counterexample test. A separate failure-preservation test deliberately raises an audit exception and verifies raw JSON, SHA and failure receipt survive. Original prereg physical hypotheses/thresholds unchanged.
