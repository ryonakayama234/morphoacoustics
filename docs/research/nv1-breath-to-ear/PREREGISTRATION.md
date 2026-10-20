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
Independent seeded unit-variance Gaussian base stream `eta[n]`. Engineering turbulence participation `g(Re)=clip((Re-1000)/2000,0,1)`; these Re thresholds are **numerical hypothesis, not a physical turbulence transition law**. Spectral shape of the stochastic stream uses an explicit dimensionless `St=f D_eq/max(U,small_speed)` with a heuristic smooth knee `St_knee=1.2` and controlled low/high frequency limits; **St_knee is NOT a validated jet-tone Strouhal measurement**. Proposed amplitude envelope: `q_ac(t)=epsilon*Q_mean(t)*g(Re(t))*noise_shaped(t; St(t))`, epsilon=0.002, units m³/s. Use overlap-add or another phase/seed-preserving, tested time-varying shaping method; no unfiltered white inlet noise, no arbitrary independent output gain based on character label. The filter transfer function, band edges, block/hop and boundary procedure are frozen below in **Addendum A0 (2026-10-21)**, before implementation or listening. This is a preregistered **research hypothesis**, not calibrated human turbulence. Changes require a dated amendment and independent review; never retrofit parameters to subjective results. At zero flow: exact q_ac=0; no direct noise when body cannot flow.

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

## Addendum A0 — exact first-pass time-varying noise spectral closure (2026-10-21, pre-implementation)

**Decision:** adopt a finite, reproducible, *unverified model closure* now, so W1 can implement a precise specification rather than selecting filters after listening. Equations below supersede the earlier "design-open" placeholder. The equations themselves are research assumptions; no claim that they follow uniquely from fluid mechanics.

1. **Deterministic base stream.** `N = int(round(T*Fs)) = 115200` float64 samples. `eta = numpy.random.Generator(numpy.random.PCG64(seed)).standard_normal(N)`; no per-clip gain or noise-RMS matching before source synthesis. Pin numpy/scipy versions in the implementation lock. A zero-drive scene must bypass noise-to-source and emit exactly 0; seed remains in provenance.
2. **Time envelope.** At sample n in [0,N-1], `e[n]=sin(pi*n/(N-1))**2`; `Δp[n]=Δp_peak*e[n]`, fixed positive aperture. The exact first/last envelope samples are zero. `Q[n], U[n], Re[n]` follow the equations above. `g(Re)=clip((Re-1000)/2000,0,1)` is a heuristic participation rule, NOT a physical critical-Re threshold.
3. **Short-time Fourier shaping.** Compute `scipy.signal.stft(eta, fs=48000, window='hann', nperseg=2048, noverlap=1536, nfft=2048, detrend=False, return_onesided=True, boundary='zeros', padded=True, scaling='spectrum')`; inverse uses matching `scipy.signal.istft(...,window='hann',nperseg=2048,noverlap=1536,nfft=2048,input_onesided=True,boundary=True,scaling='spectrum')`, trim to N samples. Require the fixed pair's reconstruction/no-filter self-test and no NOLA violation; freeze versions for reproducibility. Shape each complex frequency-time bin by the **real nonnegative magnitude** below; preserve its phase and the common seeded stream.
4. **Explicit spectral function.** For `f>=0` and STFT time `τ`, calculate `U(τ),D_eq(τ)` from interpolated valid physical traces, and set:
   `H(f,τ) = [f/sqrt(f²+300²)] * [1/sqrt(1+(f/9000)^8)] * [1/sqrt(1+(f*D_eq/(1.2*U))²)]`.
   Hz are used in the first two factors; f*D/U is dimensionless. For `U<=0` or insufficient finite physical input, `H=0`. DC H=0. The **300 Hz high-pass, 9 kHz high-frequency guard, St-knee 1.2 and exponent choices are explicitly heuristic** (not measurements). Frequencies >= Nyquist are inherently excluded by 48k sampling. No normalization of H to equal output RMS across scenes.
5. **Physical-source envelope.** Use filtered `xi[n]` from inverse-STFT then `q_ac[n] = 0.002*Q_mean[n]*g(Re[n])*xi[n]` in m³/s, force q_ac[0]=q_ac[N-1]=0; compute derivative in m³/s² using the same documented 48k difference stencil as receiver A and B. Do not use Q_mean itself as sound source; do not generate an additional independent white inlet source. The same exact **q_ac array and its SHA256** must feed A and B.
6. **Power and code limits.** Compute the ideal-monopole source energy budget from derivative and pressure work before presentation normalization; reject if a finite-scene limit exceeds the predeclared 1% average ratio, refuse nonfinite/unsafe values. No hidden clipping, gating after acoustics, gain-fitted pressure units or independently normalized L/R. Power efficiency and HRTF B absolute reference plane remain scientifically uncalibrated.

**Additional independent spectral-shape oracles (Wolfram Language, peak steady state, 2026-10-21):** characteristic knee `1.2*U/D_eq` = P0 1784.817904 Hz, P2 2524.113686 Hz, A2 1262.056843 Hz. Relative 5kHz/1kHz *H_St*-component response shifts compared with P0: P2 **+1.992765804 dB**, A2 **-1.827251675 dB** (common HP/LP factors cancel). These are **transfer-function calculations**, *not measured acoustic spectral shifts of rendered WAVs*. The output metric must also compare time-segment PSD of **actual generated q_ac** after RMS matching with NULL-GAIN. If noisy sample uncertainty prevents significance, record `INCONCLUSIVE`, not a forced pass.

**Change control:** if tests uncover algorithmic inconsistency or a poor audio result, record it in RESULTS. A new filter candidate needs a new numbered prereg revision and its own tests; never silently change A0 constants in-place to manufacture a positive listener judgment.
