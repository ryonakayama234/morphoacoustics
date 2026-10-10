# Experiment 031 / SFI-1 — Frozen pre-implementation research plan

**Date:** 2026-10-10. **Status:** exploratory preregistration within a Draft PR; NOT a completed scientific validation or production promotion. **Issue:** #78.

## Scientific question / intervention

Given the identical prescribed glottal *area* trajectory, identical fixed subglottal pressure, inertance, glottal resistance and timestep, does returning a passive supraglottal chamber pressure to the glottal flow equation alter the *upstream glottal volume velocity* U(t)? Compare C0 open loop vs C1 coupled, and vary ONLY passive outlet resistance to distinguish real upstream flow effects from downstream filtering.

The current LF source is a **prescribed flow pulse**; it is NOT used as a glottal area nor assumed equivalent. No prescribed source waveform is filtered here. The chamber is an intentionally **lumped passive acoustic toy load**, NOT a tract geometry, 1D wave propagation, tract input impedance, vowel, self-oscillating vocal fold or 3D FSI. No WAV, perceptual, naturalness or biological-calibration claims.

## Physical variables, equations and dimensions

- U(t) [m^3/s]: glottal volume flow; positive means subglottal to supraglottal.
- p(t) [Pa]: absolute deviation of supraglottal chamber pressure from atmosphere; negative values are allowed.
- A(t) [m^2]: **prescribed** glottal aperture; not a simulated tissue motion.
- Psub [Pa] fixed lung-side driving pressure.
- I [Pa s^2/m^3], Rg, Rout [Pa s/m^3], C [m^3/Pa], rho [kg/m^3], Cd [dimensionless].

For A>0, `b(A) = rho/(2 Cd^2 A^2)`, and
`I dU/dt = Psub - Rg U - b(A) U |U| - feedback*p`;
`C dp/dt = U - p/Rout`.
Feedback=0 in C0; feedback=1 in C1. Both share identical prescribed input controls and an evolving chamber pressure. Only C1 forms a power-consistent closed loop. C0 is a deliberately nonreciprocal negative control: NO global passivity claim for C0.

For A=0: set U=0 as an ideal instantaneous valve closure; the loss of previous kinetic energy I*U_before^2/2 is explicitly recorded as contact/projection loss. The chamber continues passive outlet discharge. Ignore tissue contact physics; no leakage. Reject negative / nonfinite coefficients, negative A, and invalid dt.

## Frozen exploratory fixture (not anthropometric calibration)

- dt=1/48000 s (48 kHz), duration=0.24 s; initial U=p=0.
- rho=1.21 kg/m^3, Cd=0.70, I=1200 Pa s^2/m^3, Rg=1.5e6 Pa s/m^3.
- Chamber C=3.5e-10 m^3/Pa; outlet low/high Rout=2.0e6 / 8.0e6 Pa s/m^3.
- Psub=800 Pa; f0=100 Hz; open quotient=0.65; Amax=3.0e-5 m^2. For phase=(t*f0) mod 1, A=Amax sin(pi phase/OQ)^2 if 0<phase<OQ else 0.
- Conditions: C0-low, C0-high, C1-low, C1-high, all **same controls and solver**. The only intervention C0↔C1 is the feedback flag; low↔high changes only Rout.
- Record every-sample U(t), p(t), A(t), Psub, and per-step energy-budget values in CSV; JSON summary and provenance; include sampled output only when command invoked.

## Numerical method and independent oracle

Backward Euler and simultaneous pressure elimination:
`alpha = C/(C+dt/Rout)`,
`beta = dt/(C+dt/Rout)`,
`p_next = alpha*p_old + beta*U_next`.
For open aperture solve monotonic equation `b U_next |U_next| + a U_next = rhs`
where `a = I/dt + Rg + feedback*beta` and
`rhs = Psub + (I/dt)*U_old - feedback*alpha*p_old`.
Stable root: `U_next = sign(rhs)*2*abs(rhs)/(a+sqrt(a*a+4*b*abs(rhs)))`, with a>0. Both signs/zero handled. Must avoid overflow for tiny nonzero apertures by using a numerically stable equivalent if needed. No implicit fitted parameters or waveform normalization.

Wolfram independent analytical checks to commit as a readable `.wl` script plus a machine-readable reference JSON:
- For constant open aperture and C1, steady `p=Rout U` and `b U |U|+(Rg+Rout)U=Psub`; compare numerical trajectory after sufficient settle; negative drive uses odd symmetry.
- For b→0: `U=Psub/(Rg+Rout)`; for no chamber load (Rout→0), `p→0`; I=0 only in oracle steady/limit checks (code may reject I=0).
- For open steps, with `E=(I U²+C p²)/2`, exact BE identity:
  `E_next-E_old = dt*(Psub*U_next - Rg*U_next² - b*abs(U_next)^3 - p_next²/Rout) - I*(U_next-U_old)^2/2 - C*(p_next-p_old)^2/2`.
  This conservation equation applies to **C1 only**; for C0 an extra `+p_next U_next` power mismatch is expected.
- For exact closure, `U_next=0`, and the same chamber balance plus explicit `I U_old²/2` valve contact/projection loss.
- Basic independent frequency sanity check `Z=R+i omega I` → 1/sqrt(1+q²), phase=-atan(q).

## Prespecified gates / failure signals

- **G0** independent Wolfram algebraic references, steady roots, sign symmetry, finite values, energy residual scale ≤1e-9 of max(1e-12, cumulative absolute injected energy) (with absolute residual tolerance also checked), stable root and timestep convergence on at least two refinements. Distinguish energy dissipation (physics) from backward Euler dissipation (numerical).
- **G1** C0 low/high U must agree to tight floating-point tolerance, while C1 low/high U must differ by >1% relative RMS in *upstream U*, with identical A and Psub. C1 must also differ from C0. If the threshold fails, report FAIL, do not quietly retune and report success.
- **G2** No claim of real tract load, biologically grounded vowel, source spectrum quality, or speech. The time-domain tract backend is a separate future gate and remains **UNSUPPORTED**.
- **G3** No naturalness claim or listening outcome; separate, independently reviewed research required.

## Change scope

This Draft PR starts with this preregistration **before implementation code**. Subsequent commits add only files in `experiments/031_glottal_load_feedback/` (plus optional experiments index); no `src/`, `contracts/`, existing experiments, production backend, studio, main branch, or other PRs. PR stays Draft; merges require independent scientific + code review. The user explicitly approved trying the experiment.

References:
- Titze (2008), https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/
- Current Core `src/morphoacoustics/acoustics/segmented_tube.py` is *frequency-domain* only.
