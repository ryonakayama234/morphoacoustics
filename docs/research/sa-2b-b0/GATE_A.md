# SA-2B / B0 — Gate A pre-registration, BEFORE any implementation or execution
Date: 2026-10-24 JST. Status: PREREGISTERED, NOT_RUN, NOT_ADOPTED.
Issue https://github.com/ryonakayama234/morphoacoustics/issues/173
Design https://github.com/ryonakayama234/morphoacoustics/issues/173#issuecomment-6381685120
Pinned Core main commit: 6869cfec04041393eae44485ce2fc91f002114f5
SA-2A independent baffled-piston reference commit: 6eca7a250e30de8d758087dad83d5f02a1301f38; run https://github.com/ryonakayama234/morphoacoustics/actions/runs/40062355337, not merged. The B0 test may independently evaluate the SAME analytic formula using research-only scipy, but must not claim SA-2A full farfield power identity for this simplified circuit.

## Physical system, intended Character Creator semantics
Create an experiment-local **fixed-geometry**, small-signal **lip radiation one-port**. It consumes incoming sound pressure-wave amplitude (Pa) and previous stored inertial volume-flow state (m³/s), and returns outgoing/reflected wave (Pa), lip excess pressure (Pa), acoustic volume flow (m³/s), stored energy (J) and dissipated energy (J). Not an arbitrary audio high-pass/EQ, source, jet turbulence generator, or listener waveform. Morphology area/air properties determine all impedance parameters, not editable "brightness" knobs. Average breath flow + acoustic fluctuations must be treated separately. Real moving jaw/lips would require time-varying-M mechanical power; DO NOT animate geometry during B0.

The physical approximation is a UNIFORM baffled circular piston, not an unflanged pipe, actual face, beak, microphone observation, or mean-flow aerodynamic nozzle. S=pi*a² [m²], a=sqrt(S/pi) [m], rho [kg/m³], c [m/s], Zc=rho*c/S [Pa*s/m³]. Inertance M=8*rho*a/(3*pi*S) [Pa*s²/m³], tau=3*pi*a/(16*c) [s], resistance R=M/tau [Pa*s/m³]. All must be finite positive.
Circuit: U = q+p/R, M*dq/dt=p; Z(s)=M*s/(1+tau*s), where q=U_L [m³/s]. It is a **parallel** M and R circuit, physically small-signal. Continuous stored energy E=0.5*M*q² [J]; instantaneous power identity p*U=dE/dt+p²/R [W]. Re[Z(s)]>=0 at Re(s)>=0 and pole -1/tau. DC Z(0)=0. This approximates the low-ka SA-2A exact impedance R_norm~(ka)²/2, X_norm~8ka/(3*pi), not a full-band fit. As frequency goes high, Z_B0 -> R which is NOT the correct full SA-2A asymptote. Restrict physically validated SA-2A comparisons to ka<=0.8.

## Frozen discrete scattering law and time convention
Real sample interval h=1/48000 sec (compare 96000Hz). Exterior characteristic impedance Zc. Incoming and outgoing lip-port pressure waves a_n,b_n [Pa] obey
   a_n=(p_mid+Zc*U_mid)/2 ; b_n=(p_mid-Zc*U_mid)/2 = p_mid-a_n.
One sample a_n is a drive centered over step [n*h,(n+1)*h]. Given only current a_n and previous q_n, implicit midpoint computes
   K=1+Zc/R+Zc*h/(2*M),
   p_mid=(2*a_n-Zc*q_n)/K,
   q_next=q_n+h*p_mid/M,
   q_mid=(q_n+q_next)/2,
   U_mid=q_mid+p_mid/R,
   b_n=p_mid-a_n.
NO lookahead or hidden future samples.
Every step must independently satisfy, including nonzero initial q:
   h*(a_n²-b_n²)/Zc = h*p_mid*U_mid = E_next-E_n + h*p_mid²/R.
Energy of outgoing waves may rise transiently due to discharge of stored initial E. Positive dissipated energy is a radiation POWER PROXY, not a verified directional farfield. No observer/wav output at B0.

The zero-incident SCATTERING pole is
   lambda=(1+Zc/R-Zc*h/(2*M))/(1+Zc/R+Zc*h/(2*M)).
It differs from the U-prescribed impedance Tustin pole (1-h/(2*tau))/(1+h/(2*tau)). Distinguish tests.
Digital complex reference Gamma_d=(Z_B0(s)-Zc)/(Z_B0(s)+Zc), with s=(2/h)*(1-z^-1)/(1+z^-1); independent simulation and analytic comparisons of magnitude AND phase. Analog reference Gamma_a uses s=i*2*pi*f. Bilinear warping is an APPROXIMATION, not numerical instability.

