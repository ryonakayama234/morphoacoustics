# EXPERIMENT — EL-R2-S1 preregistered controls

**2026-10-22 JST, registered after feasibility calculation and BEFORE implementation.** Issue #157. Gate A is registration, not evidence that Gate B passed.

## Research hypothesis
A fixed complex source pressure with finite passive source impedance and a **fixed absolute** terminal resistance makes the canal entrance pressure endogenous to the tube impedance, so source/body/load interventions can be separated. The source is a synthetic equivalent circuit; no real exterior acoustic field has been predicted.

## Independent Wolfram feasibility already done (not blinded)
Symbolic Core ABCD vs scattering `pL/ps` difference=0 and `det(T)=1`. For real source and load resistances `Psource-Pentrance-Zs|U0|²/2=0`, and a lossless canal `Pentrance=Pterminal`. The 18 complex fixtures were numerically evaluated before this registration; stored as separate Wolfram frozen oracle and disclosed here. They are **not** data validating a human ear.

## Primary matrix
A={3e-5,6e-5}m², L={.02,.025,.03}m, f={1000,3000,7000}Hz; rho=1.21,c_air=343,ps=1+0iPa; Zs=13834333.333333334, Zt=27668666.666666668 Pa·s/m³ fixed absolutely across all 18.

## Predeclared Gate B acceptance
1. **Independent path numerical equivalence:** Core `UniformTube` matrix source/load solver versus 18 Wolfram traveling-wave fixed JSON records: every complex pL,p0 component within abs 1e-11 Pa; source/terminal/dissipated mean powers within max(1e-13 W,1e-10 * power-scale).
2. **Physical energy:** for all primary rows f>0, Psource - Pterminal - Psource_loss and Pentrance-Pterminal <= max(1e-13 W, 1e-10 * max(Psource,Pterminal,1e-12 W)); all passive powers >= -1e-13 W. Reflections |Gamma0|<1 for positive Zt.
3. **Null fixture:** at A=3e-5 and Zs=Zc (fixed), any L in registered set yields `|pL/ps|=2/3` to 1e-11; pL phase changes. The 1 Pa source is *not* a 1 Pa total entrance pressure source; p0 remains unknown and varies with L.
4. **Geometry contrast:** at A=6e-5 with same absolute Zs,Zt, for f=3000 Hz, terminal amplitude varies across lengths and differs from baseline reference; for L=.025m expected |pL| approximately **0.4492470594476995** vs reference **0.6666666666666666**.
5. **Ideal-source control:** setting Zs=0 makes p0=ps and reproduces EL-R1 total-pressure formula *algebraically* for a matched declared terminal ratio `R=Zt/Zc`, but does not import the unmerged EL-R1 experiment module.
6. **Normalized-load control:** at fixed L, imposed total p0, changing area with `Zt=R Zc` must have identical pL/p0; when **fixed absolute** Zt is used R changes and can produce a non-null response. These are separately labeled interventions and not conflated.
7. **Negative/mutation cases:** flipped phasor sign; swapped p/U; incorrect source sign; mistaken use p0=ps; wrongly recalculating absolute Zt with area; omission of source resistor dissipation; 0Hz AC power; huge ints/nonfinite/unsupported reactive or negative parameters; exact typed error categories.
8. **CI:** independent GitHub Actions on Python 3.11/3.12 + existing Core tube regression, reproducible Wolfram oracle data regeneration verifier. WolframScript regeneration is distinct from CI's frozen-oracle comparison.
9. **No misleading inference:** any 'same physical external sound field'/'predicted eardrum pressure'/'ASMR effect' is a hard scientific reject, regardless of passing numerical tests.

## Gate C/D prohibited
Do not connect to SOFA/HRTF or Studio, add physical ear tissue, time-domain WAV, free-field calibration or product API as a side effect of Gate B. A new gate with source calibration and reference plane must be independently registered/reviewed.
