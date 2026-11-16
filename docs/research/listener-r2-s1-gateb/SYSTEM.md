# SYSTEM — measured circuit ports, identifiable transfers, and ownership

**Design refinement v0 | mathematical model, not a real-ear biological model.** This text does not modify the frozen Gate A equations.

## Computational object and responsibility graph
~~~mermaid
flowchart TD
  I["Synthetic source fixture: ps, Zs (absolute)"] --> P0["CANAL_ENTRANCE: p0, U0"]
  P0 <--> T["Core UniformTube: T(L,A,rho,c,f)"]
  T <--> PL["TERMINAL_SIDE: pL, UL"]
  PL --> Z["Absolute passive terminal: Zt"]
  P0 --> O["Research observation: complex ports / transfers / power"]
  PL --> O
  O --> V["Independent traveling-wave oracle and falsification"]
  G["Gate A frozen 18 cases, WL source, JSON SHA"] --> V
  V --> R["Research verdict and immutable evidence"]
  R -. "separate science + API adoption gate only" .-> PKG["morphoacoustics_asmr (metadata-only today)"]
  PKG -. "future version-pinned adapter" .-> ST["Studio Scene + immutable Take (future)"]
~~~

Core alone owns the physical UniformTube matrix, simulation invariants and physically meaningful p/U interface. Gate B is a **research-only source/boundary solve plus comparison**, not a new organ, phonation backend or ASMR renderer. The optional ASMR workspace owns catalog, verification coordination and (only after separate promotion) adapter packaging. Studio owns creator Scene / audition / immutable Take but cannot prescribe acoustic law, reference planes or numerical solver. No current runtime dependency of Core on ASMR; no new studio UI.

## Three non-interchangeable planes and conventions
1. **SOURCE_EQUIVALENT:** ps is the *open-circuit ideal drive in a synthetic Thévenin equivalent*, not a pressure microphone, free-field source or physical location.
2. **CANAL_ENTRANCE:** p0, U0 are **total** pressure and volume velocity at tube entrance.
3. **TERMINAL_SIDE:** pL, UL are the downstream physical port values on the tube side of the terminal resistance, not measured tympanic pressure.

Axial +x and positive U point entrance → terminal at BOTH tube planes; pressure Pa, volume velocity m³/s, acoustic impedance Pa·s/m³, positive-harmonic mean power W. Peak phasor convention exp(+i omega t). A is constant tube cross-sectional area and L is fixed axial length; there is NO pinna, free-field 3D position, actual eardrum, cartilage, tissue, external microphone, biological ListenerSpec or movement.

## Frozen physical constraints
Let k=2 pi f/c, Zc=rho*c/A and T=[[a,b],[c_m,d]] with a=d=cos(kL), b=i Zc sin(kL), c_m=i sin(kL)/Zc. Then:

- [p0,U0]^T = T [pL,UL]^T
- ps = p0 + Zs U0, with real absolute Zs>=0
- pL = Zt UL, with real absolute Zt>0
- UL = ps / ((a+Zs*c_m)*Zt+b+Zs*d)
- p0 = (a*Zt+b)*UL; U0=(c_m*Zt+d)*UL; pL=Zt*UL.

No separately imposed p0 or incident-wave pressure; those are endogenous. Fixed absolute Zs/Zt while changing A makes normalized ratios vary. Do NOT replace absolute Zt by R Zc. The matching and ideal-source controls are different experiments.

## Novel diagnostic decomposition (secondary, NOT a new physics law)
For nonzero ps and p0:
- H_drive = p0/ps (source-to-entrance loading)
- H_canal = pL/p0 (entrance-to-terminal response)
- H_total = pL/ps = H_drive * H_canal (algebraic decomposition, not independent causal mechanisms).
Keep complex values before amplitude/phase. Changing A can affect BOTH H_drive and H_canal, so simply attributing observed pL changes to the canal's intrinsic transfer is scientifically false. If a divisor approaches zero, report transfer undefined/unresolved rather than fabricating it; raw p/U remain primary observables. This factorization diagnoses numerical claims but does not prove what an actual external acoustic field would do.

Traveling-wave independent expression, q=exp(-ikL), GammaL=(Zt-Zc)/(Zt+Zc), rs=Zs/Zc:
H_total = q*(1+GammaL)/[(1+rs)+(1-rs)*GammaL*q^2].
For rs=1, H_total=q*Zt/(Zt+Zc). Thus **magnitude is L-independent but phase changes**. Note the source is a fixed circuit fixture, not fixed external incident field.

## Two energy ledgers, not one
At f>0 and using peak phasors:
- Pdrive = 0.5 Re(ps * conj(U0))
- Pentrance = 0.5 Re(p0 * conj(U0))
- Pterminal = 0.5 Re(pL * conj(UL))
- Ploss_source = 0.5 Zs |U0|²
- r_source = Pdrive - Pentrance - Ploss_source
- r_tube = Pentrance - Pterminal.

For the prescribed *lossless tube* and passive resistances both residuals should vanish numerically. Do not label Pterminal/Pdrive as reflection, absorption, loudness, hearing energy or ASMR sensation. |Gamma_in|² is incident/reflected wave-power ratio at the entrance under the plane-wave reference; it is not the terminal/source-drive power ratio.

## Future connection, without invented physical boundary
~~~mermaid
flowchart LR
  SRC["Future validated Core source/scene field"] -. "must register acoustic port/reference plane + incident/load conditions" .-> AD["future ASMR adapter"]
  AD -. "after separate matching/measurement gate" .-> EAR["validated receiver transfer"]
  EAR -. "after causal time-domain/HRTF checks" .-> TAKE["Studio Scene audition / immutable Take"]
~~~
No HRTF multiplication until measurement planes and open-vs-blocked ear conditions are reconciled; otherwise the canal could be double-counted. Source impedance here is a test-fixture equivalent, NOT a backward mechanical force on a Speaker organ. Contact two-body dynamics and genuinely time-varying sound remain future separate models.
