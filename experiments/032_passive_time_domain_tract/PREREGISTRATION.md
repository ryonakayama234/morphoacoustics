# Experiment 032 / SFI-2 — pre-implementation research registration

**Frozen before code, 2026-10-10. Status: EXPERIMENT PROPOSAL (not production), separate from the unmerged #79.** Tracks [#80](https://github.com/ryonakayama234/morphoacoustics/issues/80).

## One scientific intervention and question

Build an **experiment-local, fixed-geometry, passive, causal time-domain 1D tract** with independent inlet/outlet flow/pressure state. Does it reproduce uniform-tube propagation delay, acoustic input impedance, standing-wave eigenmodes and area-junction reflection predicted by the existing independent frequency-domain [UniformTube/SegmentedTube](../../src/morphoacoustics/acoustics/segmented_tube.py) oracle?

**Not yet connected to glottal valve:** inject **prescribed test volume flow** U_in(t). Real source feedback, time-varying articulators, human voice/naturalness and morphology transfer are explicitly out of scope. This PR will NOT modify src/, contracts/, Studio, LF voice, or existing experiments.

## Frozen geometry and physics (not calibrated human anatomy)

- Reference: 10 rigid sections × 0.017 m, each area 3.0e-4 m²; L=0.17 m; rho=1.21 kg/m³; c=343 m/s. Compare one case with one middle section's area halved (same total length).
- Fixed 1D planar, linear, isentropic acoustics with perfectly rigid walls; no wall loss/viscosity/3D, no moving geometries.
- Acoustic *cell compliance* C_i=A_i Δx_i/(rho c²), face *inertance* M_j=rho (Δx_left/(2 A_left)+Δx_right/(2 A_right)) for interior faces; inlet/outlet faces have respective half-cell inertance. Units C [m³/Pa], M [Pa s²/m³]. Pressure p_i at centers, volume velocity U_j at faces. Subdivide each original section uniformly before stepping, preserving physical sectional geometry.
- Evolution: C_i dp_i/dt=U_i-U_{i+1}; M_j dU_j/dt=p_{j-1}-p_j (interior), and M_N dU_N/dt=p_{N-1}-R_L U_N. Prescribed U_0(t) is the excitation. Reconstruct physical inlet port pressure `p_in=p_0+M_0 dU_0/dt`. Outlet termination `p_out=R_L U_N` (R_L>=0), including **pressure release** R_L=0 and **matched** R_L=rho*c/A_out. A resistive matched termination is a toy anechoic load, not a physically complete lip-radiation model.
- Numerics: **fully implicit midpoint rule**, coupled pressure and velocity, positive tridiagonal system solved by Thomas elimination; port quantities at midpoint; avoid explicit numerical instability and retain an exact discrete energy budget.
- Energy `E=Σ C_i p_i²/2 + Σ M_j U_j²/2` including the prescribed inlet-half-face inertance. For constant geometry and impedance termination: `E_{n+1}-E_n=dt [ p_in,mid U_in,mid -R_L U_N,mid² ]`. Check per-step balance to a preregistered `1e-9` relative error on accumulated absolute injected work (plus `1e-14 J` absolute floor) and no nonpassive source-free energy increase beyond floating precision. This discrete identity for a 2-cell example was independently verified by Wolfram symbolic algebra (residual exactly 0).
- Any solver-specific state stays *experiment-local*. The geometry is read from the existing `Tract1DGeometry`/TubeSection format where importable. Do NOT alter existing frequency-domain `SegmentedTube` or its oracle.

## Frozen Wolfram ideal uniform-tube oracles

For the original `exp(+i ω t)` convention, `Zc=rho*c/A`, `k=ω/c`,
`Z_in=Zc*(Z_L+i*Zc*tan(k L))/(Zc+i*Z_L*tan(k L))`.
- `Zc=1,383,433.3333333333 Pa·s/m³` for A=3e-4.
- `L/c=0.4956268221574344 ms`; `2L/c=0.9912536443148688 ms = 47.5801749271 samples at 48 kHz`.
- With pressure release and closed inlet, ideal odd quarter-wave modes `f1=504.4117647059 Hz`, `f2=1513.2352941176 Hz`, `f3=2522.0588235294 Hz`. Compare discretized solver natural modes after spatial/time discretization error, not real vowel formants.
- Matched `ZL=Zc` gives `Zin=Zc`, with no physical outlet reflection.
- Junction A1→A2: pressure reflection `r=(A1-A2)/(A1+A2)`; A2=A1/2 gives r=+1/3, A2=A1 gives r=0, and `r²+4 A1 A2/(A1+A2)²=1`. Requires appropriate impedance-normalized energy measure, not raw pressure squared.

## Planned tests / gated claims

**G0: symbolic/numeric correctness.** Wolfram source in `wolfram/independent_oracle.wl`, JSON exact reference. Check 2-cell discrete energy identity, input impedance characteristic for matching termination, round-trip time, uniform modes and junction reflection. No assertion of numerical waveform passing before running.

**G1: causal acoustics.** Test a smooth compactly supported volume-flow pulse; no pre-response; estimate first return from outlet in pressure-release case relative to matched case (clear as a negative-going reflection at ~2L/c after input pulse) with **predeclared** tolerance ±0.20 ms (accounts for discrete dispersion and finite pulse width). Compare independent frequency oracle at selected moderate non-resonant frequencies, e.g. 250, 500, 1000 Hz for matched boundary; require `|Z_est-Z_expected|/Zc ≤ 0.08` for each after numerical steady-state. Exclude ideal poles from finite-duration impedance estimates, and explicitly record phase convention.

**G2: numerical stability/passivity.** Source-free energy monotonic for RL≥0; max per-step normalized energy residual ≤1e-9 with 1e-14 J absolute floor. Spatial refinement at section subdivisions=2/4/8 and fixed 48 kHz: report error convergence for selected pressure-release modal frequencies; prefer monotonic errors for first three modes. Check one-segment constriction, A1=A2 negative control, extremal positive area ratios; reject A<=0 and negative loads as INVALID rather than silently clip.

**G3: causal source coupling UNSUPPORTED.** This PR does NOT call Exp031 glottal valve with feedback, use glottal area or report source–filter coupling as established by Experiment 032 alone. That is a following independently preregistered experiment after G0–G2 review.

**G4: listening, real vowels, physiological calibration, naturalness NOT TESTED.** No WAV required; complex impedance, pressure/flow, energy traces are the metrics.

## CI and process

Create one experiment-specific GitHub Actions workflow with explicit unittest run, reproducible diagnostic CLI invocation, test gate checking and artifact upload. Unmerged PR #79 has a new workflow specifically for Exp031 and shall remain separate; **green generic CI must not be called Exp031 local-test CI**.

This registration must be committed FIRST, before solver code or oracle implementation, in a new `research/sfi2-*` branch from main. Keep Draft PR. No merge until independent scientific/code review. Numerical tolerances are research-fixture gates, not safety/production or perceptual acceptance thresholds.

Sources: existing code `src/morphoacoustics/acoustics/{uniform_tube,segmented_tube}.py`; Titze 2008 https://pmc.ncbi.nlm.nih.gov/articles/PMC2811547/ ; Wolfram https://reference.wolfram.com/language/PDEModels/tutorial/Acoustics/AcousticsTimeDomain .