## Authentic input provenance and frozen cases
Genuine prepared CC-A2 M0 /a/ body from experiments/042_sv1_sustained_vowel/run.py SV-1 strict validated context, **not** hardcoded geometry; expect section_count=16, lips area 0.000804247719318987 m² (a=0.016m), rho=1.21,c=343, fs=48000. Archive sections' immutable area/length bytes as SHA256. Calibration-only radii 5mm,10mm explicitly hypothetical, not extra adopted bodies.

Excitation is externally prescribed INCIDENT ACOUSTIC WAVE, NOT vocal folds:
- 0 Pa for 0.20s from zero state; exactly zero result.
- impulse: one incident 1 Pa sample then 0, length 0.20s.
- seeded noise: RNG seed 48017 Gaussian at 1Pa RMS (0.20s), and alternating pulses.
- sinusoidal incident 1Pa peak at 200,1000,2600Hz for 0.20s, use 256-sample transient exclusion, assess complex transfer via least squares / lock-in against analytic bilinear Gamma.
- zero input with q0=1e-6 m³/s to test stored-energy release and decay.
- 48k/96k comparison at 1000Hz.
- anatomy sensitivity: same incident amplitude and separately same incident energy per step across different areas; do not confuse waveform changes caused by different Zc with identical incident power.
- SA-2A exact-vs-circuit model-comparison x=ka [0.02,0.1,0.29309,0.55,0.8], two separate budgets.
- M0 3000Hz: ka≈0.879 >0.8 therefore OUT_OF_DOMAIN; record this as exclusion, NOT a pass. No original JET-P0 source replay, no LF voice render, no synthesized WAV; those are B3.

## Frozen numerical and negative gates (no ex-post tolerance edits)
1. Strict genuine M0 preflight: 16 tube sections, outlet area relative error <=1e-12 vs frozen M0. S,rho,c,fs finite positive, real incident wave and initial q finite. Nonphysical zeros, NaN, infinities, negative area or R/M-like coefficient values MUST throw (negative resistance not externally configurable).
2. Model reduction vs exact SA-2A analytic Bessel J1 and Struve H1: x grid above, max COMPLEX relative impedance difference <=0.055; max R-only relative difference <=0.11; record BOTH independently, report x grid. These are deliberately looser physical model errors and NOT implementation tolerances.
3. Continuous analytic positive-real: Re Z(s)>=-1e-10 Pa*s/m³ on s=sigma+i*omega, sigma=(0,10,1000)/sec, frequencies=(0,200,1000,2600)Hz; time-domain pole -1/tau negative and both R/M positive; exact DC 0.
4. Per-step energy identity absolute residual <=1e-9*max(|h*(a²-b²)/Zc|, |dE|, |dissipated|, 1e-20 J). Cumulative signed residual <=1e-9*max(sum_n |h*(a²-b²)/Zc|, 1e-20 J). Resistance dissipation>=-1e-20 J and E>=0 in all cases. With zero incident and nonzero q0, E monotonically decreases. With zero incident q0=0, all fields/energies exactly zero.
5. Scattering zero-input pole |lambda|<1 and direct simulation q_next/q0 relative error <=1e-12. Any nonzero forced-U Tustin pole explicitly identified as DIFFERENT from scattering lambda.
6. Complex digital Gamma at frequencies 200,1000,2600Hz: independent state-space analytic vs bilinear Gamma absolute diff <=1e-11; steady sinusoid from 0.20s simulation, discarding 256 startup samples, complex estimate absolute difference <=0.002. At 1kHz, analog-vs-digital Gamma difference at 96k <=0.35 of difference at 48k; both finite.
7. Physical dimensional scaling identities M/Zc=8*a/(3*pi*c), R=M/tau, positive real radiation resistance. Calibration geometry changes parameters in physically derived way. No arbitrary independent filter/noise controls.
8. Archive all arrays and SHA256 digests and manifest with exact GitHub run HEAD/ref in a separate CI receipt. Never claim SHA from embedded placeholder; test actual job / branch SHA. Preserve failed runs and negative results. Existing Core public API, Studio, SMC, ASMR and original JET-P0 highband gates unchanged.

Decision ONLY after actual source CI: SA2B_BOUNDARY_VERIFIED_DUCT_PENDING if all checks PASS, or SA2B_HOLD otherwise. Even with pass: NO coupled time-domain tract B1/B2, no glottal acoustic feedback, no VF-1 self-excitation, no measured radiation field, no voice naturalness, no public adoption / main merge.

References: Verified SA-2A experiment / results: https://github.com/ryonakayama234/morphoacoustics/blob/research/sa2a-baffled-piston-20261024/docs/research/sa-2/RESULTS_20261024.md ; positive-real/circuit source https://pubmed.ncbi.nlm.nih.gov/18986901/ ; discrete dissipative port-Hamiltonian https://link.springer.com/article/10.1007/s00498-023-00376-z ; source-filter physics https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/.
