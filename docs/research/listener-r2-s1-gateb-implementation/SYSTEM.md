# SYSTEM — Gate B finite synthetic equivalent source and passive tube

Peak phasors `exp(+i ωt)`, positive `U` from entrance toward terminal at both ports; pressure Pa, volume flow m³/s, acoustic impedance Pa·s/m³, positive harmonic mean power W.

~~~mermaid
flowchart LR
  S["SOURCE_EQUIVALENT: virtual ps + absolute Zs"] --> E["CANAL_ENTRANCE: total p0,U0"]
  E --> C["Core UniformTube: rigid, linear, 1D, lossless"]
  C --> T["TERMINAL_SIDE: pL,UL"]
  T --> Z["Real absolute positive Zt"]
  E --> V["Typed complex port observation"]
  T --> V
  V --> A["Oracle, independent conservation, negative controls"]
~~~

Source `ps=p0+Zs U0`; terminal `pL=Zt UL`; propagation `[p0,U0]^T=T[pL,UL]^T`, where the **existing unmodified Core** `UniformTube` owns T. Gate B's `listener_port.py` solves the two *boundary* equations using Core's matrix coefficients, with dimensionless scaling `rs=Zs/Zc`, `rt=Zt/Zc`, `Zc=rho*c/A`:

`Dn=(a+rs*(c_matrix*Zc))*rt + b/Zc + rs*d`

`pL=ps*rt/Dn`, `UL=pL/Zt`, `p0=ps*(a*rt+b/Zc)/Dn`, `U0=ps*((c_matrix*Zc)*rt+d)/(Zc*Dn)`.

Independent diagnostic: `Dn=(rs+rt)cos(kL) + i(1+rs*rt)sin(kL)`; for real rs>=0,rt>0, `|Dn|>=min(rs+rt,1+rs*rt)>0`. Thus apparent division-by-zero is numerical representational trouble, not a real passive-circuit resonance without a solution. The *frozen* Wolfram travelling-wave oracle (NOT this diagnostic) is the primary independent path.

Two distinct ledgers: `Pdrive-Pentrance-Psource_loss=0`, `Pentrance-Pterminal=0` for this zero-loss model. This is not a physically calibrated free field: source pressure is a virtual drive, total entrance pressure is endogenous. Do not call modeled terminal pressure real tympanic pressure. H_total=pL/ps is algebraically H_drive=p0/ps times H_canal=pL/p0 when defined; neither factor proves an independent physiological cause.

Owned modules: Core physical law (`src/morphoacoustics`); research adapter and audit (`experiments/044`); possible *future separately promoted* optional `morphoacoustics_asmr` adapter; *future* version-pinned Studio Scene/Take. No changes to Core production, source body, gesture, ASMR runtime or Studio UI.