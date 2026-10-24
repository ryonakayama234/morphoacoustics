# SA-2A — EXPERIMENT (Gate A preregistration, never rewritten after run)

Question: can a single baffled-piston aperture supply mathematically consistent reactive+resistive physical load and far-field radiation for the same outward volume flow, with independent reference and power accounting, before VF-1?

H1: Bessel/Struve closed-form acoustic impedance matches independent Rayleigh double-area overlap quadrature in BOTH real and imaginary components.
H2: the on-axis/directivity field integrated over the forward hemisphere carries exactly the same acoustic power as the lip-port resistance (within quadrature tolerance). NEVER infer power from one observer pressure.
H3: load is passive Re(Zrad)>=0, finite and conjugate symmetric when extended to negative f; at zero f both R and X tend to zero, stable series avoids 0/0.
H4: at fixed genuine M0 body geometry, changing only termination to Zrad(f) alters input impedance, lip flow and observation transfer. A numeric difference does NOT establish voice naturalness, model superiority over real data, or a causal time-domain solver.

Controls:
1. Analytic special-function result against independent separation-overlap 256-node Gauss-Legendre quadrature, x=[0,0.005,0.02,0.1,0.25,0.55,0.8]; abs complex normalized impedance difference <=2e-9. Zero exactly 0.
2. Low-x series against x=.005 and .02; R relative error <=1e-3 and X relative error <=1e-3 against leading x²/2 and 8x/(3pi), provided nonzero.
3. Farfield directivity integrated by 256-node Gauss-Legendre quadrature over cos(theta) from 0..1; relative normalized radiated power-vs-port mismatch <=2e-8 at x>=.02 up to x=.8. Directivity on axis 1 within 1e-12. At x=0 compare zero power exactly. Pport>=0 for 1m³/s peak calibration.
4. Zrad normalized resistance >=-1e-12 on x grid, finite both parts, conjugate symmetry for ±frequency (negative-f definitions are derived from the complex conjugate); X>=-1e-12 for x in (0,.8].
5. For M0 body at f=[200,1000,3000] Hz filtered by ka<=0.8: check 2-port transfer identity within relative 2e-10 (independently reconstruct A,B,C,D), denominator finite, and consistent lip/load pressure and port power. Compare with actual legacy Exp009 transfer at same f, but do not claim it to be an apples-to-apples biological benchmark or replay an old output gate.
6. Geometry sensitivity for a=[.005,.010]m at 1000 and 3000 Hz: normalized impedance must follow ka and absolute Zrad must scale with rho*c/S; preserve all physical units, refuse <=0, nonfinite radius, f, c, rho and area.
7. Test exact source code head in GitHub CI and archive hash payloads. Source HEAD provenance from CI, not an unfilled manifest placeholder.

Decision:
- SA2A_ANALYTIC_REFERENCE_VERIFIED if ALL actual executed criteria 1–7 pass, with immutable exact-head CI and artifacts. This means only bounded frequency-domain baffled-piston consistency, NOT valid biological mouth/FSI or VF-1 readiness.
- SA2A_ORACLE_FAIL otherwise. No retroactive tolerance change.
- SA2B_TIME_DOMAIN_NOT_RUN unless separately implemented and reviewed. Future time-domain stable causal passive boundary + authentic body and JET flow comparisons are mandatory before MODEL_BOUNDARY_VERIFIED and researching VF-1 feedback.

Only experiment-local source/test/docs on research Draft branch. Public Core and Studio, SMC and ASMR stay untouched.
