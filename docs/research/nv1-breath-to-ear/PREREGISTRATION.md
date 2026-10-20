# NV1-EAR / Core — preregistration candidate v0 (2026-10-21)

**Status:** proposed pre-code freeze for implementation, not a declaration of measured acoustic fidelity. Any change to a test-defining constant before first code requires a dated amendment, reason, and independent acknowledgment; never silently tune parameters to listening outcomes. Tests may refute the hypothesis.

## H0/H1
H0: changing Δp or effective aperture yields only gain-scaled stochastic output within test resolution; a pure-gain surrogate explains all sonic changes. H1: an explicit physical state-conditioned closure produces reproducible non-gain spectral/time differences, alongside analytic monotonic flow differences. H1 is evidence for the selected computational closure, *not* evidence for human breath realism.

## Reference actuation and physics
Fs=48000 Hz, T=2.4 s, seed=133041, rho=1.2 kg/m³, mu=1.8e-5 Pa·s, c=343m/s, Cd=0.65, Δp_peak=120 Pa, effective area 30e-6 m². Pressure shape: raised cosine `e(t)=sin(pi*t/T)^2` for 0<=t<=T, 0 outside; aperture fixed inside the frame, with zero-drive state explicitly allowed. `Δp(t)=peak*e(t)`. These pressures/apertures are **illustrative experiment parameters, not measured human respiratory ranges**.

Quasi-steady positive-flow rule:
`Q_mean=Cd*A*sqrt(2*max(Δp,0)/rho)` [m³/s],
`U=Q_mean/A` [m/s] for A>0,
`D_eq=sqrt(4*A/pi)` [m],
`Re=rho*U*D_eq/mu`,
`P_pneumatic=Δp*Q_mean` [W].
The input pressure is the local effective constriction drop, not total lung pressure. Do not infer precise noise sound power from the mean flow equation.

## Candidate uncalibrated closure (must be recorded verbatim and evaluated against nulls)
Independent seeded unit-variance Gaussian base stream `eta[n]`. Engineering turbulence participation `g(Re)=clip((Re-1000)/2000,0,1)`; these Re thresholds are **numerical hypothesis, not a physical turbulence transition law**. Spectral shape of the stochastic stream uses an explicit dimensionless `St=f D_eq/max(U,small_speed)` with a heuristic smooth knee `St_knee=1.2` and controlled low/high frequency limits; **St_knee is NOT a validated jet-tone Strouhal measurement**. Proposed amplitude envelope: `q_ac(t)=epsilon*Q_mean(t)*g(Re(t))*noise_shaped(t; St(t))`, epsilon=0.002, units m³/s. Use overlap-add or another phase/seed-preserving, tested time-varying shaping method; no unfiltered white inlet noise, no arbitrary independent output gain based on character label. The exact filter transfer function, low/high band edges, block/hop and boundary procedure MUST be specified in code and as a dated prereg amendment **before scientific comparison**, rather than backfitted after listening; until then closure gate remains DESIGN-OPEN. At zero flow: exact q_ac=0; no direct noise when body cannot flow.

Safety budget: compute `P_ac_ideal=rho/(4*pi*c)*mean((d(q_ac)/dt)^2)` in W for ideal free-field monopole surrogate, log the ratio `P_ac_ideal/mean(P_pneumatic)`, reject or explicitly constrain if over 1%; no silent after-the-fact normalization of raw physical traces. The 1% limit is an engineering bound, **not** a validated human conversion efficiency. Exclude zero-drive from ratio division.

## Wolfram independent numerical oracles, evaluated 2026-10-21
Peak steady-plateau values (note actual raised-cosine profile is time varying, so do NOT confuse peak with time average):
| case | Q_peak L/s | U_peak m/s | Re_peak | pressure power_peak W |
|--|--:|--:|--:|--:|
| P0: 120Pa, 30mm² | 0.2757716447 | 9.192388155 | 3787.501226 | 0.03309259736 |
| P2: 240Pa, 30mm² | 0.3900000000 | 13.00000000 | 5356.335601 | 0.09360000000 |
| A2: 120Pa, 60mm² | 0.5515432893 | 9.192388155 | 5356.335601 | 0.06618519472 |
| Z0: 0Pa, 30mm² | 0 | 0 | 0 | 0 |

A heuristic St=0.2 diagnostic corresponds to f*=297.4697 Hz (P0), 420.6856 Hz (P2), 210.3428 Hz (A2); **diagnostic only, not presumed audible peak or chosen spectral-knee threshold**. Unit test tolerances: relative error <=1e-8 for pure algebraic steady oracles (float64), with tight 1e-12 absolute tolerance near zeros; actual filtered waveforms have separate recorded tolerances based on deterministic fixtures.

## Receiver/creative prereg
A: ideal L/R geometry and `p'=rho/(4*pi*r) d(q_ac(t-r/c))/dt` model Pa, derived pressure trace. B: exactly measured ~30 cm SOFA positions, center +/-27.69 degrees actual data, 48kHz stereo. B is relative/unverified pressure calibration; do not claim actual eardrum Pa, measured SPL, or matched A/B reference plane. Receiver-only changes MUST preserve exact source checksum. Do not add 1/r or propagation delay twice. Headphones blind listening and measured-SOFA provenance are separate from numerical pass.

## Explicit fail/stop
Inconsistent SI/dimensions; P0/P2/A2 not matching numeric oracles; nonzero Z0; nondeterministic fixed-seed output; NaN/Inf; uncontrolled energy; clipping/clicks; spectral change indistinguishable from NULL-GAIN -> **INCONCLUSIVE** not promoted; improperly calibrated B claim -> **FAIL**; unsupported SOFA directions or dirty/unpinned Core when claiming reproducibility -> **REFUSE**, no playable artifact. Data/model audits and user perception are independent gates.
