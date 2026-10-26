# EL-R1 SYSTEM — research-only passive listener acoustic port
**Frozen Gate A: 2026-10-22; parent #152. Model ID: el-r1.passive.uniform.v0.**

## Causal placement
~~~mermaid
flowchart LR
 S["Calibrated experimental total entrance pressure (not a speaker simulation)"] --> P["CANAL_ENTRANCE acoustic p/U port"]
 L["Independent listener geometry and passive load"] --> T["Core UniformTube ABCD law"]
 P --> T
 T --> Q["TERMINAL_SIDE acoustic p/U port"]
 P --> O["Observation + provenance"]
 Q --> O
 O --> C["Wolfram traveling-wave oracle; audit"]
~~~

There is *no* gesture-to-waveform inference, speaker physique, neural bypass, contact mechanics, HRTF, Studio code or public creature schema change.

## Definitions
- +x points from entrance x=0 to terminal x=L; positive U flows in +x direction at both planes.
- Complex quantities are **peak phasors** with e^(+iωt), not RMS; f>=0 Hz, k=2πf/c.
- p: pressure [Pa]; U: volume velocity [m³/s]; acoustic impedance Z=p/U [Pa·s/m³].
- UniformTube physical characteristic impedance Zc=ρ c/A, with positive density, sound speed, area.
- State [p0,U0]^T = [[cos(kL),iZc sin(kL)],[i sin(kL)/Zc,cos(kL)]] [pL,UL]^T.
- Terminal load Zt=R Zc, with **real R>0**, pL=Zt UL. This is a **surrogate passive terminal resistance**, not an empirical eardrum model.
- Drive fixes **total** entrance pressure p0 (phasor); U0 is *solved*, not specified independently.
- H=pL/p0=1/(cos(kL)+i sin(kL)/R); for p0=0, H is defined as system transfer independent of stimulus.
- Input impedance Zin=(a Zt+b)/(c Zt+d); input reflection Γ0=(Zin-Zc)/(Zin+Zc), with reference to entrance plane.
- Mean active acoustic power P=(1/2) Re(p conjugate(U)) [W]. For this lossless tube P0=PL>=0; reflecting load does not mean amplification of delivered power.

## Independent traveling-wave oracle
At the *terminal* ΓL=(R-1)/(R+1). With q=exp(-ikL), Γ0=ΓL q² and H=q(1+ΓL)/(1+ΓL q²), independent of the Core matrix algorithm. The positive-resistance load guarantees |ΓL|<1. In matched case R=1, Γ0=0 and H=q. Algebraic oracle and the Core matrix must agree; determinant 1 alone is insufficient.

## Explicit limits
Initially no wall loss, tympanic membrane motion, cochlea, wave diffraction, nonlinear tissue, contact, binaural interaction, pinna, near-field source. Geometry and f guardrails in DATA are **engineering research limits**, not calibrated anatomical validity. In particular the 1D model is not evidence of <1cm acoustic fidelity. Nothing is promoted to runtime type hierarchy before a later adoption gate.
