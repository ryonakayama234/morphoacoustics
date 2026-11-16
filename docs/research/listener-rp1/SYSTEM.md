# SYSTEM — research-only receiver-port architecture

**Phase D0 | physical boundary frozen before code.**

## Causal decomposition

\`\`\`text
Independent body/source/motor or synthetic drive
      | external acoustic boundary: p, U and/or calibrated equivalent ps, Zs
      v
[RP1 EvidenceClassifier + QualificationEngine] --- insufficiency ---> typed refusal
      |
      | identifiability + port contract satisfied
      v
[RP1 ConditionalCoupler research-only] -> existing Core UniformTube matrix
      |
      v
typed p0,U0,pL,UL and source/entrance/terminal power ledger
      |
      v
audited research evidence — NOT product ASMR API or Studio
\`\`\`

No dependence from Core to RP1; no dependence from Studio to research scripts. Do not modify Core source solver, body, gestures, SMC, source models or existing performance contracts.

## Bounded physics
- Ideal, stationary, small-signal, 1D rigid lossless uniform tube with one mode and a single passive port; no 3D pinna, real tympanic mechanics, cartilage conduction, near-contact physics, psychoacoustics or time-domain signal synthesis.
- Complex **peak** phasor exp(+iωt); positive volume flow U [m³/s] from entrance to terminal; p [Pa]; acoustic impedances Z [Pa·s/m³]; f>0 for mean-power tests.
- Existing Core UniformTube supplies T=[[a,b],[c,d]], [p0,U0]^T=T[pL,UL]^T, Zc=rho*c/A.
- For synthetic source and terminal boundary: ps=p0+Zs U0; pL=Zt UL, with real Zs>=0 and Zt>0. Thus UL=ps/((a+Zs*c)*Zt+b+Zs*d). "c" in this denominator is T[1,0], **not sound speed**.
- Real dissipative Zs belongs in source power loss; lossless canal has Pentrance=Pterminal, Psource=Pentrance+Zs|U0|²/2, P=Re(p conj(U))/2.
- A fixed **total** entrance p0 is not fixed **incident** pressure, and neither is generally a free-field sound field.

## Identifiability
A scalar transfer measurement at one load identifies its **observed channel response at that load**, not a unique equivalent source impedance or pressure–flow state at a changed load. Even a known reference plane cannot create absent impedance/velocity information. A measured HRTF is never auto-cast to a calibrated source port. A measured HRTF may already include an ear-canal response: no bare HRTF multiplication or de-embedding by assumption.

## Scope ladder
Gate A: typed evidence and identifiability/refusal.
Gate B: synthetic, boundary-consistent 1D solver using existing Core physical primitives; independent oracle, split-tube reference-plane invariance, powers and mutation.
Gate C: separate authorization and freeze for newly calibrated source/termination measurements and independent held-out counterfactual loads.
Gate D: separate review for versioned optional ASMR API and Studio.

**Stop:** any missing or inconsistent required measurement plane, acoustic boundary, timing, channel calibration, rights status (when redistribution is attempted), or unsatisfied numerical guards. Refusal must preserve original evidence and reason; no silent fallback. Physical generality beyond supported assumptions is UNSUPPORTED, not automatically INVALID.
