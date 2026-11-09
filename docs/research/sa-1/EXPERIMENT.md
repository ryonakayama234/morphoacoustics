# SA-1 — EXPERIMENT (Gate A preregistration; before implementation)

STATUS: PREREGISTERED_PLAN / NOT_RUN / NOT_ADOPTED
Frozen main: 6869cfec04041393eae44485ce2fc91f002114f5.
Frozen historic JET-P0: https://github.com/ryonakayama234/morphoacoustics/actions/runs/39951204385 (three conditions failed original high-band criterion). No posthoc threshold relaxation.

## Hypotheses
H1: under fixed geometry the intended total transfer P_obs/U_in equals T_U times R_obs, with independently checked units and complex phase.
H2: current fixed-tract frame_render is linear: F(U+V) = F(U)+F(V) to numerical precision at identical geometry, hop/window/edge settings; the noise-only difference otherwise cannot be interpreted as a linear separated output.
H3: observer high-band dominance can be allocated separately to source spectral power, tube flow transfer and f-proportional radiation, with additional windowing checks.
H4: current Z_L=0.05 Zc is an explicitly simplified terminal resistor; its numerical behavior is NOT proof of actual biological lip radiation.
H5: a single prepared M0 result does not establish perceptual naturalness or speaker individuality.

## Frozen experiments, in order
A. Independent oracle — lossless UniformTube with length 0.17m, cross-section 3e-4m2, rho 1.21kg/m3, c 343m/s, matched Z_L=Zc. At nonnegative frequencies [100,500,1000,2000,4000] Hz, verify Z_in=Zc and U_lips/U_in=exp(-j 2pi f L/c). Gate maximum complex relative error <1e-10 with IEEE float64 on non-singular bins.

B. Existing unchanged real Core M0 renderer — generated JET-P0 modal mean U, seeded residual V, U+V, and zero source. Keep exact common body and sound units. Gate: zero output for zero inlet; ||F(U+V)-F(U)-F(V)||2 / max(||F(U+V)||2,||F(U)||2,||F(V)||2) <1e-10. Report as failure if not.

C. Analytical gain decomposition — evaluate intended T_U, R_obs, product transfer and Zin from Exp009 matrices. Gate max relative algebraic product error <1e-10 for non-singular, nonzero-input bins. Reproduce observer frames using the exact SAME frame_render operator; do not incorrectly demand that one-shot FFT and Hann OLA have identical edge behavior.

D. Source-independent calibration — zero, then single 200, 1000, 3000 Hz flow-tone probes at fixed physical RMS, explicit waveforms and phase; compare transfer at those bins rather than inferring it from zero-valued original excitation bins. Separate source, tube, radiation gain. Test appropriate analytic port-power signs and consistency; identify any physically insufficient/out-of-scope surrogate.

E. Historical negative case reproduction — same exact JET-P0 input source code and analysis method, 4 archived cases. Compare >=2kHz output fractions to previously logged values within 0.01 percentage point; failure to reconstruct exact software chain -> BLOCKED, not silently approximated. Never call the rejected source model accepted.

F. Extension only if basics pass — repeat on independently authenticated second prepared body if available; consider physically motivated frequency-dependent radiation impedance as a DISTINCT prospective research condition, never a backdoor EQ or changed old run.

## What to deliver
At each stage, table/plot of frequency, complex U_lips/U_in, observer pressure/lip flow, input impedance, zero/source/renderer residuals, >=2kHz energy shares with full-file AND steady analyses, and exact file and source hashes. Declare the stage that explains highband output (source/tube/radiation/OLA/mixed), remaining uncertainty, and one of:

- DIAGNOSIS_VERIFIED_INTERFACE_READY — numerical oracles pass AND physically defensible port/termination model is documented; research VF-1 allowed with independent gate.
- DIAGNOSIS_VERIFIED_REPAIR_REQUIRED — origin isolated, but acoustic port/termination physical approximation needs bounded SA-2 model repair before VF-1.
- UNRESOLVED_ORACLE_FAIL — cannot isolate/verify; keep HOLD.

PASS of SA-1 does not mean high-band JET-P0 passes or that a sound is voice-like. No Studio Take transfer, no main merge, no full FSI, no arbitrary post-render filtering. Future listening is separate Studio Voice Atlas workflow. ASMR and SMC are separate.
