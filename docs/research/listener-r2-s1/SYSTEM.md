# SYSTEM — EL-R2-S1 finite-source acoustic boundary

**Gate A frozen: 2026-10-22, before Python solver implementation; issue #157.**

~~~mermaid
flowchart LR
 PS["Acoustic Thevenin drive: p_s [Pa]"] --> ZS["Series resistance Z_s [Pa s/m³]"]
 ZS --> EP["CANAL_ENTRANCE p_0,U_0"]
 BODY["Synthetic rigid 1D listener tube: L,A,rho,c"] --> C["Existing Core UniformTube ABCD"]
 EP --> C
 C --> TP["TERMINAL_SIDE p_L,U_L"]
 TP --> ZT["Fixed absolute resistance Z_t"]
 EP --> OBS["Complex observations: port power, reflectance, p/U"]
 TP --> OBS
 OBS --> ORACLE["Independent Wolfram traveling-wave oracle"]
~~~

## Core physical conventions
- Axial +x entrance toward terminal; +U flows from entrance toward terminal at both observation planes. `p` Pa; `U` m³/s; `Z` Pa·s/m³. Peak phasors `exp(+i omega t)`. Only positive harmonic f>0 Hz in primary power grid; the f→0 analytical limit is distinct from DC work rate.
- Core acoustic law `[p0,U0]^T=T [pL,UL]^T`, `T=[[a,b],[c,d]]`, `a=d=cos(kL)`, `b=i Zc sin(kL)`, `c=i sin(kL)/Zc`, `Zc=rho*c_air/A`.
- Terminal `pL=Zt UL` with **fixed absolute, real** Zt>0; source `ps=p0+Zs U0` with **fixed absolute, real** Zs>=0 (zero is ideal source limit). This is a **series acoustic source impedance**, not a receiving device response curve.
- Unique response: `UL=ps/[(a+Zs*c)Zt+b+Zs*d]`, `pL=Zt UL`, `p0=(a Zt+b)UL`, `U0=(c Zt+d)UL`.
- Derived `Zin=p0/U0=(a Zt+b)/(c Zt+d)`; `p0=ps Zin/(Zs+Zin)`. Do not accidentally constrain p0=ps for finite Zs.
- Source power = `0.5 Re(ps conj(U0))` W; entrance power = `0.5 Re(p0 conj(U0))`; terminal power = `0.5 Re(pL conj(UL))`; source resistor dissipation = `0.5 Zs |U0|²` (all at **positive** f).
- Conservation `Psource = Pentrance + Pdiss_source`, `Pentrance=Pterminal` in lossless tube. A load ratio R=Zt/Zc changes with A here because Zt is fixed; this is intentionally **not** EL-R1's normalized-load experiment.

## Independent representation
Define `q=exp(-ikL)`, `GammaL=(Zt-Zc)/(Zt+Zc)`, `sc=Zs/Zc`, so
`pL/ps = q(1+GammaL) / [(1+sc)+(1-sc)GammaL q²]`.
This is traveling-wave scattering independently of Core's matrix multiplication. Source matching `Zs=Zc` removes source-side re-reflection, yielding `|pL|=|ps| Zt/(Zt+Zc)` independent of **L**, but still with phase delay. For frozen baseline Zt=2Zc, this equals **2/3 Pa**. An intentional **null**; a model which reports monotonic length-dependent amplitude at this source-matched reference is wrong.

## Exclusions
This source is *not* a simulated vibrating body, an acoustic free field, measured speaker or universal microphone. No pinna, nonlinearity, viscothermal loss, eardrum mechanics, measured source impedance, HRTF filter concatenation, contact, phonation, perceptual ASMR or Studio package activation.
